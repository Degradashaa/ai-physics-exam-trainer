from dataclasses import dataclass, field
from typing import List


@dataclass
class Criterion:
    id: str
    text: str
    weight: float
    keywords: List[str] = field(default_factory=list)


@dataclass
class Question:
    id: str
    topic: str
    text: str
    reference: str
    criteria: List[Criterion]


@dataclass
class CriterionScore:
    id: str
    score: float
    max_score: float
    comment: str


@dataclass
class Evaluation:
    total_score: float
    max_score: float
    grade: str
    criteria: List[CriterionScore]
    missing: List[str]
    errors: List[str]
    summary: str
    verifier: dict = field(default_factory=dict)