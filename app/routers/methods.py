from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import TransactionMethod

router = APIRouter(prefix="/transaction-methods", tags=["Transaction Methods"])

@router.get("/")
async def list_transaction_methods(db: AsyncSession = Depends(get_db)):
    """Retourne la liste de toutes les méthodes disponibles"""
    result = await db.execute(select(TransactionMethod))
    methods = result.scalars().all()
    return methods

@router.get("/{method_id}")
async def get_transaction_method(method_id: int, db: AsyncSession = Depends(get_db)):
    """Retourne les détails d'une méthode spécifique (ex: MTN Benin)"""
    result = await db.execute(select(TransactionMethod).where(TransactionMethod.id == method_id))
    method = result.scalars().first()
    if not method:
        raise HTTPException(status_code=404, detail="Méthode introuvable")
    return method
