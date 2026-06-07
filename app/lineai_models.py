# app/lineai_models.py
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text,
    ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import LineAIBase
import enum

# =========================================================
# ENUMS
# =========================================================

class MatchResult(str, enum.Enum):
    v1  = "v1"   # victoire équipe domicile
    nul = "nul"
    v2  = "v2"   # victoire équipe extérieur

class ConfidenceLevel(str, enum.Enum):
    haute   = "haute"
    moyenne = "moyenne"
    faible  = "faible"

class PronosticCategory(str, enum.Enum):
    H   = "H"    # paris standards
    W   = "W"    # paris spéciaux
    RSM = "RSM"  # paris avancés

# =========================================================
# ÉQUIPES
# =========================================================

class Team(LineAIBase):
    __tablename__ = "teams"

    id         = Column(Integer, primary_key=True)
    name       = Column(String(100), nullable=False, unique=True)
    short_name = Column(String(10), nullable=True)   # ex: FCB, RMA
    logo_url   = Column(String(255), nullable=True)
    country    = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relations
    home_matches    = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches    = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")
    recent_matches  = relationship("TeamRecentMatch", back_populates="team", cascade="all, delete-orphan")

# =========================================================
# MATCH PRINCIPAL (le pronostic)
# =========================================================

class Match(LineAIBase):
    __tablename__ = "matches"

    id              = Column(Integer, primary_key=True)
    home_team_id    = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id    = Column(Integer, ForeignKey("teams.id"), nullable=False)
    competition     = Column(String(100), nullable=True)   # ex: Liga, Champions League
    match_date      = Column(DateTime, nullable=False)
    is_published    = Column(Boolean, default=False)
    created_at      = Column(DateTime, server_default=func.now())
    updated_at      = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relations
    home_team       = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team       = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    context         = relationship("MatchContext",      back_populates="match", uselist=False, cascade="all, delete-orphan")
    h2h_matches     = relationship("H2HMatch",         back_populates="match", cascade="all, delete-orphan")
    h2h_stats       = relationship("H2HStats",         back_populates="match", uselist=False, cascade="all, delete-orphan")
    team_stats      = relationship("TeamFormStats",    back_populates="match", cascade="all, delete-orphan")
    percentages     = relationship("MatchPercentages", back_populates="match", uselist=False, cascade="all, delete-orphan")
    pronostics      = relationship("Pronostic",        back_populates="match", cascade="all, delete-orphan")
    verdict         = relationship("MatchVerdict",     back_populates="match", uselist=False, cascade="all, delete-orphan")

# =========================================================
# SECTION 1 — CONTEXTE
# =========================================================

class MatchContext(LineAIBase):
    __tablename__ = "match_contexts"

    id          = Column(Integer, primary_key=True)
    match_id    = Column(Integer, ForeignKey("matches.id"), nullable=False, unique=True)
    narrative   = Column(Text, nullable=False)       # texte enjeux / ambiance
    home_form   = Column(String(10), nullable=True)  # ex: VVDNV
    away_form   = Column(String(10), nullable=True)  # ex: NVVDD
    home_absent = Column(Text, nullable=True)        # noms séparés par virgule
    away_absent = Column(Text, nullable=True)
    created_at  = Column(DateTime, server_default=func.now())

    match = relationship("Match", back_populates="context")

# =========================================================
# SECTION 2 — HISTORIQUE H2H (5 dernières confrontations)
# =========================================================

class H2HMatch(LineAIBase):
    __tablename__ = "h2h_matches"

    id           = Column(Integer, primary_key=True)
    match_id     = Column(Integer, ForeignKey("matches.id"), nullable=False)
    played_at    = Column(DateTime, nullable=False)
    competition  = Column(String(100), nullable=True)
    home_team    = Column(String(100), nullable=False)
    away_team    = Column(String(100), nullable=False)
    home_score   = Column(Integer, nullable=False)
    away_score   = Column(Integer, nullable=False)
    result       = Column(SAEnum(MatchResult), nullable=False)
    display_order = Column(Integer, default=0)       # 1 = plus récent

    match = relationship("Match", back_populates="h2h_matches")

# =========================================================
# SECTION 2 — FORME RÉCENTE (6 derniers matchs par équipe)
# =========================================================

class TeamRecentMatch(LineAIBase):
    __tablename__ = "team_recent_matches"

    id            = Column(Integer, primary_key=True)
    team_id       = Column(Integer, ForeignKey("teams.id"), nullable=False)
    match_id      = Column(Integer, ForeignKey("matches.id"), nullable=False)
    played_at     = Column(DateTime, nullable=False)
    competition   = Column(String(100), nullable=True)
    opponent      = Column(String(100), nullable=False)
    home_or_away  = Column(String(4), nullable=False)   # "home" | "away"
    goals_for     = Column(Integer, nullable=False)
    goals_against = Column(Integer, nullable=False)
    result        = Column(SAEnum(MatchResult), nullable=False)
    display_order = Column(Integer, default=0)

    team  = relationship("Team", back_populates="recent_matches")
    match = relationship("Match")

# =========================================================
# SECTION 3 — STATS H2H (moyennes sur les 5 confrontations)
# =========================================================

