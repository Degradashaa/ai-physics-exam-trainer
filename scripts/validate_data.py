import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

q = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
r = json.loads((DATA / "rubrics.json").read_text(encoding="utf-8"))
ref = json.loads((DATA / "reference_answers.json").read_text(encoding="utf-8"))

errors = []
for item in q:
    qid = item["id"]
    if qid not in r:
        errors.append(f"нет рубрики для {qid}")
    if qid not in ref:
        errors.append(f"нет эталона для {qid}")
    if not item.get("topic") or not item.get("text"):
        errors.append(f"{qid}: пустые topic/text")

if errors:
    print("Ошибки:")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print(f"OK: {len(q)} вопросов, у всех есть рубрика и эталон")