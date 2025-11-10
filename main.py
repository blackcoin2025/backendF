import os
from fastapi import FastAPI
from app.routers import methods, validator_auth
from app.routes import deposits, withdrawals
from app.routes import history
from fastapi.middleware.cors import CORSMiddleware
from app.routers import withdraw_methods
from dotenv import load_dotenv
from app.database import engine
from app.models import Base
import uvicorn

load_dotenv()

app = FastAPI(title="Wallet Deposit Backend API")

# 🔀 Inclure les routes (⚠️ Ne pas redéfinir les préfixes si déjà dans les fichiers)
app.include_router(deposits.router)
app.include_router(withdrawals.router)
app.include_router(methods.router)
app.include_router(validator_auth.router)
app.include_router(history.router)
app.include_router(withdraw_methods.router)

# 🌐 CORS
FRONTEND_URLS = os.getenv("FRONTEND_URLS")

if not FRONTEND_URLS:
    raise RuntimeError("❌ FRONTEND_URLS manquant dans le fichier .env")

# On découpe la chaîne en liste (séparée par des virgules)
origins = [url.strip() for url in FRONTEND_URLS.split(",") if url.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Wallet deposit backend is running 🚀"}

# 🔧 Init DB
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Base de données initialisée et tables vérifiées.")

@app.on_event("startup")
async def on_startup():
    await init_db()

if __name__ == "__main__":
    port = int(os.getenv("DEPOSIT_PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
