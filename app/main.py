from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import time

from app.db import init_db
from app.crud import (
    create_category,
    create_subcategory,
    create_question,
    create_option,
    delete_option,
    get_categories,
    get_random_questions,
    get_question,
    delete_category,
    delete_subcategory,
    delete_question,
    update_category,
    update_subcategory,
    update_question
)
from app.engine import evaluate_answer


app = FastAPI(title="Sciences Trainer")
templates = Jinja2Templates(directory="app/templates")

# =====================================================
# SESIÓN (single-user, simple)
# =====================================================
SESSION = {}


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
    categories = get_categories()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "categories": categories
        }
    )


# =====================================================
# ADMIN
# =====================================================
@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):
    categories = get_categories()
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "categories": categories
        }
    )


@app.post("/admin/category")
def admin_create_category(name: str = Form(...)):
    create_category(name)
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/subcategory")
def admin_create_subcategory(
    category_id: int = Form(...),
    name: str = Form(...)
):
    create_subcategory(category_id, name)
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/option/delete")
def admin_delete_option(option_id: int = Form(...)):
    delete_option(option_id)
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/question")
def admin_create_question(
    subcategory_id: int = Form(...),
    statement: str = Form(...),
    answer: str = Form(...)
):
    create_question(subcategory_id, statement, answer)
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/option")
def admin_create_option(
    question_id: int = Form(...),
    text: str = Form(...),
    is_correct: bool = Form(False)
):
    create_option(question_id, text, is_correct)
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/category/delete")
def admin_delete_category(category_id: int = Form(...)):
    delete_category(category_id)
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/subcategory/delete")
def admin_delete_subcategory(subcategory_id: int = Form(...)):
    delete_subcategory(subcategory_id)
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/question/delete")
def admin_delete_question(question_id: int = Form(...)):
    delete_question(question_id)
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/category/update")
def admin_update_category(
    category_id: int = Form(...),
    name: str = Form(...)
):
    update_category(category_id, name)
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/subcategory/update")
def admin_update_subcategory(
    subcategory_id: int = Form(...),
    name: str = Form(...)
):
    update_subcategory(subcategory_id, name)
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/question/update")
def admin_update_question(
    question_id: int = Form(...),
    statement: str = Form(...),
    answer: str = Form(...)
):
    update_question(question_id, statement, answer)
    return RedirectResponse("/admin", status_code=303)

# =====================================================
# PLAY — INICIO
# =====================================================
@app.post("/play/question", response_class=HTMLResponse)
def play_start(
    request: Request,
    subcategory_id: int = Form(...),
    limit: int = Form(...),
    time_limit: int = Form(...),
    all_questions: int | None = Form(None),
    exam: int | None = Form(None)
):
    if all_questions:
        questions = get_random_questions(subcategory_id, None)
    else:
        questions = get_random_questions(subcategory_id, limit)

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
        "answers": []
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
                "total": len(SESSION["queue"])
            }
        }
    )


# =====================================================
# PLAY — RESPUESTA NORMAL
# =====================================================
@app.post("/play/answer", response_class=HTMLResponse)
def play_answer(
    request: Request,
    question_id: int = Form(...),
    subcategory_id: int = Form(...),
    user_answer: str = Form(...)
):
    elapsed = time.time() - SESSION["start_time"]
    remaining = int(SESSION["time_limit"] - elapsed)

    # ⛔ si el tiempo ya acabó, mostrar resumen
    if remaining <= 0:
        return play_timeout(request)

    # guardar respuesta
    SESSION["answers"].append({
        "question_id": question_id,
        "user_answer": user_answer
    })

    result = None

    if SESSION["mode"] == "training":
        result = evaluate_answer(question_id, user_answer)
        if result["correct"]:
            SESSION["correct"] += 1

    SESSION["current"] += 1

    # ⛔ fin por preguntas
    if SESSION["current"] >= len(SESSION["queue"]):
        return play_timeout(request)

    # siguiente pregunta
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
            "total": len(SESSION["queue"])
        }
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

    if SESSION.get("mode") == "exam":
        correct = 0
        for a in SESSION.get("answers", []):
            r = evaluate_answer(a["question_id"], a["user_answer"])
            if r["correct"]:
                correct += 1
    else:
        correct = SESSION.get("correct", 0)

    return templates.TemplateResponse(
        "play.html",
        {
            "request": request,
            "summary": {
                "attempts": attempts,
                "correct": correct,
                "timeout": True
            },
            "training": False
        }
    )
