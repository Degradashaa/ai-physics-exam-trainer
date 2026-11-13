import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas import Question, Criterion
from app.rubric import build_evaluation, grade_from_percent


def _q():
    return Question(
        id="T1", topic="t", text="q", reference="r",
        criteria=[
            Criterion(id="C1", text="t1", weight=2),
            Criterion(id="C2", text="t2", weight=2),
        ],
    )


def test_full_score():
    ev = build_evaluation(_q(), {
        "criteria": [
            {"id": "C1", "score": 2, "comment": ""},
            {"id": "C2", "score": 2, "comment": ""},
        ],
        "missing": [], "errors": [], "summary": "",
    })
    assert ev.total_score == 4
    assert ev.grade.startswith("5")


def test_clamp_score():
    ev = build_evaluation(_q(), {
        "criteria": [{"id": "C1", "score": 99, "comment": ""}],
        "missing": [], "errors": [], "summary": "",
    })
    assert ev.criteria[0].score == 2


def test_missing_criterion_defaults_to_zero():
    ev = build_evaluation(_q(), {
        "criteria": [{"id": "C1", "score": 2, "comment": ""}],
        "missing": [], "errors": [], "summary": "",
    })
    assert ev.criteria[1].score == 0


def test_grade_thresholds():
    assert grade_from_percent(0.9).startswith("5")
    assert grade_from_percent(0.75).startswith("4")
    assert grade_from_percent(0.6).startswith("3")
    assert grade_from_percent(0.1).startswith("2")