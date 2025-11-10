# app/blackcoin_admin/backend/seed_transaction_methods.py

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.models import TransactionMethod
from app.database import AsyncSessionLocal


methods = [
    # =================== MÉTHODES DE RETRAIT ===================
    # BENIN
    {"name": "MTN Benin", "type": "withdrawal", "country": "Benin",
     "icon_url": "/icons/mtn.png", "flag_url": "/flags/benin.png", "account_number": "+2290123456789"},
    {"name": "Moov Benin", "type": "withdrawal", "country": "Benin",
     "icon_url": "/icons/moov.png", "flag_url": "/flags/benin.png", "account_number": "+2290987654321"},

    # TOGO
    {"name": "MTN Togo", "type": "withdrawal", "country": "Togo",
     "icon_url": "/icons/mtn.png", "flag_url": "/flags/togo.png", "account_number": "+2280123456789"},
    {"name": "Moov Togo", "type": "withdrawal", "country": "Togo",
     "icon_url": "/icons/moov.png", "flag_url": "/flags/togo.png", "account_number": "+2280987654321"},

    # CÔTE D’IVOIRE
    {"name": "MTN Côte d’Ivoire", "type": "withdrawal", "country": "Côte d’Ivoire",
     "icon_url": "/icons/mtn.png", "flag_url": "/flags/coteivoir.png", "account_number": "+2250123456789"},
    {"name": "Moov Côte d’Ivoire", "type": "withdrawal", "country": "Côte d’Ivoire",
     "icon_url": "/icons/moov.png", "flag_url": "/flags/coteivoir.png", "account_number": "+2250987654321"},
    {"name": "Orange Côte d’Ivoire", "type": "withdrawal", "country": "Côte d’Ivoire",
     "icon_url": "/icons/orange.png", "flag_url": "/flags/coteivoir.png", "account_number": "+2250112233445"},
    {"name": "Wave Côte d’Ivoire", "type": "withdrawal", "country": "Côte d’Ivoire",
     "icon_url": "/icons/wave.png", "flag_url": "/flags/coteivoir.png", "account_number": "+2250998877665"},

    # SÉNÉGAL
    {"name": "Orange Sénégal", "type": "withdrawal", "country": "Sénégal",
     "icon_url": "/icons/orange.png", "flag_url": "/flags/senegal.png", "account_number": "+2210123456789"},
    {"name": "Wave Sénégal", "type": "withdrawal", "country": "Sénégal",
     "icon_url": "/icons/wave.png", "flag_url": "/flags/senegal.png", "account_number": "+2210987654321"},

    # MALI
    {"name": "Orange Mali", "type": "withdrawal", "country": "Mali",
     "icon_url": "/icons/orange.png", "flag_url": "/flags/mali.png", "account_number": "+2230123456789"},
    {"name": "Wave Mali", "type": "withdrawal", "country": "Mali",
     "icon_url": "/icons/wave.png", "flag_url": "/flags/mali.png", "account_number": "+2230987654321"},

    # BURKINA-FASO
    {"name": "Moov Burkina Faso", "type": "withdrawal", "country": "Burkina-Faso",
     "icon_url": "/icons/moov.png", "flag_url": "/flags/burkina.png", "account_number": "+2260123456789"},
    {"name": "Orange Burkina Faso", "type": "withdrawal", "country": "Burkina-Faso",
     "icon_url": "/icons/orange.png", "flag_url": "/flags/burkina.png", "account_number": "+2260987654321"},
    {"name": "Wave Burkina Faso", "type": "withdrawal", "country": "Burkina-Faso",
     "icon_url": "/icons/wave.png", "flag_url": "/flags/burkina.png", "account_number": "+2260112233445"},

    # CAMEROUN
    {"name": "MTN Cameroun", "type": "withdrawal", "country": "Cameroun",
     "icon_url": "/icons/mtn.png", "flag_url": "/flags/cameroun.png", "account_number": "+2370123456789"},
    {"name": "Orange Cameroun", "type": "withdrawal", "country": "Cameroun",
     "icon_url": "/icons/orange.png", "flag_url": "/flags/cameroun.png", "account_number": "+2370987654321"},

    # =================== CRYPTO ===================
    {"name": "USDT (TRC20)", "type": "withdrawal", "country": "Global",
     "icon_url": "/icons/usdt.png", "flag_url": "/flags/crypto.png", "account_number": "0x123abc456def789"},
    {"name": "Toncoin", "type": "withdrawal", "country": "Global",
     "icon_url": "/icons/toncoin.png", "flag_url": "/flags/crypto.png", "account_number": "0x987xyz654wvu321"},
    {"name": "Pi Network", "type": "withdrawal", "country": "Global",
     "icon_url": "/icons/pi.png", "flag_url": "/flags/crypto.png", "account_number": "pi_user_example"},
]


async def seed_methods(session: AsyncSession):
    # ✅ Important : utiliser text() ici
    await session.execute(text("DELETE FROM transaction_methods WHERE type='withdrawal'"))
    await session.commit()

    for method in methods:
        session.add(TransactionMethod(**method))

    await session.commit()
    print(f"✅ {len(methods)} méthodes de retrait insérées avec succès !")


async def main():
    async with AsyncSessionLocal() as session:
        await seed_methods(session)


if __name__ == "__main__":
    asyncio.run(main())
