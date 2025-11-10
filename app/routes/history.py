from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Deposit, TransactionMethod
import locale

# 🇫🇷 Forcer le format français pour la date
try:
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except:
    # En cas d'erreur sur Windows (où fr_FR.UTF-8 peut ne pas exister)
    pass

router = APIRouter(prefix="/history", tags=["History"])

@router.get("/{user_id}")
async def get_user_history(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retourne l’historique des dépôts validés ou rejetés pour un utilisateur,
    avec la date formatée en français lisible.
    """
    result = await db.execute(
        select(Deposit)
        .where(Deposit.user_id == user_id, Deposit.status.in_(["approved", "rejected"]))
        .order_by(Deposit.created_at.desc())
    )
    deposits = result.scalars().all()

    history = []
    for dep in deposits:
        method = await db.get(TransactionMethod, dep.method_id)
        formatted_date = (
            dep.created_at.strftime("%d %B %Y à %Hh%M")
            if dep.created_at else None
        )
        history.append({
            "id": dep.id,
            "method_name": method.name if method else "Inconnue",
            "amount": float(dep.amount),
            "status": dep.status,
            "date": formatted_date
        })

    return history
