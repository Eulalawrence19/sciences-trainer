#main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import time
from fastapi import UploadFile, File
import csv
import io
import re
import json
from fastapi import UploadFile, File
from fastapi.responses import RedirectResponse

from app.db import init_db
from app.services.admin_service import create_question_from_admin
from app.services.question_service import update_question_full
from app.services.exam_session import evaluate_question

from app.crud import (
    create_category,
    create_subcategory,
    create_option,
    delete_option,
    get_categories,
    get_question,
    delete_category,
    delete_subcategory,
    delete_question,
    update_category,
    update_subcategory,
    update_option,
    set_correct_option,
    get_playable_questions,   # 👈 IMPORTANTE
)

# =====================================================
# APP
# =====================================================

app = FastAPI(title="Sciences Trainer")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)

# =====================================================
# SESIÓN (single-user, simple)
# =====================================================

SESSION: dict = {}

# =====================================================
# STARTUP
# =====================================================

@app.on_event("startup")
def startup():
    init_db()

# =====================================================
# INDEX
# =====================================================

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    categories_db = get_categories()

    categories = [
        {
            "id": c.id,
            "name": c.name,
            "subcategories": [
                {"id": s.id, "name": s.name}
                for s in c.subcategories
            ]
        }
        for c in categories_db
    ]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "categories": categories
        },
    )
# =====================================================
# ADMIN
# =====================================================

@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):
    categories_db = get_categories()

    categories = [
        {
            "id": c.id,
            "name": c.name,
            "subcategories": [
                {
                    "id": s.id,
                    "name": s.name,
                    "questions": [
                        {
                            "id": q.id,
                            "eval_type": q.eval_type,
                            "statement_text": q.statement_text,
                            "statement_math": q.statement_math,
                            "options": [
                                {
                                    "id": o.id,
                                    "text": o.text,
                                    "is_correct": o.is_correct
                                }
                                for o in getattr(q, "options", [])
                            ]
                        }
                        for q in getattr(s, "questions", [])
                    ]
                }
                for s in c.subcategories
            ]
        }
        for c in categories_db
    ]

    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "categories_admin": categories},
    )
# ---------- CATEGORY ----------

@app.post("/admin/category")
def admin_create_category(name: str = Form(...)):
    create_category(name)
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/category/delete")
def admin_delete_category(category_id: int = Form(...)):
    delete_category(category_id)
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/category/update")
def admin_update_category(
    category_id: int = Form(...),
    name: str = Form(...),
):
    update_category(category_id, name)
    return RedirectResponse("/admin", status_code=303)

# ---------- SUBCATEGORY ----------

@app.post("/admin/subcategory")
def admin_create_subcategory(
    category_id: int = Form(...),
    name: str = Form(...),
):
    create_subcategory(category_id, name)
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/subcategory/delete")
def admin_delete_subcategory(subcategory_id: int = Form(...)):
    delete_subcategory(subcategory_id)
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/subcategory/update")
def admin_update_subcategory(
    subcategory_id: int = Form(...),
    name: str = Form(...),
):
    update_subcategory(subcategory_id, name)
    return RedirectResponse("/admin", status_code=303)

# ---------- QUESTION ----------

@app.post("/admin/question")
def admin_create_question(
    subcategory_id: int = Form(...),
    statement: str = Form(...),
    eval_type: str = Form(...),
    answer: str | None = Form(None),
    tolerance: float | None = Form(None),
):
    create_question_from_admin(
        subcategory_id=subcategory_id,
        raw_statement=statement,
        eval_type=eval_type,
        answer=answer,
        tolerance=tolerance,
    )
    return RedirectResponse("/admin", status_code=303)

# ---------- QUESTION (JSON / PRODUCTIVO) ----------

@app.post("/admin/question/json")
def admin_create_question_json(
    subcategory_id: int = Form(...),
    statement: str = Form(...),
    eval_type: str = Form(...),
    answer: str | None = Form(None),
    tolerance: float | None = Form(None),
):
    """
    Endpoint PRODUCTIVO:
    - No redirige
    - Devuelve confirmación real (JSON)
    """

    try:
        qid = create_question_from_admin(
            subcategory_id=subcategory_id,
            raw_statement=statement,
            eval_type=eval_type,
            answer=answer,
            tolerance=tolerance,
        )
        return {
            "ok": True,
            "id": qid,
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
        }



