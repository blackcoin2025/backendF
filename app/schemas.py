# app/schemas.py

from pydantic import BaseModel, condecimal
from typing import Optional
from decimal import Decimal

# ============================================================
# 💰 SCHEMAS DÉPÔT
# ============================================================

class DepositCreate(BaseModel):
    user_id: int
    username: str
    phone: Optional[str] = None
    amount: Decimal                       # Compatible avec Numeric SQLAlchemy
    transaction_id: str
    method_id: int
    currency: str                         # Exemple : "BKC", "USDT"
    country: Optional[str] = None


class DepositResponse(BaseModel):
    id: int
    user_id: int
    username: str
    phone: Optional[str]
    amount: Decimal
    transaction_id: str
    currency: str
    status: str
    method_name: Optional[str] = None

    class Config:
        orm_mode = True


# ============================================================
# 💸 SCHEMAS RETRAIT
# ============================================================

class WithdrawalCreate(BaseModel):
    """
    Demande de retrait envoyée par l'utilisateur.
    - `address` : numéro de compte, mobile money, IBAN, adresse crypto, etc.
    - `amount` : montant strictement positif
    """
    user_id: int
    method_id: int
    address: str
    amount: condecimal(gt=0, max_digits=10, decimal_places=2)


class WithdrawalResponse(BaseModel):
    """
    Réponse renvoyée après création ou consultation d'un retrait.
    - `method_name` : nom convivial de la méthode de paiement
    """
    id: int
    user_id: int
    amount: Decimal
    status: str
    method_name: Optional[str] = None
    address: str

    class Config:
        orm_mode = True
