# app/engine/evaluators/choice.py

from app.models import Question
from app.engine.evaluator import Result


def evaluate(question: Question, user_answer: str) -> Result:
    try:
        selected_id = int(user_answer)
    except Exception:
        return Result(correct=False, expected=None)

    correct_option = None
    for opt in question.options:
        if opt.is_correct:
            correct_option = opt
            break

    if correct_option is None:
        # pregunta mal construida
        return Result(correct=False, expected=None)

    correct = (selected_id == correct_option.id)

    return Result(
        correct=correct,
        expected=str(correct_option.id)
    )