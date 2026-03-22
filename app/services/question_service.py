#question_service.py
from app.crud import (
    update_question,
    delete_options_by_question,
)
from app.models import Question

def update_question_full(
    *,
    question: Question,
    statement_text: str | None,
    statement_math: str | None,
    eval_type: str,
    answer: str | None,
    tolerance: float | None,
):
    """
    Actualiza una pregunta como agregado.
    """

    # ───────────────────────────────
    # Reglas duras
    # ───────────────────────────────

    if eval_type == "CHOICE":
        answer = None
        tolerance = None

    if eval_type != "CHOICE":
        # Si deja de ser CHOICE → borrar alternativas
        delete_options_by_question(question.id)

    # ───────────────────────────────
    # Persistencia
    # ───────────────────────────────

    update_question(
        question_id=question.id,
        statement_text=statement_text,
        statement_math=statement_math,
        answer=answer,
        tolerance=tolerance,
    )

    question.eval_type = eval_type