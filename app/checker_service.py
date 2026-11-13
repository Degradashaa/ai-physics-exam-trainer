import logging
from app import config, groq_client, prompts, rubric, verifier
from app.schemas import Question, Evaluation

log = logging.getLogger(__name__)


def check_answer(question: Question, student_answer: str) -> Evaluation:
    user = prompts.USER_CHECKER_TEMPLATE.format(
        question=question.text,
        reference=question.reference,
        rubric_text=rubric.rubric_text(question),
        student_answer=student_answer,
    )
    raw = groq_client.chat_json(prompts.SYSTEM_CHECKER, user)

    vreport = {"applied": False, "caps": [], "n_caps": 0, "checked": 0}
    if config.VERIFIER_ENABLED:
        raw, vreport = verifier.apply_caps(question, raw, student_answer)
        if vreport["n_caps"]:
            log.info("Verifier обнулил %d критериев", vreport["n_caps"])

    ev = rubric.build_evaluation(question, raw)
    ev.verifier = vreport
    return ev


def generate_followup(question: Question, student_answer: str) -> str:
    user = prompts.FOLLOWUP_TEMPLATE.format(
        question=question.text, student_answer=student_answer,
    )
    raw = groq_client.chat_json(prompts.SYSTEM_FOLLOWUP, user)
    return (raw.get("followup") or "").strip()