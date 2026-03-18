from services.hallucination_detection import extract_keywords


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def score_context_relevance(question: str, grouped_chunks: dict[str, list[dict]]) -> float:
    query_keywords = extract_keywords(question)
    if not query_keywords:
        return 0.0

    per_document_scores = []
    for chunks in grouped_chunks.values():
        chunk_keywords = extract_keywords(" ".join(chunk["content"] for chunk in chunks))
        overlap = len(query_keywords & chunk_keywords)
        per_document_scores.append(_safe_ratio(overlap, len(query_keywords)))

    if not per_document_scores:
        return 0.0

    return round(sum(per_document_scores) / len(per_document_scores), 4)


def score_completeness(question: str, answer: str, grouped_chunks: dict[str, list[dict]]) -> float:
    query_keywords = extract_keywords(question)
    answer_keywords = extract_keywords(answer)

    answer_coverage = _safe_ratio(len(query_keywords & answer_keywords), len(query_keywords))

    supporting_documents = 0
    for chunks in grouped_chunks.values():
        document_keywords = extract_keywords(" ".join(chunk["content"] for chunk in chunks))
        if query_keywords & document_keywords:
            supporting_documents += 1

    document_coverage = _safe_ratio(supporting_documents, max(len(grouped_chunks), 1))
    return round((0.65 * answer_coverage) + (0.35 * document_coverage), 4)


def evaluate_answer(
    answer: str,
    context: dict[str, list[dict]],
    question: str,
    grounding_score: float | None = None,
) -> dict:
    return {
        "relevance_score": score_context_relevance(question, context),
        "grounding_score": round(grounding_score or 0.0, 4),
        "completeness_score": score_completeness(question, answer, context),
    }


def build_metrics(
    question: str,
    answer: str,
    grouped_chunks: dict[str, list[dict]],
    grounding_score: float,
) -> dict[str, float]:
    evaluation = evaluate_answer(
        answer=answer,
        context=grouped_chunks,
        question=question,
        grounding_score=grounding_score,
    )
    return {
        "relevance": evaluation["relevance_score"],
        "grounding": evaluation["grounding_score"],
        "completeness": evaluation["completeness_score"],
    }
