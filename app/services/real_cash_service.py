from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models import RealCash

# ============================================================
# 🔹 Ajouter des fonds réels
# ============================================================
async def add_real_cash(user_id: int, amount: float, db: AsyncSession) -> RealCash:
    # Conversion sûre en Decimal
    decimal_amount = Decimal(str(amount))

    result = await db.execute(select(RealCash).where(RealCash.user_id == user_id))
    real_cash = result.scalars().first()

    if real_cash:
        real_cash.cash_balance += decimal_amount
        real_cash.updated_at = func.now()
    else:
        real_cash = RealCash(
            user_id=user_id,
            cash_balance=decimal_amount
        )
        db.add(real_cash)

    # Commit et refresh pour s'assurer que la valeur est persistée
    await db.commit()
    await db.refresh(real_cash)
    return real_cash


# ============================================================
# 🔹 Retirer des fonds réels
# ============================================================
async def remove_real_cash(user_id: int, amount: float, db: AsyncSession) -> RealCash:
    decimal_amount = Decimal(str(amount))

    result = await db.execute(
        select(RealCash)
        .where(RealCash.user_id == user_id)
        .with_for_update()
    )
    real_cash = result.scalars().first()

    if not real_cash or real_cash.cash_balance < decimal_amount:
        raise HTTPException(
            status_code=400,
            detail="Fonds réels insuffisants"
        )

    real_cash.cash_balance -= decimal_amount
    real_cash.updated_at = func.now()

    await db.commit()
    await db.refresh(real_cash)
    return real_cash


# ============================================================
# 🔹 Consulter le solde réel
# ============================================================
async def get_real_cash_balance(user_id: int, db: AsyncSession) -> float:
    result = await db.execute(select(RealCash).where(RealCash.user_id == user_id))
    real_cash = result.scalars().first()
    return float(real_cash.cash_balance) if real_cash else 0.0