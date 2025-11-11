import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# --- Import interne ---
from app.routers import methods, validator_auth, withdraw_methods
from app.routes import deposits, withdrawals, history
from app.database import engine
from app.models import Base

# --- Charger les variables d'environnement ---
load_dotenv()

# --- Créer l'application FastAPI ---
app = FastAPI(title="Wallet Deposit Backend API")

# --- Routes principales ---
app.include_router(deposits.router)
app.include_router(withdrawals.router)
app.include_router(methods.router)
app.include_router(validator_auth.router)
app.include_router(history.router)
app.include_router(withdraw_methods.router)

# --- 🌐 Configuration CORS ---
# Variable d'environnement attendue : FRONTEND_URLS="https://frontend1.com,https://frontend2.com"
frontend_urls = os.getenv("FRONTEND_URLS")

# Valeurs par défaut pour éviter les crashs si non définie
if not frontend_urls:
    print("⚠️ Avertissement : FRONTEND_URLS manquant, utilisation des valeurs par défaut.")
    origins = [
        "https://blackcoin-v5-frontend.vercel.app",
        "https://admblackcoin.vercel.app",
        "http://localhost:5173",  # utile pour test local
    ]
else:
    origins = [url.strip() for url in frontend_urls.split(",") if url.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Root endpoint ---
@app.get("/")
def root():
    return {"message": "Wallet deposit backend is running 🚀"}

# --- Initialisation de la base de données ---
async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Base de données initialisée et tables vérifiées.")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la base de données : {e}")

@app.on_event("startup")
async def on_startup():
    await init_db()

# --- Lancement du serveur ---
if __name__ == "__main__":
    port = int(os.getenv("DEPOSIT_PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
