import re
from typing import List
from app.schemas import Question

STOPWORDS = {
    "и", "в", "на", "с", "по", "что", "как", "это", "для", "из", "к", "у", "о",
    "не", "но", "или", "при", "же", "ли", "бы", "то", "чем", "так", "все",
}


def _tokenize(text: str) -> set:
    words = re.findall(r"[a-zA-Zа-яА-Я0-9]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def search(questions: List[Question], query: str, top_k: int = 20) -> List[Question]:
    if not query.strip():
        return questions[:top_k]
    q_tokens = _tokenize(query)
    scored = []
    for q in questions:
        tokens = _tokenize(q.text + " " + q.topic)
        overlap = len(q_tokens & tokens)
        if overlap > 0:
            scored.append((overlap, q))
    scored.sort(key=lambda x: -x[0])
    return [q for _, q in scored[:top_k]]