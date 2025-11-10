from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Withdrawal, TransactionMethod, User, TransactionHistory, UserPack, Wallet
from app.database import get_db
from app.schemas import WithdrawalCreate, WithdrawalResponse
from app.services.wallet_service import remove_wallet_points

router = APIRouter(prefix="/withdrawals", tags=["Withdrawals"])


# ============================================================
# 🔹 Créer une demande de retrait
# ============================================================
@router.post("/", response_model=WithdrawalResponse, status_code=status.HTTP_201_CREATED)
async def create_withdrawal(data: WithdrawalCreate, db: AsyncSession = Depends(get_db)):

    user = await db.get(User, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    method = await db.get(TransactionMethod, data.method_id)
    if not method or method.type != "withdrawal":
        raise HTTPException(status_code=400, detail="Méthode de retrait invalide")

    wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == user.id))
    wallet = wallet_result.scalars().first()

    if not wallet or wallet.amount < data.amount:
        raise HTTPException(status_code=400, detail="Fonds insuffisants")

    pack_result = await db.execute(select(UserPack).where(UserPack.user_id == user.id))
    pack = pack_result.scalars().first()
    if not pack:
        raise HTTPException(status_code=400, detail="Aucun pack actif trouvé pour cet utilisateur")

    withdrawal = Withdrawal(
        user_id=user.id,
        method_id=method.id,
        address=data.address,      # ✅ unique champ fourni par l’utilisateur
        amount=data.amount,
        status="pending"
    )

    db.add(withdrawal)
    await db.commit()
    await db.refresh(withdrawal)

    return WithdrawalResponse(
        id=withdrawal.id,
        user_id=user.id,
        amount=withdrawal.amount,
        status=withdrawal.status,
        method_name=method.name,
        address=withdrawal.address
    )


# ============================================================
# 🔹 Lister toutes les demandes de retrait
# ============================================================
@router.get("/", response_model=list[WithdrawalResponse])
async def list_withdrawals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Withdrawal).order_by(Withdrawal.created_at.desc()))
    withdrawals = result.scalars().all()

    response_data = []
    for w in withdrawals:
        method = await db.get(TransactionMethod, w.method_id)

        response_data.append(
            WithdrawalResponse(
                id=w.id,
                user_id=w.user_id,
                amount=w.amount,
                status=w.status,
                method_name=method.name if method else None,
                address=w.address
            )
        )

    return response_data


# ============================================================
# 🔹 Valider un retrait
# ============================================================
@router.post("/{withdrawal_id}/validate")
async def validate_withdrawal(withdrawal_id: int, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Withdrawal).where(Withdrawal.id == withdrawal_id))
    withdrawal = result.scalars().first()

    if not withdrawal:
        raise HTTPException(status_code=404, detail="Retrait introuvable")

    if withdrawal.status != "pending":
        raise HTTPException(status_code=400, detail="Ce retrait a déjà été traité")

    user = await db.get(User, withdrawal.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    await remove_wallet_points(user, withdrawal.amount, db)

    history_entry = TransactionHistory(
        user_id=user.id,
        method_id=withdrawal.method_id,
        username=user.username,
        phone=user.phone,
        transaction_id=f"WDR-{withdrawal.id}",
        amount=withdrawal.amount,
        status="approved"
    )
    db.add(history_entry)

    withdrawal.status = "approved"

    await db.commit()
    await db.refresh(withdrawal)

    return {
        "message": "Retrait validé, wallet débité et historique mis à jour",
        "withdrawal_id": withdrawal.id
    }


# ============================================================
# 🔹 Rejeter un retrait
# ============================================================
@router.post("/{withdrawal_id}/reject")
async def reject_withdrawal(withdrawal_id: int, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Withdrawal).where(Withdrawal.id == withdrawal_id))
    withdrawal = result.scalars().first()

    if not withdrawal:
        raise HTTPException(status_code=404, detail="Retrait introuvable")

    if withdrawal.status != "pending":
        raise HTTPException(status_code=400, detail="Ce retrait a déjà été traité")

    history_entry = TransactionHistory(
        user_id=withdrawal.user_id,
        method_id=withdrawal.method_id,
        username=None,
        phone=None,
        transaction_id=f"WDR-{withdrawal.id}",
        amount=withdrawal.amount,
        status="rejected"
    )
    db.add(history_entry)

    withdrawal.status = "rejected"

    await db.commit()
    await db.refresh(withdrawal)

    return {
        "message": "Retrait rejeté et historique mis à jour",
        "withdrawal_id": withdrawal.id
    }
