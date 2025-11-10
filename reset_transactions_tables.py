import asyncio
from app.database import engine
from app.models import Base, TransactionMethod, Deposit, Withdrawal

async def reset_transactions_tables():
    print("⚠️  ATTENTION : Cette opération va SUPPRIMER les tables de transactions uniquement.")
    confirm = input("Es-tu sûr de vouloir continuer ? (oui/non) : ").strip().lower()
    if confirm not in ["oui", "o", "yes", "y"]:
        print("❌ Opération annulée.")
        return

    print("🔄 Réinitialisation des tables de transactions en cours...")

    async with engine.begin() as conn:
        # Supprime uniquement les tables spécifiques
        await conn.run_sync(TransactionMethod.__table__.drop, checkfirst=True)
        await conn.run_sync(Deposit.__table__.drop, checkfirst=True)
        await conn.run_sync(Withdrawal.__table__.drop, checkfirst=True)

        # Recrée uniquement ces tables
        await conn.run_sync(TransactionMethod.__table__.create)
        await conn.run_sync(Deposit.__table__.create)
        await conn.run_sync(Withdrawal.__table__.create)

    print("✅ Tables de transactions réinitialisées avec succès !")

if __name__ == "__main__":
    asyncio.run(reset_transactions_tables())
