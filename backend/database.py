"""
Database setup com SQLAlchemy
"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings

# Criar diretório data se não existir
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Montar DATABASE_URL corretamente (usar caminho absoluto para SQLite)
if "sqlite" in settings.DATABASE_URL:
    db_path = DATA_DIR / "app.db"
    database_url = f"sqlite:///{db_path}"
else:
    database_url = settings.DATABASE_URL

# Engine
engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para models
Base = declarative_base()


def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa o banco de dados"""
    Base.metadata.create_all(bind=engine)
