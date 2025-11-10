from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Deposit, Withdrawal

async def approve_deposit(db: AsyncSession, deposit_id: int):
    result = await db.execute(select(Deposit).where(Deposit.id == deposit_id))
    deposit = result.scalars().first()
    if not deposit or deposit.status != "pending":
        return False
    deposit.status = "approved"
    await db.commit()
    return True

async def reject_deposit(db: AsyncSession, deposit_id: int):
    result = await db.execute(select(Deposit).where(Deposit.id == deposit_id))
    deposit = result.scalars().first()
    if not deposit:
        return False
    deposit.status = "rejected"
    await db.commit()
    return True
