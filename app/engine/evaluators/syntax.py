#syntax.py
from app.models import Question
from app.engine.evaluator import Result


def normalize_code(s: str) -> str:

    if not s:
        return ""

    lines = s.splitlines()

    cleaned = []

    for line in lines:

        line = line.replace("\t", "    ")
        line = line.rstrip()

        if line.strip():
            cleaned.append(line)

    return "\n".join(cleaned)


def evaluate(question: Question, user_answer: str) -> Result:

    expected = question.answer or ""

    a = normalize_code(user_answer)
    b = normalize_code(expected)

    correct = a == b

    return Result(
        correct=correct,
        expected=expected
    )