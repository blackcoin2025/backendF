# app/blackcoin_admin/backend/seed_transaction_methods.py

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.models import TransactionMethod
from app.database import AsyncSessionLocal


methods = [
    # =================== MÉTHODES DE RETRAIT ===================
    # BENIN
    {
        "name": "MTN Benin", "type": "withdrawal", "country": "Benin",
        "icon_url": "/icons/mtn.png", "flag_url": "/flags/benin.png",
        "account_number": "+2290154303209"   # ✔️ NEW
    },
    {
        "name": "Moov Benin", "type": "withdrawal", "country": "Benin",
        "icon_url": "/icons/moov.png", "flag_url": "/flags/benin.png",
        "account_number": "+2290198914729"   # ✔️ NEW
    },

    # TOGO
    {
        "name": "MTN Togo", "type": "withdrawal", "country": "Togo",
        "icon_url": "/icons/mtn.png", "flag_url": "/flags/togo.png",
        "account_number": "indisponible"
    },
    {
        "name": "Moov Togo", "type": "withdrawal", "country": "Togo",
        "icon_url": "/icons/moov.png", "flag_url": "/flags/togo.png",
        "account_number": "indisponible"
    },

    # CÔTE D'IVOIRE
    {
        "name": "MTN Côte d’Ivoire", "type": "withdrawal", "country": "Côte d’Ivoire",
        "icon_url": "/icons/mtn.png", "flag_url": "/flags/coteivoir.png",
        "account_number": "+2250504446348"
    },
    {
        "name": "Moov Côte d’Ivoire", "type": "withdrawal", "country": "Côte d’Ivoire",
        "icon_url": "/icons/moov.png", "flag_url": "/flags/coteivoir.png",
        "account_number": "indisponible"
    },
    {
        "name": "Orange Côte d’Ivoire", "type": "withdrawal", "country": "Côte d’Ivoire",
        "icon_url": "/icons/orange.png", "flag_url": "/flags/coteivoir.png",
        "account_number": "indisponible"
    },
    {
        "name": "Wave Côte d’Ivoire", "type": "withdrawal", "country": "Côte d’Ivoire",
        "icon_url": "/icons/wave.png", "flag_url": "/flags/coteivoir.png",
        "account_number": "indisponible"
    },

    # SÉNÉGAL
    {
        "name": "Orange Sénégal", "type": "withdrawal", "country": "Sénégal",
        "icon_url": "/icons/orange.png", "flag_url": "/flags/senegal.png",
        "account_number": "indisponible"
    },
    {
        "name": "Wave Sénégal", "type": "withdrawal", "country": "Sénégal",
        "icon_url": "/icons/wave.png", "flag_url": "/flags/senegal.png",
        "account_number": "indisponible"
    },

    # MALI
    {
        "name": "Orange Mali", "type": "withdrawal", "country": "Mali",
        "icon_url": "/icons/orange.png", "flag_url": "/flags/mali.png",
        "account_number": "indisponible"
    },
    {
        "name": "Wave Mali", "type": "withdrawal", "country": "Mali",
        "icon_url": "/icons/wave.png", "flag_url": "/flags/mali.png",
        "account_number": "indisponible"
    },

    # BURKINA-FASO
    {
        "name": "Moov Burkina Faso", "type": "withdrawal", "country": "Burkina-Faso",
        "icon_url": "/icons/moov.png", "flag_url": "/flags/burkina.png",
        "account_number": "indisponible"
    },
    {
        "name": "Orange Burkina Faso", "type": "withdrawal", "country": "Burkina-Faso",
        "icon_url": "/icons/orange.png", "flag_url": "/flags/burkina.png",
        "account_number": "indisponible"
    },
    {
        "name": "Wave Burkina Faso", "type": "withdrawal", "country": "Burkina-Faso",
        "icon_url": "/icons/wave.png", "flag_url": "/flags/burkina.png",
        "account_number": "indisponible"
    },

    # CAMEROUN
    {
        "name": "MTN Cameroun", "type": "withdrawal", "country": "Cameroun",
        "icon_url": "/icons/mtn.png", "flag_url": "/flags/cameroun.png",
        "account_number": "indisponible"
    },
    {
        "name": "Orange Cameroun", "type": "withdrawal", "country": "Cameroun",
        "icon_url": "/icons/orange.png", "flag_url": "/flags/cameroun.png",
        "account_number": "indisponible"
    },

    # =================== CRYPTO ===================
    {
        "name": "USDT (TON)", "type": "withdrawal", "country": "Global",
        "icon_url": "/icons/usdt.png", "flag_url": "/flags/ton.png",
        "account_number": "UQDMG-EZe_7WQa_qKLv5PBIApFTx7aEjkfx6M3-zRUkPa4a0"
    },
    {
        "name": "Toncoin (TON)", "type": "withdrawal", "country": "Global",
        "icon_url": "/icons/toncoin.png", "flag_url": "/flags/ton.png",
        "account_number": "UQDMG-EZe_7WQa_qKLv5PBIApFTx7aEjkfx6M3-zRUkPa4a0"
    },
    {
        "name": "Pi Network", "type": "withdrawal", "country": "Global",
        "icon_url": "/icons/pi.png", "flag_url": "/flags/pi.png",
        "account_number": "GDPH5ZJWVEH5RR3MCDXNCP7SUJ66KYISPGZJA6HKGIWZZBPVPTWQSJOE"
    },
]


async def seed_methods(session: AsyncSession):
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
