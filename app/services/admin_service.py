# app/services/admin_service.py

from app.domain.eval_types import EVAL_TYPES
from app.crud import create_question


def create_question_from_admin(
    *,
    subcategory_id: int,
    raw_statement: str,
    eval_type: str,
    answer: str | None = None,
    tolerance: float | None = None,
) -> int:
    """
    Application service para creación de preguntas desde admin.

    Decisión actual:
    - El admin guarda texto normal
    - statement_math se reserva para matemáticas
    """

    # -------------------------------------------------
    # 1. Validar eval_type (dominio cerrado)
    # -------------------------------------------------
    if eval_type not in EVAL_TYPES:
        raise ValueError(f"Invalid eval_type: {eval_type}")

    # -------------------------------------------------
    # 2. Validar enunciado
    # -------------------------------------------------
    statement_text = raw_statement.strip()

    if not statement_text:
        raise ValueError("Statement cannot be empty")

    statement_math = None

    # -------------------------------------------------
    # 3. Reglas por tipo de evaluación
    # -------------------------------------------------
    if eval_type == "CHOICE":
        # CHOICE:
        # - no usa answer
        # - no usa tolerance
        answer = None
        tolerance = None

    elif eval_type == "NUMERIC":
        # NUMERIC:
        # - requiere answer
        # - tolerance puede venir o no
        if answer is None:
            raise ValueError("NUMERIC question requires answer")
    elif eval_type == "SYNTAX":
        if answer is None:
            raise ValueError("SYNTAX question requires answer")
        tolerance = None

    else:
        # TEXT / EQUATION:
        # - requieren answer
        # - NO usan tolerance
        if answer is None:
            raise ValueError(f"{eval_type} question requires answer")

        tolerance = None

    # -------------------------------------------------
    # 4. Persistir (CRUD)
    # -------------------------------------------------
    return create_question(
        subcategory_id=subcategory_id,
        statement_text=statement_text,
        statement_math=statement_math,
        eval_type=eval_type,
        answer=answer,
        tolerance=tolerance,
    )