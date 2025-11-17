from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Deposit, TransactionMethod, User, TransactionHistory
from app.schemas import DepositCreate, DepositResponse
from app.database import get_db
from app.services.wallet_service import add_wallet_points

router = APIRouter(prefix="/deposits", tags=["Deposits"])


# ============================================================
# 🔹 Créer un dépôt
# ============================================================
@router.post("/", response_model=DepositResponse, status_code=status.HTTP_201_CREATED)
async def create_deposit(data: DepositCreate, db: AsyncSession = Depends(get_db)):
    method_result = await db.execute(select(TransactionMethod).where(TransactionMethod.id == data.method_id))
    method = method_result.scalars().first()
    if not method:
        raise HTTPException(status_code=404, detail="Méthode de transaction introuvable")

    user_result = await db.execute(select(User).where(User.id == data.user_id))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    existing_tx = await db.execute(select(Deposit).where(Deposit.transaction_id == data.transaction_id))
    if existing_tx.scalars().first():
        raise HTTPException(status_code=400, detail="Cet ID de transaction existe déjà")

    deposit = Deposit(
        user_id=data.user_id,
        username=data.username,
        phone=data.phone,
        amount=data.amount,
        transaction_id=data.transaction_id,
        method_id=data.method_id,
        status="pending",
        country=data.country,
        currency=data.currency,     # <--- OBLIGATOIRE
    )

    db.add(deposit)
    await db.commit()
    await db.refresh(deposit)

    return DepositResponse(
        id=deposit.id,
        user_id=deposit.user_id,
        username=deposit.username,
        phone=deposit.phone,
        amount=deposit.amount,
        transaction_id=deposit.transaction_id,
        status=deposit.status,
        method_name=method.name,
        currency=data.currency,     # <--- OBLIGATOIRE
    )


# ============================================================
# 🔹 Lister tous les dépôts
# ============================================================
@router.get("/", response_model=list[DepositResponse])
async def list_deposits(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deposit).order_by(Deposit.created_at.desc()))
    deposits = result.scalars().all()

    deposits_with_method = []
    for deposit in deposits:
        method = await db.get(TransactionMethod, deposit.method_id)
        deposits_with_method.append(
            DepositResponse(
                id=deposit.id,
                user_id=deposit.user_id,
                username=deposit.username,
                phone=deposit.phone,
                amount=deposit.amount,
                transaction_id=deposit.transaction_id,
                status=deposit.status,
                method_name=method.name if method else None,
                currency=deposit.currency  # <-- ajouté ici !
            )
        )
    return deposits_with_method


# ============================================================
# 🔹 Valider un dépôt
# ============================================================
@router.post("/{deposit_id}/validate")
async def validate_deposit(deposit_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deposit).where(Deposit.id == deposit_id))
    deposit = result.scalars().first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Dépôt introuvable")
    if deposit.status != "pending":
        raise HTTPException(status_code=400, detail="Ce dépôt a déjà été traité")

    user = await db.get(User, deposit.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # Ajoute le montant au wallet
    await add_wallet_points(user, deposit.amount, db)

    # Crée l'entrée dans l'historique
    history_entry = TransactionHistory(
        user_id=deposit.user_id,
        method_id=deposit.method_id,
        username=deposit.username,
        phone=deposit.phone,
        transaction_id=deposit.transaction_id,
        country=deposit.country,
        amount=deposit.amount,
        status="approved"
    )
    db.add(history_entry)

    # Met à jour le statut du dépôt
    deposit.status = "approved"
    await db.commit()
    await db.refresh(deposit)

    return {
        "message": "✅ Dépôt validé, wallet crédité et historique mis à jour",
        "deposit_id": deposit.id,
        "amount": deposit.amount,
    }


# ============================================================
# 🔹 Rejeter un dépôt
# ============================================================
@router.post("/{deposit_id}/reject")
async def reject_deposit(deposit_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deposit).where(Deposit.id == deposit_id))
    deposit = result.scalars().first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Dépôt introuvable")
    if deposit.status != "pending":
        raise HTTPException(status_code=400, detail="Ce dépôt a déjà été traité")

    # Crée l'entrée dans l'historique avec status rejeté
    history_entry = TransactionHistory(
        user_id=deposit.user_id,
        method_id=deposit.method_id,
        username=deposit.username,
        phone=deposit.phone,
        transaction_id=deposit.transaction_id,
        country=deposit.country,
        amount=deposit.amount,
        status="rejected"
    )
    db.add(history_entry)

    # Met à jour le statut du dépôt
    deposit.status = "rejected"
    await db.commit()
    await db.refresh(deposit)

    return {"message": "🚫 Dépôt rejeté et historique mis à jour", "deposit_id": deposit.id}
