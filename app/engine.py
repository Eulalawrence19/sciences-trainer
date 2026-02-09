from app.crud import get_question


# =========================
# NORMALIZACIÓN
# =========================

def normalize(s: str) -> str:
    if not s:
        return ""

    s = s.upper()

    for ch in [" ", "\t", "\n", "(", ")", "[", "]"]:
        s = s.replace(ch, "")

    s = (
        s.replace("*", "X")
         .replace("·", "X")
         .replace("×", "X")
    )

    return s


# =========================
# EVALUACIÓN
# =========================

def evaluate_answer(question_id: int, user_answer: str) -> dict:
    question = get_question(question_id)

    if not question:
        return {
            "correct": False,
            "expected": None
        }

    expected = normalize(question.answer)
    given = normalize(user_answer)

    if given == expected:
        return {
            "correct": True,
            "expected": question.answer
        }

    return {
        "correct": False,
        "expected": question.answer
    }
