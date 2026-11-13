import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import streamlit as st
from app import config
from app.schemas import Question, Criterion
from app.retrieval import search
from app.exam_service import ExamSession

st.set_page_config(
    page_title="ИИ-тренажёр к УГ по физике",
    page_icon="⚛️",
    layout="wide",
)


@st.cache_data
def load_questions():
    with open(config.QUESTIONS_FILE, encoding="utf-8") as f:
        qdata = json.load(f)
    with open(config.RUBRICS_FILE, encoding="utf-8") as f:
        rdata = json.load(f)
    with open(config.REFERENCE_FILE, encoding="utf-8") as f:
        ref = json.load(f)
    result = []
    for q in qdata:
        criteria = [Criterion(**c) for c in rdata.get(q["id"], [])]
        result.append(
            Question(
                id=q["id"],
                topic=q["topic"],
                text=q["text"],
                reference=ref.get(q["id"], ""),
                criteria=criteria,
            )
        )
    return result


# инициализация состояния
for k, v in {
    "session": None,
    "stage": "pick",
    "followup_count": 0,
    "current_followup": "",
    "last_eval": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.title("⚛️ ИИ-тренажёр для подготовки к устному экзамену по физике")
st.caption("Проверка по рубрике · Groq LLM · эталонные ответы · без замены преподавателя")

questions = load_questions()
tab_pick, tab_answer, tab_result = st.tabs(
    ["🎯 Выбор билета", "📝 Устный ответ", "📊 Результат"]
)

# выбор
with tab_pick:
    query = st.text_input("Поиск по теме / ключевому слову", "")
    found = search(questions, query, top_k=20)
    options = {f"[{q.topic}] {q.text[:90]}...": q for q in found}
    if not options:
        st.warning("Ничего не найдено. Попробуйте другой запрос.")
    else:
        choice = st.selectbox("Выберите вопрос", list(options.keys()))
        if st.button("Начать ответ", type="primary"):
            st.session_state.session = ExamSession(options[choice])
            st.session_state.stage = "answer"
            st.session_state.followup_count = 0
            st.session_state.current_followup = ""
            st.session_state.last_eval = None
            st.success("Вопрос загружен. Переходите на вкладку «Устный ответ».")

# ответ
with tab_answer:
    if st.session_state.session is None:
        st.info("Сначала выберите билет на вкладке «Выбор билета».")
    else:
        try:
            s: ExamSession = st.session_state.session
            st.markdown(f"**Вопрос:** {s.question.text}")
            st.markdown(f"**Тема:** {s.question.topic}")
            with st.expander("Критерии оценки"):
                for c in s.question.criteria:
                    st.markdown(f"- `{c.id}` {c.text} — {c.weight} б.")

            stage = st.session_state.stage

            if stage == "answer":
                answer = st.text_area(
                    "Ваш устный ответ (можно печатать)",
                    height=200,
                    key="main_answer",
                )
                c1, c2 = st.columns(2)
                if c1.button("✅ Оценить ответ", type="primary"):
                    if answer.strip():
                        s.submit_main(answer)
                        st.session_state.stage = "evaluating"
                        st.rerun()
                    else:
                        st.warning("Введите ответ.")
                if c2.button("🔁 Задать уточняющий вопрос"):
                    if answer.strip():
                        s.submit_main(answer)
                        with st.spinner("Формулирую уточняющий вопрос..."):
                            fq = s.next_followup()
                        if fq:
                            st.session_state.current_followup = fq
                            st.session_state.followup_count = 1
                            st.session_state.stage = "followup"
                        else:
                            st.session_state.stage = "evaluating"
                        st.rerun()
                    else:
                        st.warning("Сначала ответьте на основной вопрос.")

            elif stage == "followup":
                if s.answer_parts:
                    with st.expander("Ваш ответ на основной вопрос"):
                        st.write(s.answer_parts[0])
                st.info(f"**Уточняющий вопрос:** {st.session_state.current_followup}")
                fu = st.text_area(
                    "Ваш ответ на уточнение",
                    height=150,
                    key=f"fu_answer_{st.session_state.followup_count}",
                )
                c1, c2 = st.columns(2)
                if c1.button("📊 Оценить сейчас", type="primary"):
                    if fu.strip():
                        s.add_followup_qa(st.session_state.current_followup, fu)
                        st.session_state.stage = "evaluating"
                        st.rerun()
                    else:
                        st.warning("Введите ответ.")
                if st.session_state.followup_count < config.MAX_FOLLOWUPS:
                    if c2.button("🔁 Ещё уточнение"):
                        if fu.strip():
                            s.add_followup_qa(st.session_state.current_followup, fu)
                            with st.spinner("Формулирую ещё один вопрос..."):
                                fq = s.next_followup()
                            if fq:
                                st.session_state.current_followup = fq
                                st.session_state.followup_count += 1
                            else:
                                st.session_state.stage = "evaluating"
                            st.rerun()
                        else:
                            st.warning("Введите ответ.")

            elif stage == "evaluating":
                with st.spinner("Проверяю по рубрике..."):
                    ev = s.evaluate()
                st.session_state.last_eval = ev
                st.session_state.stage = "done"
                st.rerun()

            elif stage == "done":
                st.success("Готово! Откройте вкладку «Результат».")

        except Exception as e:
            st.error(f"Ошибка: {e}")

# результат
with tab_result:
    ev = st.session_state.get("last_eval")
    if not ev:
        st.info("Пока нет результата. Сначала ответьте на билет.")
    else:
        st.metric("Итог", f"{ev.total_score} / {ev.max_score}")
        st.write(f"**Оценка:** {ev.grade}")

        v = ev.verifier or {}
        if v.get("n_caps"):
            with st.expander(f"🛡 Верификатор обнулил {v['n_caps']} критериев"):
                for cap in v["caps"]:
                    st.write(
                        f"- **{cap['id']}**: LLM поставила {cap['llm_score']} → 0. "
                        f"_{cap['reason']}_"
                    )
        
        if ev.missing:
            st.subheader("Чего не хватило")
            for m in ev.missing:
                st.write(f"- {m}")
                
        if ev.errors:
            st.subheader("Найденные ошибки")
            for e in ev.errors:
                st.write(f"- {e}")
                
        st.subheader("Резюме")
        st.write(ev.summary)
        
        if st.button("🔄 Начать заново"):
            st.session_state.session = None
            st.session_state.stage = "pick"
            st.session_state.last_eval = None
            st.rerun()