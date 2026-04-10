from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import (
    Withdrawal,
    TransactionMethod,
    User,
    TransactionHistory,
    UserPack,
    RealCash
)
from app.database import get_db
from app.schemas import WithdrawalCreate, WithdrawalResponse
from app.services.real_cash_service import remove_real_cash

router = APIRouter(prefix="/withdrawals", tags=["Withdrawals"])


# ============================================================
# 🔹 Créer une demande de retrait
# ============================================================
@router.post("/", response_model=WithdrawalResponse, status_code=status.HTTP_201_CREATED)
async def create_withdrawal(
    data: WithdrawalCreate,
    db: AsyncSession = Depends(get_db)
):
    # ---- Vérifie utilisateur
    user = await db.get(User, data.user_id)
    if not user:
        raise HTTPException(404, "Utilisateur introuvable")

    # ---- Vérifie méthode
    method = await db.get(TransactionMethod, data.method_id)
    if not method or method.type != "withdrawal":
        raise HTTPException(400, "Méthode de retrait invalide")

    # ---- Vérifie solde réel
    result = await db.execute(
        select(RealCash).where(RealCash.user_id == user.id)
    )
    real_cash = result.scalars().first()

    if not real_cash or real_cash.cash_balance < data.amount:
        raise HTTPException(400, "Fonds insuffisants dans le compte réel")

    # ---- Vérifie pack actif
    pack_result = await db.execute(
        select(UserPack).where(UserPack.user_id == user.id)
    )
    pack = pack_result.scalars().first()

    if not pack:
        raise HTTPException(400, "Aucun pack actif trouvé pour cet utilisateur")

    # ---- Création retrait
    withdrawal = Withdrawal(
        user_id=user.id,
        method_id=method.id,
        address=data.address,
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
# 🔹 Lister les retraits
# ============================================================
@router.get("/", response_model=list[WithdrawalResponse])
async def list_withdrawals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Withdrawal).order_by(Withdrawal.created_at.desc())
    )
    withdrawals = result.scalars().all()

    response = []

    for w in withdrawals:
        method = await db.get(TransactionMethod, w.method_id)

        response.append(
            WithdrawalResponse(
                id=w.id,
                user_id=w.user_id,
                amount=w.amount,
                status=w.status,
                method_name=method.name if method else None,
                address=w.address
            )
        )

    return response


# ============================================================
# 🔹 Valider un retrait
# ============================================================
@router.post("/{withdrawal_id}/validate")
async def validate_withdrawal(
    withdrawal_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Withdrawal).where(Withdrawal.id == withdrawal_id)
    )
    withdrawal = result.scalars().first()

    if not withdrawal:
        raise HTTPException(404, "Retrait introuvable")

    if withdrawal.status != "pending":
        raise HTTPException(400, "Retrait déjà traité")

    user = await db.get(User, withdrawal.user_id)
    if not user:
        raise HTTPException(404, "Utilisateur introuvable")

    # ✅ Débit réel (CORRIGÉ)
    await remove_real_cash(user.id, withdrawal.amount, db)

    # ---- Historique
    history = TransactionHistory(
        user_id=user.id,
        method_id=withdrawal.method_id,
        username=user.username,
        phone=user.phone,
        transaction_id=f"WDR-{withdrawal.id}",
        amount=withdrawal.amount,
        status="approved"
    )

    db.add(history)

    withdrawal.status = "approved"

    await db.commit()
    await db.refresh(withdrawal)

    return {
        "message": "Retrait validé et solde débité",
        "withdrawal_id": withdrawal.id
    }


# ============================================================
# 🔹 Rejeter un retrait
# ============================================================
@router.post("/{withdrawal_id}/reject")
async def reject_withdrawal(
    withdrawal_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Withdrawal).where(Withdrawal.id == withdrawal_id)
    )
    withdrawal = result.scalars().first()

    if not withdrawal:
        raise HTTPException(404, "Retrait introuvable")

    if withdrawal.status != "pending":
        raise HTTPException(400, "Retrait déjà traité")

    history = TransactionHistory(
        user_id=withdrawal.user_id,
        method_id=withdrawal.method_id,
        username=None,
        phone=None,
        transaction_id=f"WDR-{withdrawal.id}",
        amount=withdrawal.amount,
        status="rejected"
    )

    db.add(history)

    withdrawal.status = "rejected"

    await db.commit()
    await db.refresh(withdrawal)

    return {
        "message": "Retrait rejeté",
        "withdrawal_id": withdrawal.id
    }
