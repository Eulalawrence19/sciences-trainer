# app/engine/evaluators/numeric.py

from app.models import Question
from app.engine.evaluator import Result


def _parse_float(s: str) -> float | None:
    try:
        return float(s.strip())
    except Exception:
        return None


def evaluate(question: Question, user_answer: str) -> Result:
    expected_raw = question.answer
    tolerance = question.tolerance

    if expected_raw is None:
        return Result(correct=False, expected=None)

    expected_val = _parse_float(expected_raw)
    given_val = _parse_float(user_answer)

    if expected_val is None or given_val is None:
        return Result(correct=False, expected=expected_raw)

    if tolerance is None:
        correct = expected_val == given_val
    else:
        correct = abs(expected_val - given_val) <= tolerance

    return Result(correct=correct, expected=expected_raw)