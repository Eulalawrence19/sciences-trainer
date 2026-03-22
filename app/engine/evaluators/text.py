# app/engine/evaluators/text.py

from app.models import Question
from app.engine.evaluator import Result


def _normalize(s: str) -> str:
    if not s:
        return ""
    s = s.upper()
    for ch in [" ", "\t", "\n", "(", ")", "[", "]"]:
        s = s.replace(ch, "")
    return s


def evaluate(question: Question, user_answer: str) -> Result:
    expected = question.answer or ""
    correct = _normalize(expected) == _normalize(user_answer)
    return Result(correct=correct, expected=expected)