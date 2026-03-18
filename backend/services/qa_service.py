import os
import re

import google.generativeai as genai

from services.hallucination_detection import detect_hallucination
from services.prompt_templates import build_strict_rag_prompt


MODEL_NAME = "gemini-2.5-flash"
OUTSIDE_DOCUMENTS_MESSAGE = "This question is outside the provided documents."


class QAService:
    def __init__(self, embedding_service):
        api_key = os.getenv("GOOGLE_API_KEY")
        self.model = None

        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(MODEL_NAME)

        self.embedding_service = embedding_service
        self.per_document_k = 4
        self.max_context_chars = 3500
        self.max_chunk_chars = 650
        self.max_chunks_per_document = 4

    def answer_question(self, vector_store, question: str) -> dict:
        print(f"RAG request started for question: {question}")

        if not self.model:
            return self._fallback_response("GOOGLE_API_KEY is not configured.")

        try:
            retrieval_query = self._rewrite_query(question)
            print(f"Retrieval query: {retrieval_query}")

            retrieved_chunks = self.embedding_service.retrieve_balanced_chunks(
                vector_store,
                retrieval_query,
                per_document_k=self.per_document_k,
            )
            if not retrieved_chunks:
                return self._fallback_response("No document evidence was retrieved.")

            grouped_chunks = self._group_chunks_by_document(retrieved_chunks)
            context, used_chunks = self._build_context(grouped_chunks)
            if not context or not used_chunks:
                return self._fallback_response("No usable context could be built.")

            print("Final context:")
            print(context)

            prompt = build_strict_rag_prompt(context=context, question=question)
            answer_text = self._generate_answer(prompt)
            if not answer_text:
                return self._fallback_response("Gemini request failed.", used_chunks)

            answer_body = self._extract_answer_body(answer_text)
            if not answer_body:
                return self._fallback_response("Empty answer from Gemini.", used_chunks)

            grounding = detect_hallucination(
                answer_body,
                [chunk["content"] for chunk in used_chunks],
            )
            print(
                f"Grounding score: {grounding['grounding_score']:.4f} | "
                f"confidence: {grounding['confidence']}"
            )

            return {
                "answer": answer_body,
                "sources": self._build_sources(used_chunks),
                "confidence": grounding["confidence"],
                "warning": grounding["warning"],
                "metrics": {
                    "grounding": grounding["grounding_score"],
                },
            }
        except Exception as exc:
            error_message = str(exc)
            print(f"Error in answer_question: {error_message}")
            return self._fallback_response(f"Generation failed: {error_message}")

    def _rewrite_query(self, question: str) -> str:
        lowered = question.lower()

        if "self-rag" in lowered:
            return "SELF-RAG retrieval generation critique self reflection explanation"

        if "graphrag" in lowered:
            return "GraphRAG knowledge graph community summary global reasoning"

        if "rag" in lowered:
            return "retrieval augmented generation explanation definition"

        return question

    def _generate_answer(self, prompt: str) -> str | None:
        print("Gemini generation started")
        try:
            response = self.model.generate_content(prompt)
            return (response.text or "").strip()
        except Exception as exc:
            print(f"Gemini error: {exc}")
            return None

    def _group_chunks_by_document(self, retrieved_chunks: list[dict]) -> dict[str, list[dict]]:
        grouped: dict[str, list[dict]] = {}
        for chunk in retrieved_chunks:
            document_id = str(chunk["document_id"])
            grouped.setdefault(document_id, []).append(chunk)
        return grouped

    def _build_context(self, grouped_chunks: dict[str, list[dict]]) -> tuple[str, list[dict]]:
        sections: list[str] = []
        used_chunks: list[dict] = []
        current_length = 0

        for document_id, chunks in grouped_chunks.items():
            section_lines = [f"### Document {document_id}"]
            section_chunks: list[dict] = []

            for chunk in chunks[: self.max_chunks_per_document]:
                cleaned_text = self._clean_chunk(chunk.get("content", ""))
                excerpt = self._build_excerpt(cleaned_text, self.max_chunk_chars)
                if not excerpt:
                    continue

                projected_lines = section_lines + [excerpt]
                projected_section = "\n\n".join(projected_lines)
                projected_total = current_length + len(projected_section) + (2 if sections else 0)
                if sections and projected_total > self.max_context_chars:
                    break
                if not sections and not section_chunks and len(projected_section) > self.max_context_chars:
                    section_lines.append(excerpt)
                    section_chunks.append(chunk)
                    break

                section_lines.append(excerpt)
                section_chunks.append(chunk)

            if len(section_lines) == 1:
                continue

            section = "\n\n".join(section_lines)
            projected_total = current_length + len(section) + (2 if sections else 0)
            if sections and projected_total > self.max_context_chars:
                break

            sections.append(section)
            used_chunks.extend(section_chunks)
            current_length = projected_total

        return "\n\n".join(sections), used_chunks

    def _clean_chunk(self, text: str) -> str:
        cleaned = " ".join(text.split())
        lowered = cleaned.lower()

        if not cleaned:
            return ""
        if "appendix" in lowered or "references" in lowered or "bibliography" in lowered:
            return ""
        if lowered.startswith("preprint") or "all rights reserved" in lowered:
            return ""

        return cleaned

    def _build_excerpt(self, text: str, max_chars: int) -> str:
        sentences = self._split_sentences(text)
        if not sentences:
            return ""

        excerpt_sentences = []
        current_length = 0

        for sentence in sentences:
            projected = current_length + len(sentence) + (1 if excerpt_sentences else 0)
            if excerpt_sentences and projected > max_chars:
                break
            excerpt_sentences.append(sentence)
            current_length = projected

        if excerpt_sentences:
            return " ".join(excerpt_sentences)

        return sentences[0]

    def _extract_answer_body(self, answer_text: str) -> str:
        cleaned = answer_text.strip()
        cleaned = re.sub(r"^Answer:\s*", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"^Final Answer:\s*", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.split(r"\n\s*Sources:\s*", cleaned, maxsplit=1, flags=re.IGNORECASE)[0].strip()
        return cleaned

    def _build_sources(self, used_chunks: list[dict]) -> list[str]:
        sources = []
        seen = set()

        for chunk in used_chunks:
            source = f"Document {chunk['document_id']}, Chunk {chunk['chunk_id']}"
            if source in seen:
                continue
            seen.add(source)
            sources.append(source)

        return sources

    def _fallback_response(self, warning: str = "", used_chunks: list[dict] | None = None) -> dict:
        return {
            "answer": OUTSIDE_DOCUMENTS_MESSAGE,
            "sources": self._build_sources(used_chunks or []),
            "confidence": "❌ Not grounded",
            "warning": warning or "",
            "metrics": {
                "grounding": 0.0,
            },
        }

    def _split_sentences(self, text: str) -> list[str]:
        return [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
            if sentence.strip()
        ]
