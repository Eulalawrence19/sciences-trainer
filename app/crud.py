from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal
from app.models import Category, Subcategory, Question


# =====================================================
# DB HELPER
# =====================================================

def _get_db() -> Session:
    return SessionLocal()


# =====================================================
# CATEGORY
# =====================================================

def get_categories():
    """
    Devuelve todas las categorías con subcategorías y preguntas
    (eager loading completo para admin)
    """
    db = _get_db()
    try:
        return (
            db.query(Category)
            .options(
                joinedload(Category.subcategories)
                .joinedload(Subcategory.questions)
            )
            .order_by(Category.name)
            .all()
        )
    finally:
        db.close()



def create_category(name: str):
    db = _get_db()
    try:
        db.add(Category(name=name))
        db.commit()
    except IntegrityError:
        db.rollback()
    finally:
        db.close()


def update_category(category_id: int, new_name: str) -> bool:
    db = _get_db()
    try:
        cat = db.query(Category).filter(Category.id == category_id).first()
        if not cat:
            return False

        cat.name = new_name
        db.commit()
        return True
    finally:
        db.close()


def delete_category(category_id: int) -> bool:
    db = _get_db()
    try:
        cat = db.query(Category).filter(Category.id == category_id).first()
        if not cat:
            return False

        db.delete(cat)
        db.commit()
        return True
    finally:
        db.close()


# =====================================================
# SUBCATEGORY
# =====================================================

def get_subcategories(category_id: int):
    db = _get_db()
    try:
        return (
            db.query(Subcategory)
            .filter(Subcategory.category_id == category_id)
            .order_by(Subcategory.name)
            .all()
        )
    finally:
        db.close()


def create_subcategory(category_id: int, name: str):
    db = _get_db()
    try:
        db.add(Subcategory(category_id=category_id, name=name))
        db.commit()
    finally:
        db.close()


def update_subcategory(subcategory_id: int, new_name: str) -> bool:
    db = _get_db()
    try:
        sub = (
            db.query(Subcategory)
            .filter(Subcategory.id == subcategory_id)
            .first()
        )
        if not sub:
            return False

        sub.name = new_name
        db.commit()
        return True
    finally:
        db.close()


def delete_subcategory(subcategory_id: int) -> bool:
    db = _get_db()
    try:
        sub = (
            db.query(Subcategory)
            .filter(Subcategory.id == subcategory_id)
            .first()
        )
        if not sub:
            return False

        db.delete(sub)
        db.commit()
        return True
    finally:
        db.close()


# =====================================================
# QUESTION
# =====================================================

def create_question(subcategory_id: int, statement: str, answer: str):
    db = _get_db()
    try:
        db.add(
            Question(
                subcategory_id=subcategory_id,
                statement=statement,
                answer=answer
            )
        )
        db.commit()
    finally:
        db.close()


def get_question(question_id: int):
    db = _get_db()
    try:
        return (
            db.query(Question)
            .filter(Question.id == question_id)
            .first()
        )
    finally:
        db.close()


def update_question(
    question_id: int,
    new_statement: str,
    new_answer: str
) -> bool:
    db = _get_db()
    try:
        q = db.query(Question).filter(Question.id == question_id).first()
        if not q:
            return False

        q.statement = new_statement
        q.answer = new_answer
        db.commit()
        return True
    finally:
        db.close()


def delete_question(question_id: int) -> bool:
    db = _get_db()
    try:
        q = db.query(Question).filter(Question.id == question_id).first()
        if not q:
            return False

        db.delete(q)
        db.commit()
        return True
    finally:
        db.close()


def get_random_questions(subcategory_id: int, limit: int | None = None):
    """
    Devuelve preguntas aleatorias SIN REPETICIÓN
    """
    db = _get_db()
    try:
        query = (
            db.query(Question)
            .filter(Question.subcategory_id == subcategory_id)
            .order_by(func.random())
        )

        if limit is not None:
            query = query.limit(limit)

        return query.all()
    finally:
        db.close()

from app.db import SessionLocal
from app.models import Category, Subcategory, Question


def update_category(category_id: int, name: str):
    db = SessionLocal()
    try:
        c = db.query(Category).get(category_id)
        if c:
            c.name = name
            db.commit()
    finally:
        db.close()


def update_subcategory(subcategory_id: int, name: str):
    db = SessionLocal()
    try:
        s = db.query(Subcategory).get(subcategory_id)
        if s:
            s.name = name
            db.commit()
    finally:
        db.close()


def update_question(question_id: int, statement: str, answer: str):
    db = SessionLocal()
    try:
        q = db.query(Question).get(question_id)
        if q:
            q.statement = statement
            q.answer = answer
            db.commit()
    finally:
        db.close()
