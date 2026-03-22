# app/engine/evaluators/equation.py

from app.models import Question
from app.engine.evaluator import Result


def _normalize_equation(s: str) -> str:
    if not s:
        return ""
    s = s.upper()

    for ch in [" ", "\t", "\n", "(", ")", "[", "]"]:
        s = s.replace(ch, "")

    # normalización explícita de multiplicación
    s = (
        s.replace("*", "X")
         .replace("·", "X")
         .replace("×", "X")
    )
    return s


def evaluate(question: Question, user_answer: str) -> Result:
    expected = question.answer or ""
    correct = (
        _normalize_equation(expected)
        == _normalize_equation(user_answer)
    )
    return Result(correct=correct, expected=expected)