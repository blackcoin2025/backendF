import os
import pyotp
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/validator", tags=["Validator Auth"])

# === Données de référence depuis .env ===
VALIDATOR_EMAIL = os.getenv("VALIDATOR_EMAIL")
VALIDATOR_PASSWORD = os.getenv("VALIDATOR_PASSWORD")
VALIDATOR_TELEGRAM_USERNAME = os.getenv("VALIDATOR_TELEGRAM_USERNAME")
VALIDATOR_GOOGLE_SECRET = os.getenv("VALIDATOR_GOOGLE_SECRET")

# --- Schémas de données ---
class ValidatorLogin(BaseModel):
    email: str
    password: str
    telegram_username: str

class OTPVerify(BaseModel):
    email: str
    code: str


# --- Étape 1 : Vérification des identifiants ---
@router.post("/login")
async def validator_login(data: ValidatorLogin):
    """
    Vérifie les identifiants du validateur.
    Si tout est correct, demande le code Google Authenticator.
    """
    if (
        data.email != VALIDATOR_EMAIL
        or data.password != VALIDATOR_PASSWORD
        or data.telegram_username.lower() != VALIDATOR_TELEGRAM_USERNAME.lower()
    ):
        raise HTTPException(status_code=401, detail="Identifiants invalides.")

    return {"message": "Identifiants valides. Veuillez entrer le code Google Authenticator."}


# --- Étape 2 : Vérification du code Google Authenticator ---
@router.post("/verify-otp")
async def verify_otp(data: OTPVerify):
    """
    Vérifie le code fourni via Google Authenticator.
    """
    if data.email != VALIDATOR_EMAIL:
        raise HTTPException(status_code=401, detail="Email invalide.")

    totp = pyotp.TOTP(VALIDATOR_GOOGLE_SECRET)

    if totp.verify(data.code):
        return {"message": "Connexion validée ✅"}
    else:
        raise HTTPException(status_code=400, detail="Code invalide ou expiré.")
