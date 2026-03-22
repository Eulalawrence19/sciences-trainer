# app/models.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    ForeignKey,
    CheckConstraint,
)
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
        cascade="all, delete",
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
        nullable=False,
    )

    category = relationship(
        "Category",
        back_populates="subcategories",
    )

    questions = relationship(
        "Question",
        back_populates="subcategory",
        cascade="all, delete",
    )


# =========================
# QUESTION
# =========================

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    # Contenido
    statement_text = Column(Text, nullable=True)
    statement_math = Column(Text, nullable=True)

    # Semántica de evaluación (CONTRATO)
    eval_type = Column(String(20), nullable=False)

    # Respuesta directa (solo si NO es CHOICE)
    answer = Column(Text, nullable=True)

    # Tolerancia numérica (solo NUMERIC)
    tolerance = Column(Float, nullable=True)

    subcategory_id = Column(
        Integer,
        ForeignKey("subcategories.id"),
        nullable=False,
    )

    subcategory = relationship(
        "Subcategory",
        back_populates="questions",
    )

    options = relationship(
        "Option",
        back_populates="question",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        # R1 — debe haber contenido
        CheckConstraint(
            "(statement_text IS NOT NULL) OR (statement_math IS NOT NULL)",
            name="question_has_content",
        ),

        # R3 — exclusión CHOICE vs answer
        CheckConstraint(
            """
            (
                eval_type = 'CHOICE'
                AND answer IS NULL
            )
            OR
            (
                eval_type != 'CHOICE'
                AND answer IS NOT NULL
            )
            """,
            name="question_answer_xor_choice",
        ),

        # R4 — tolerancia solo para NUMERIC
        CheckConstraint(
            """
            (
                eval_type = 'NUMERIC'
                OR tolerance IS NULL
            )
            """,
            name="question_tolerance_only_numeric",
        ),
    )


# =========================
# OPTION
# =========================

class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True)

    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )

    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)

    question = relationship(
        "Question",
        back_populates="options",
    )