@app.post("/admin/question/edit")
def admin_edit_question(
    question_id: int = Form(...),
    statement_text: str | None = Form(None),
    statement_math: str | None = Form(None),
    eval_type: str = Form(...),
    answer: str | None = Form(None),
    tolerance: float | None = Form(None),
):
    q = get_question(question_id)
    if not q:
        return RedirectResponse("/admin", status_code=303)

    update_question_full(
        question=q,
        statement_text=statement_text,
        statement_math=statement_math,
        eval_type=eval_type,
        answer=answer,
        tolerance=tolerance,
    )

    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/question/delete")
def admin_delete_question(question_id: int = Form(...)):
    delete_question(question_id)
    return RedirectResponse("/admin", status_code=303)

# ---------- OPTIONS ----------

@app.post("/admin/option")
def admin_create_option(
    question_id: int = Form(...),
    text: str = Form(...),
    is_correct: bool = Form(False),
):
    create_option(
        question_id=question_id,
        text=text,
        is_correct=is_correct,
    )
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/option/edit")
def admin_edit_option(
    option_id: int = Form(...),
    text: str = Form(...),
    is_correct: bool = Form(False),
):
    update_option(
        option_id=option_id,
        text=text,
        is_correct=is_correct,
    )
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/option/set-correct")
def admin_set_correct_option(
    question_id: int = Form(...),
    option_id: int = Form(...),
):
    set_correct_option(
        question_id=question_id,
        option_id=option_id,
    )
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/option/delete")
def admin_delete_option(option_id: int = Form(...)):
    delete_option(option_id)
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/import")
async def admin_import_questions(file: UploadFile = File(...)):

    content = await file.read()

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return {
            "created": 0,
            "errors": ["Archivo no es UTF-8"]
        }

    reader = csv.DictReader(io.StringIO(text))

    required_columns = {
        "subcategory_id",
        "statement",
        "eval_type",
        "answer",
        "tolerance",
    }

    if not required_columns.issubset(reader.fieldnames or []):
        return {
            "created": 0,
            "errors": [
                "Header inválido. Debe ser: "
                "subcategory_id,statement,eval_type,answer,tolerance"
            ]
        }

    created = 0
    errors: list[str] = []

    for line, row in enumerate(reader, start=2):

        try:

            subcategory_id = int(row["subcategory_id"])

            statement = (row.get("statement") or "").strip()
            eval_type = (row.get("eval_type") or "").strip()

            answer = row.get("answer")

            if answer:
                # permite código multilínea usando \n
                answer = answer.replace("\\n", "\n").strip()
            else:
                answer = None

            tolerance_raw = row.get("tolerance")
            tolerance = float(tolerance_raw) if tolerance_raw else None

            # ---------------------------
            # Validaciones
            # ---------------------------

            if not statement:
                raise ValueError("statement vacío")

            if eval_type not in EVAL_TYPES:
                raise ValueError(f"eval_type inválido: {eval_type}")

            # CSV no soporta CHOICE
            if eval_type == "CHOICE":
                raise ValueError("CHOICE no soportado en CSV")

            # ---------------------------
            # Reglas por tipo
            # ---------------------------

            if eval_type == "NUMERIC":
                if answer is None:
                    raise ValueError("NUMERIC requiere answer")

            else:
                if answer is None:
                    raise ValueError(f"{eval_type} requiere answer")
                tolerance = None

            # ---------------------------
            # Crear pregunta
            # ---------------------------

            create_question_from_admin(
                subcategory_id=subcategory_id,
                raw_statement=statement,
                eval_type=eval_type,
                answer=answer,
                tolerance=tolerance,
            )

            created += 1

        except Exception as e:
            errors.append(f"line {line}: {str(e)}")

    return {
        "created": created,
        "errors": errors
    }

