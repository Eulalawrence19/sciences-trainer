from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


# =========================
# CATEGORY
# =========================

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    subcategories = relationship(
        "Subcategory",
        back_populates="category",
        cascade="all, delete"
    )


# =========================
# SUBCATEGORY
# =========================

class Subcategory(Base):
    __tablename__ = "subcategories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False
    )

    category = relationship(
        "Category",
        back_populates="subcategories"
    )

    questions = relationship(
        "Question",
        back_populates="subcategory",
        cascade="all, delete"
    )


# =========================
# QUESTION
# =========================

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    # Texto del enunciado (puede incluir LaTeX)
    statement = Column(Text, nullable=False)

    # Respuesta directa (para matemática u otros)
    answer = Column(Text, nullable=False)

    subcategory_id = Column(
        Integer,
        ForeignKey("subcategories.id"),
        nullable=False
    )

    subcategory = relationship(
        "Subcategory",
        back_populates="questions"
    )

    # Opciones (para lectura / alternativas)
    options = relationship(
        "Option",
        back_populates="question",
        cascade="all, delete-orphan"
    )


# =========================
# OPTION / ALTERNATIVE
# =========================

class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True)
    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False
    )

    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)

    question = relationship(
        "Question",
        back_populates="options"
    )
