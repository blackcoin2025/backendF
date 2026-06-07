# app/lineai_admin/init_lineai_db.py

import asyncio
from app.database import lineai_engine
from app.lineai_models import LineAIBase

async def main():
    async with lineai_engine.begin() as conn:
        await conn.run_sync(LineAIBase.metadata.create_all)
    print("✅ Tables LineAI créées avec succès.")

if __name__ == "__main__":
    asyncio.run(main())