class H2HStats(LineAIBase):
    __tablename__ = "h2h_stats"

    id              = Column(Integer, primary_key=True)
    match_id        = Column(Integer, ForeignKey("matches.id"), nullable=False, unique=True)

    # Possession
    home_possession = Column(Float, nullable=True)
    away_possession = Column(Float, nullable=True)

    # Tirs
    home_shots      = Column(Float, nullable=True)
    away_shots      = Column(Float, nullable=True)
    home_shots_on   = Column(Float, nullable=True)   # tirs cadrés
    away_shots_on   = Column(Float, nullable=True)

    # Buts
    home_goals      = Column(Float, nullable=True)
    away_goals      = Column(Float, nullable=True)

    # Discipline
    home_yellow     = Column(Float, nullable=True)
    away_yellow     = Column(Float, nullable=True)
    home_red        = Column(Float, nullable=True)
    away_red        = Column(Float, nullable=True)

    # Divers
    home_corners    = Column(Float, nullable=True)
    away_corners    = Column(Float, nullable=True)
    home_fouls      = Column(Float, nullable=True)
    away_fouls      = Column(Float, nullable=True)
    home_offsides   = Column(Float, nullable=True)
    away_offsides   = Column(Float, nullable=True)

    match = relationship("Match", back_populates="h2h_stats")

# =========================================================
# SECTION 3 — STATS FORME (moyennes 6 derniers matchs / équipe)
# =========================================================

class TeamFormStats(LineAIBase):
    __tablename__ = "team_form_stats"

    id              = Column(Integer, primary_key=True)
    match_id        = Column(Integer, ForeignKey("matches.id"), nullable=False)
    team_id         = Column(Integer, ForeignKey("teams.id"), nullable=False)

    possession      = Column(Float, nullable=True)
    shots           = Column(Float, nullable=True)
    shots_on        = Column(Float, nullable=True)
    goals_scored    = Column(Float, nullable=True)
    goals_conceded  = Column(Float, nullable=True)
    yellow_cards    = Column(Float, nullable=True)
    red_cards       = Column(Float, nullable=True)
    corners         = Column(Float, nullable=True)
    fouls           = Column(Float, nullable=True)
    offsides        = Column(Float, nullable=True)
    touches         = Column(Float, nullable=True)
    saves           = Column(Float, nullable=True)   # arrêts du gardien

    match = relationship("Match", back_populates="team_stats")
    team  = relationship("Team")

# =========================================================
# SECTION 4 — POURCENTAGES ÉVÉNEMENTS
# =========================================================

class MatchPercentages(LineAIBase):
    __tablename__ = "match_percentages"

    id              = Column(Integer, primary_key=True)
    match_id        = Column(Integer, ForeignKey("matches.id"), nullable=False, unique=True)

    # Résultat
    pct_home_win    = Column(Float, nullable=True)   # ex: 70
    pct_draw        = Column(Float, nullable=True)   # ex: 8
    pct_away_win    = Column(Float, nullable=True)   # ex: 30
    pct_v1_or_v2   = Column(Float, nullable=True)   # ex: 80

    # Buts
    pct_over_1_5    = Column(Float, nullable=True)
    pct_over_2_5    = Column(Float, nullable=True)
    pct_over_3_5    = Column(Float, nullable=True)
    pct_over_4_5    = Column(Float, nullable=True)

    # Événements (seuil = valeur affichée, pct = proba de dépasser)
    possession_home     = Column(Float, nullable=True)   # % possession v1
    fouls_threshold     = Column(Float, nullable=True)   # ex: 18.5
    fouls_pct           = Column(Float, nullable=True)
    corners_threshold   = Column(Float, nullable=True)
    corners_pct         = Column(Float, nullable=True)
    shots_on_threshold  = Column(Float, nullable=True)
    shots_on_pct        = Column(Float, nullable=True)
    cards_threshold     = Column(Float, nullable=True)
    cards_pct           = Column(Float, nullable=True)
    touches_threshold   = Column(Float, nullable=True)
    touches_pct         = Column(Float, nullable=True)
    shots_threshold     = Column(Float, nullable=True)
    shots_pct           = Column(Float, nullable=True)
    offsides_threshold  = Column(Float, nullable=True)
    offsides_pct        = Column(Float, nullable=True)

    match = relationship("Match", back_populates="percentages")

# =========================================================
# SECTION 5 — PRONOSTICS H / W / RSM
# =========================================================

class Pronostic(LineAIBase):
    __tablename__ = "pronostics"

    id          = Column(Integer, primary_key=True)
    match_id    = Column(Integer, ForeignKey("matches.id"), nullable=False)
    category    = Column(SAEnum(PronosticCategory), nullable=False)   # H | W | RSM
    code        = Column(String(10), nullable=False)   # ex: H1, W2, RSM1
    label       = Column(String(255), nullable=False)  # ex: v1 moins de 19.5 touches
    is_active   = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)

    match = relationship("Match", back_populates="pronostics")

# =========================================================
# SECTION 6 — VERDICT FINAL
# =========================================================

class MatchVerdict(LineAIBase):
    __tablename__ = "match_verdicts"

    id              = Column(Integer, primary_key=True)
    match_id        = Column(Integer, ForeignKey("matches.id"), nullable=False, unique=True)
    predicted_score = Column(String(10), nullable=True)    # ex: 2-1
    summary         = Column(Text, nullable=False)
    confidence      = Column(SAEnum(ConfidenceLevel), nullable=False)
    created_at      = Column(DateTime, server_default=func.now())

    match = relationship("Match", back_populates="verdict")