"""
Детерминированная проверка поверх LLM.

Идея: LLM может похвалить ответ, в котором нет ни формулы, ни нужного
понятия. Верификатор обнуляет балл критерия, если в ответе обучающегося
не найдено ни одного ключевого слова этого критерия — независимо от того,
что решила модель. Это и есть защита от галлюцинаций на уровне логики.
"""

import re
from typing import Dict, List, Tuple
from app.schemas import Question, Criterion


def _normalize(text: str) -> str:
    """Нижний регистр, убираем пробелы."""
    text = text.lower()
    text = text.replace("ё", "е")
    text = re.sub(r"\s+", "", text)
    return text


def has_keyword(criterion: Criterion, answer: str) -> bool:
    """True, если в ответе есть хотя бы одно ключевое слово критерия.
    Если у критерия keywords пуст — не ограничиваем (True)."""
    if not criterion.keywords:
        return True
    ans = _normalize(answer)
    for kw in criterion.keywords:
        if _normalize(kw) in ans:
            return True
    return False


def apply_caps(
    question: Question,
    raw: dict,
    answer: str,
) -> Tuple[dict, dict]:
    """
    Модифицирует raw['criteria']: обнуляет балл критериев, где LLM поставила
    > 0, но в ответе нет ключевых слов. Возвращает (raw, report).

    report = {
        "applied": True,
        "caps": [{"id", "llm_score", "capped_to", "reason"}, ...],
        "n_caps": int,
        "checked": int,
    }
    """
    scores_map = {c["id"]: c for c in raw.get("criteria", [])}
    caps: List[Dict] = []
    checked = 0

    for c in question.criteria:
        item = scores_map.get(c.id)
        if item is None:
            continue
        checked += 1
        try:
            score = float(item.get("score", 0))
        except (TypeError, ValueError):
            score = 0.0

        if score > 0 and not has_keyword(c, answer):
            caps.append({
                "id": c.id,
                "llm_score": score,
                "capped_to": 0.0,
                "reason": f"в ответе нет ключевых слов: {', '.join(c.keywords)}",
            })
            item["score"] = 0.0
            prev = item.get("comment") or ""
            item["comment"] = (prev + " [verifier: балл обнулён — нет ключевых слов]").strip()

    report = {
        "applied": True,
        "caps": caps,
        "n_caps": len(caps),
        "checked": checked,
    }
    return raw, report