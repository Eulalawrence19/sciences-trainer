from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# =========================
# CONFIGURACIÓN
# =========================

DATABASE_URL = "sqlite:///./data.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# =========================
# INIT DB
# =========================

def init_db():
    from app.models import Category, Subcategory, Question
    Base.metadata.create_all(bind=engine)


# =========================
# DEPENDENCIA
# =========================

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
