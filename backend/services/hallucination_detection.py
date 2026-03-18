import math
import re
from functools import lru_cache

from langchain_community.embeddings import HuggingFaceEmbeddings

WARNING_MESSAGE = "Answer may be only partially grounded in the retrieved documents"


def _split_sentences(text: str) -> list[str]:
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
        if sentence.strip()
    ]
    return sentences or ([text.strip()] if text.strip() else [])


@lru_cache(maxsize=1)
def _get_grounding_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def _cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def detect_hallucination(answer: str, context_chunks: list[str]) -> dict:
    answer_sentences = _split_sentences(answer)
    cleaned_chunks = [chunk.strip() for chunk in context_chunks if chunk and chunk.strip()]

    if not answer_sentences or not cleaned_chunks:
        return {
            "is_grounded": False,
            "grounding_score": 0.0,
            "sentence_scores": [],
            "confidence": "❌ Not grounded",
            "warning": WARNING_MESSAGE,
        }

    embeddings = _get_grounding_embeddings()
    sentence_embeddings = embeddings.embed_documents(answer_sentences)
    chunk_embeddings = embeddings.embed_documents(cleaned_chunks)

    sentence_scores = []
    for sentence, sentence_embedding in zip(answer_sentences, sentence_embeddings):
        best_similarity = max(
            (
                _cosine_similarity(sentence_embedding, chunk_embedding)
                for chunk_embedding in chunk_embeddings
            ),
            default=0.0,
        )
        sentence_scores.append(
            {
                "sentence": sentence,
                "score": round(best_similarity, 4),
            }
        )

    grounding_score = round(
        sum(item["score"] for item in sentence_scores) / len(sentence_scores),
        4,
    )

    if grounding_score >= 0.75:
        confidence = "✅ Fully grounded"
    elif grounding_score >= 0.6:
        confidence = "⚠️ Partially grounded"
    else:
        confidence = "❌ Not grounded"

    return {
        "is_grounded": grounding_score >= 0.6,
        "grounding_score": grounding_score,
        "sentence_scores": sentence_scores,
        "confidence": confidence,
        "warning": WARNING_MESSAGE if grounding_score < 0.6 else "",
    }
