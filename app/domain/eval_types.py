# app/domain/eval_types.py

from typing import Final, Tuple

# Dominio cerrado de tipos de evaluación
TEXT: Final[str] = "TEXT"
EQUATION: Final[str] = "EQUATION"
NUMERIC: Final[str] = "NUMERIC"
CHOICE: Final[str] = "CHOICE"
SYNTAX: Final[str] = "SYNTAX"   # ← NUEVO

# Tupla canónica para validación
EVAL_TYPES: Final[Tuple[str, ...]] = (
    TEXT,
    EQUATION,
    NUMERIC,
    CHOICE,
    SYNTAX,                     # ← NUEVO
)