from typing import List, Optional
from app import config, checker_service
from app.schemas import Question, Evaluation


class ExamSession:
    def __init__(self, question: Question):
        self.question = question
        self.answer_parts: List[str] = []
        self.followups: List[str] = []
        self.final: Optional[Evaluation] = None

    def submit_main(self, text: str) -> None:
        self.answer_parts.append(text.strip())

    def add_followup_qa(self, q: str, a: str) -> None:
        self.followups.append(q)
        self.answer_parts.append(f"[уточнение] {q}\n{a.strip()}")

    def evaluate(self) -> Evaluation:
        full = "\n\n".join(self.answer_parts)
        self.final = checker_service.check_answer(self.question, full)
        return self.final

    def next_followup(self) -> Optional[str]:
        if len(self.followups) >= config.MAX_FOLLOWUPS:
            return None
        if not self.answer_parts:
            return None
        return checker_service.generate_followup(
            self.question, "\n\n".join(self.answer_parts)
        ) or None