@app.post("/admin/import/file")
async def admin_import_file(
    subcategory_id: int = Form(...),
    file: UploadFile = File(...)
):

    content = await file.read()

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return RedirectResponse("/admin", status_code=303)

    blocks = re.split(r"\n\s*\n", text.strip())

    for block in blocks:

        lines = block.splitlines()

        statement = None
        tolerance = None
        answer_lines = []

        reading_answer = False

        for line in lines:

            if line.startswith("Q:"):
                statement = line[2:].strip()
                reading_answer = False

            elif line.startswith("A:"):
                reading_answer = True

                content = line[2:].lstrip()
                if content:
                    answer_lines.append(content)

            elif line.startswith("T:"):

                reading_answer = False

                try:
                    tolerance = float(line[2:].strip())
                except ValueError:
                    tolerance = None

            else:
                if reading_answer:
                    answer_lines.append(line)

        answer = "\n".join(answer_lines).rstrip()

        if not statement or not answer:
            continue

        # ---------------------------
        # Determinar tipo
        # ---------------------------

        eval_type = "TEXT"

        if tolerance is not None:
            eval_type = "NUMERIC"

        if "\n" in answer:
            eval_type = "SYNTAX"

        # ---------------------------
        # Crear pregunta
        # ---------------------------

        create_question_from_admin(
            subcategory_id=subcategory_id,
            raw_statement=statement,
            eval_type=eval_type,
            answer=answer,
            tolerance=tolerance,
        )

    return RedirectResponse("/admin", status_code=303)

# =====================================================
# PLAY — INICIO
# =====================================================

@app.post("/play/question", response_class=HTMLResponse)
def play_start(
    request: Request,
    subcategory_id: int = Form(...),
    limit: int | None = Form(None),
    time_limit: int = Form(...),
    all_questions: bool = Form(False),
    exam: bool = Form(False),
):
    if not all_questions and limit is None:
        return RedirectResponse("/", status_code=303)

    questions = get_playable_questions(
        subcategory_id=subcategory_id,
        limit=None if all_questions else limit,
    )

    if not questions:
        return RedirectResponse("/", status_code=303)

    SESSION.clear()
    SESSION.update({
        "queue": [q.id for q in questions],
        "current": 0,
        "correct": 0,
        "start_time": time.time(),
        "time_limit": time_limit * 60,
        "mode": "exam" if exam else "training",
        "answers": [],
    })

    first_question = get_question(SESSION["queue"][0])

    return templates.TemplateResponse(
        "play.html",
        {
            "request": request,
            "question": first_question,
            "subcategory_id": subcategory_id,
            "training": True,
            "remaining_time": SESSION["time_limit"],
            "progress": {
                "current": 1,
                "total": len(SESSION["queue"]),
            },
        },
    )

# =====================================================
# PLAY — RESPUESTA
# =====================================================

@app.post("/play/answer", response_class=HTMLResponse)
def play_answer(
    request: Request,
    question_id: int = Form(...),
    subcategory_id: int = Form(...),
    user_answer: str = Form(...),
):
    elapsed = time.time() - SESSION["start_time"]
    remaining = int(SESSION["time_limit"] - elapsed)

    if remaining <= 0:
        return play_timeout(request)

    SESSION["answers"].append({
        "question_id": question_id,
        "user_answer": user_answer,
    })

    result = None
    if SESSION["mode"] == "training":
        result = evaluate_question(question_id, user_answer)
        if result.correct:
            SESSION["correct"] += 1

    SESSION["current"] += 1

    if SESSION["current"] >= len(SESSION["queue"]):
        return play_timeout(request)

    next_q_id = SESSION["queue"][SESSION["current"]]
    next_question = get_question(next_q_id)

    context = {
        "request": request,
        "question": next_question,
        "subcategory_id": subcategory_id,
        "training": True,
        "remaining_time": remaining,
        "progress": {
            "current": SESSION["current"] + 1,
            "total": len(SESSION["queue"]),
        },
    }

    if result:
        context["result"] = result

    return templates.TemplateResponse("play.html", context)

# =====================================================
# PLAY — TIMEOUT / FIN
# =====================================================

@app.post("/play/timeout", response_class=HTMLResponse)
def play_timeout(request: Request):
    attempts = SESSION.get("current", 0)

    correct = 0
    for a in SESSION.get("answers", []):
        r = evaluate_question(a["question_id"], a["user_answer"])
        if r.correct:
            correct += 1

    return templates.TemplateResponse(
        "play.html",
        {
            "request": request,
            "summary": {
                "attempts": attempts,
                "correct": correct,
                "timeout": True,
            },
            "training": False,
        },
    )