# app/routers/withdraw_methods.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from app.models import TransactionMethod
from app.database import get_db

router = APIRouter(
    prefix="/withdraw-methods",
    tags=["Withdraw Methods"]
)

# 🧩 Schéma de réponse
class WithdrawMethodResponse(BaseModel):
    id: int
    name: str
    icon_url: str | None = None
    country: str | None = None

    class Config:
        from_attributes = True  # Pydantic v2 : remplace orm_mode

# 🚀 Route principale : liste les méthodes de retrait
@router.get("/", response_model=List[WithdrawMethodResponse])
async def get_withdraw_methods(session: AsyncSession = Depends(get_db)):
    """
    Retourne la liste des méthodes de retrait disponibles :
    - id
    - nom
    - icône
    - pays
    """
    query = (
        select(
            TransactionMethod.id,
            TransactionMethod.name,
            TransactionMethod.icon_url,
            TransactionMethod.country
        )
        .where(TransactionMethod.type == "withdrawal")
    )

    result = await session.execute(query)
    methods = result.all()

    # Convertit [(id, name, icon_url, country)] → [{...}, {...}]
    return [
        {"id": id_, "name": name, "icon_url": icon_url, "country": country}
        for id_, name, icon_url, country in methods
    ]
