from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Wallet


# ============================================================
# 🔹 Ajouter des fonds au wallet
# ============================================================
async def add_wallet_points(user, amount: int, db: AsyncSession):
    """Ajoute des points au wallet de l'utilisateur."""
    result = await db.execute(select(Wallet).where(Wallet.user_id == user.id))
    wallet = result.scalars().first()

    if wallet:
        wallet.amount += amount
    else:
        wallet = Wallet(user_id=user.id, amount=amount)
        db.add(wallet)

    await db.commit()
    await db.refresh(wallet)
    return wallet


# ============================================================
# 🔹 Retirer des fonds du wallet
# ============================================================
async def remove_wallet_points(user, amount: int, db: AsyncSession):
    """Retire des points du wallet de l'utilisateur (utilisé pour les retraits)."""
    result = await db.execute(select(Wallet).where(Wallet.user_id == user.id))
    wallet = result.scalars().first()

    if not wallet or wallet.amount < amount:
        raise HTTPException(status_code=400, detail="Fonds insuffisants dans le wallet")

    wallet.amount -= amount
    await db.commit()
    await db.refresh(wallet)
    return wallet


# ============================================================
# 🔹 Consulter le solde
# ============================================================
async def get_wallet_balance(user, db: AsyncSession):
    """Récupère le solde actuel du wallet."""
    result = await db.execute(select(Wallet).where(Wallet.user_id == user.id))
    wallet = result.scalars().first()
    return wallet.amount if wallet else 0
