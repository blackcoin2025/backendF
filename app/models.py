from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, Boolean, Date, ForeignKey, Float
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

# ===============================
# Utilisateurs
# ===============================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birth_date = Column(Date, nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(30), unique=True, index=True, nullable=False)
    avatar_url = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    has_completed_welcome_tasks = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relations
    deposits = relationship("Deposit", back_populates="user", cascade="all, delete-orphan")
    withdrawals = relationship("Withdrawal", back_populates="user", cascade="all, delete-orphan")
    wallet = relationship("Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    history = relationship("TransactionHistory", back_populates="user", cascade="all, delete-orphan")
    packs = relationship("UserPack", back_populates="user", cascade="all, delete-orphan")  # ✅ ajout

# ===============================
# Méthodes de transaction
# ===============================
class TransactionMethod(Base):
    __tablename__ = "transaction_methods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    type = Column(String, nullable=False)
    country = Column(String, nullable=True)
    icon_url = Column(String, nullable=True)
    flag_url = Column(String, nullable=True)
    account_number = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    deposits = relationship("Deposit", back_populates="transaction_method")
    withdrawals = relationship("Withdrawal", back_populates="transaction_method")
    history = relationship("TransactionHistory", back_populates="transaction_method")

# ===============================
# Packs utilisateurs
# ===============================
class UserPack(Base):
    __tablename__ = "user_packs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pack_id = Column(Integer, nullable=True)  # 🔹 en attendant le modèle Action
    start_date = Column(DateTime, default=func.now())
    last_claim_date = Column(DateTime, nullable=True)
    daily_earnings = Column(Float, default=0)
    is_unlocked = Column(Boolean, default=False)
    total_earned = Column(Float, default=0)
    current_day = Column(Date, default=func.current_date())
    all_tasks_completed = Column(Boolean, default=False)
    pack_status = Column(String(50), default="payé")

    user = relationship("User", back_populates="packs")
    # pack = relationship("Action", back_populates="user_packs")  # ⚠️ commenter si Action n'existe pas
    # tasks = relationship("UserDailyTask", back_populates="user_pack", cascade="all, delete-orphan")

# ===============================
# Dépôts utilisateurs
# ===============================
class Deposit(Base):
    __tablename__ = "deposits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    method_id = Column(Integer, ForeignKey("transaction_methods.id", ondelete="SET NULL"), index=True)
    username = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    transaction_id = Column(String, nullable=False, unique=True, index=True)
    country = Column(String, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, default="FCFA")
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="deposits")
    transaction_method = relationship("TransactionMethod", back_populates="deposits")

# ===============================
# Retraits utilisateurs
# ===============================
class Withdrawal(Base):
    __tablename__ = "withdrawals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    method_id = Column(Integer, ForeignKey("transaction_methods.id", ondelete="SET NULL"), index=True)
    address = Column(String, nullable=False)  # ✅ champ unique pour crypto, compte bancaire ou autre
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="withdrawals")
    transaction_method = relationship("TransactionMethod", back_populates="withdrawals")

# ===============================
# Wallet utilisateur
# ===============================
class Wallet(Base):
    __tablename__ = "wallet"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="wallet")

# ===============================
# Historique des transactions
# ===============================
class TransactionHistory(Base):
    __tablename__ = "transaction_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    method_id = Column(Integer, ForeignKey("transaction_methods.id", ondelete="SET NULL"), nullable=True)
    username = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    transaction_id = Column(String, nullable=False, index=True)
    country = Column(String, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="history")
    transaction_method = relationship("TransactionMethod", back_populates="history")
