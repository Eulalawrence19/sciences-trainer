#evaluator.py
from app.models import Question
from dataclasses import dataclass

@dataclass(frozen=True)
class Result:
    correct: bool
    expected: str | None = None
    error: str | None = None

    @staticmethod
    def invalid(reason: str) -> "Result":
        return Result(correct=False, error=reason)


def evaluate_answer(question: Question, user_answer: str) -> Result:
    if question is None:
        return Result.invalid("Pregunta inexistente")

    et = question.eval_type

    if et == "TEXT":
        from app.engine.evaluators.text import evaluate
        return evaluate(question, user_answer)

    elif et == "EQUATION":
        from app.engine.evaluators.equation import evaluate
        return evaluate(question, user_answer)

    elif et == "NUMERIC":
        from app.engine.evaluators.numeric import evaluate
        return evaluate(question, user_answer)

    elif et == "CHOICE":
        # 🔒 VALIDACIÓN DE DOMINIO (OBLIGATORIA)
        options = question.options or []

        if len(options) < 2:
            return Result.invalid("CHOICE sin alternativas")

        correct = [o for o in options if o.is_correct]

        if len(correct) != 1:
            return Result.invalid("CHOICE debe tener exactamente una correcta")
    elif et == "SYNTAX":
        from app.engine.evaluators.syntax import evaluate
        return evaluate(question, user_answer)

    else:
        return Result.invalid(f"eval_type no soportado: {et}")