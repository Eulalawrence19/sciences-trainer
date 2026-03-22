# app/services/exam_session.py

from app.engine.evaluator import evaluate_answer, Result
from app.crud import get_question
from app.domain.normalization import (
    normalize_text,
    normalize_equation,
)


def normalize_user_answer(question, user_answer: str) -> str:
    """
    R9 — Normalización OBLIGATORIA de la respuesta del usuario
    según el tipo de evaluación.
    """

    if user_answer is None:
        return ""

    et = question.eval_type

    if et in ("TEXT", "CHOICE"):
        return normalize_text(user_answer)

    elif et in ("EQUATION", "NUMERIC"):
        return normalize_equation(user_answer)

    # fallback defensivo
    return user_answer


def evaluate_question(question_id: int, user_answer: str) -> Result:
    """
    Punto ÚNICO de entrada a la evaluación.
    Aquí se impone R9.
    """

    question = get_question(question_id)

    if question is None:
        return Result.invalid("Pregunta inexistente")

    # 🔒 R9 APLICADO AQUÍ
    normalized_answer = normalize_user_answer(question, user_answer)

    return evaluate_answer(question, normalized_answer) 