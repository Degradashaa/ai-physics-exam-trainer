from typing import List
from app.schemas import Question, Evaluation, CriterionScore


def rubric_text(question: Question) -> str:
    lines = []
    for c in question.criteria:
        kw = ", ".join(c.keywords) if c.keywords else "—"
        lines.append(f"{c.id} | {c.text} | max {c.weight} | ключевые слова: {kw}")
    return "\n".join(lines)


def grade_from_percent(p: float) -> str:
    if p >= 0.85:
        return "5 (отлично)"
    if p >= 0.70:
        return "4 (хорошо)"
    if p >= 0.50:
        return "3 (удовлетворительно)"
    return "2 (неудовлетворительно)"


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def build_evaluation(question: Question, raw: dict) -> Evaluation:
    scores_map = {c["id"]: c for c in raw.get("criteria", [])}
    criterion_scores: List[CriterionScore] = []
    total = 0.0
    max_total = 0.0

    for c in question.criteria:
        max_total += c.weight
        item = scores_map.get(c.id, {})
        raw_score = _safe_float(item.get("score", 0))
        score = max(0.0, min(c.weight, raw_score))
        total += score
        criterion_scores.append(
            CriterionScore(
                id=c.id,
                score=score,
                max_score=c.weight,
                comment=item.get("comment", "") or "",
            )
        )

    percent = (total / max_total) if max_total else 0.0
    return Evaluation(
        total_score=round(total, 2),
        max_score=round(max_total, 2),
        grade=grade_from_percent(percent),
        criteria=criterion_scores,
        missing=list(raw.get("missing", []) or []),
        errors=list(raw.get("errors", []) or []),
        summary=raw.get("summary", "") or "",
        verifier={},  # заполнит checker_service
    )