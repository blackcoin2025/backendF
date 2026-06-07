# app/database.py
import os
from typing import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

# 🔄 Charge les variables d'environnement
load_dotenv()
ENV = os.getenv("ENV", "dev")

# =========================================================
# MAIN DATABASE (WALLET)
# =========================================================
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL manquant dans .env")

engine = create_async_engine(
    DATABASE_URL,
    echo=(ENV == "dev"),
    future=True,
    pool_pre_ping=True,
    poolclass=NullPool,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# =========================================================
# LINEAI DATABASE
# =========================================================
LINEAI_DATABASE_URL = os.getenv("LINEAI_DATABASE_URL")
if not LINEAI_DATABASE_URL:
    raise ValueError("❌ LINEAI_DATABASE_URL manquant dans .env")

lineai_engine = create_async_engine(
    LINEAI_DATABASE_URL,
    echo=(ENV == "dev"),
    future=True,
    pool_pre_ping=True,
    poolclass=NullPool,
)

LineAISessionLocal = async_sessionmaker(
    bind=lineai_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

LineAIBase = declarative_base()

# =========================================================
# FASTAPI DEPENDENCIES
# =========================================================
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_lineai_db() -> AsyncGenerator[AsyncSession, None]:
    async with LineAISessionLocal() as session:
        yield session

# =========================================================
# INIT DATABASES
# =========================================================
async def init_db() -> None:
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with lineai_engine.begin() as conn:
            await conn.run_sync(LineAIBase.metadata.create_all)
        print("✅ Toutes les bases de données sont initialisées.")
    except Exception as e:
        print(f"❌ Erreur init_db : {e}")
        raise