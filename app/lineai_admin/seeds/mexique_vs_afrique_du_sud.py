# app/lineai_admin/seeds/mexique_vs_afrique_du_sud.py

import asyncio
from datetime import datetime
from sqlalchemy import select
from app.lineai_models import (
    Team, Match, MatchContext, H2HMatch, TeamRecentMatch,
    H2HStats, TeamFormStats, MatchPercentages, Pronostic, MatchVerdict,
    MatchResult, ConfidenceLevel, PronosticCategory,
)
from app.database import LineAISessionLocal


# =========================================================
# DONNÉES
# =========================================================

MATCH_DATE = datetime(2026, 6, 22, 20, 0)  # à ajuster
COMPETITION = "FIFA Coupe du Monde 2026"

CONTEXT = {
    "narrative": (
        "Le Mexique lance sa Coupe du Monde à domicile dans un match très important contre "
        "l'Afrique du Sud. Jouer au Stade Azteca donne un avantage psychologique énorme aux "
        "Mexicains, poussés par leur public et habitués à l'altitude. "
        "L'Afrique du Sud arrive avec moins de pression mais possède une équipe physique et "
        "disciplinée capable de gêner les transitions adverses. "
        "Le Mexique montre une meilleure stabilité récente défensive tandis que l'Afrique du Sud "
        "alterne entre bonnes performances offensives et erreurs défensives."
    ),
    "home_form":   "VVVNNV",
    "away_form":   "DNDVDV",
    "home_absent": "Aucun absent majeur confirmé",
    "away_absent": "Aucun absent majeur confirmé",
}

H2H_MATCHES = [
    {"home_team": "Afrique du Sud", "away_team": "Mexique",       "home_score": 1, "away_score": 1, "result": MatchResult.nul, "display_order": 1},
    {"home_team": "Mexique",        "away_team": "Afrique du Sud", "home_score": 4, "away_score": 0, "result": MatchResult.v1,  "display_order": 2},
    {"home_team": "Mexique",        "away_team": "Afrique du Sud", "home_score": 2, "away_score": 1, "result": MatchResult.v1,  "display_order": 3},
    {"home_team": "Afrique du Sud", "away_team": "Mexique",       "home_score": 0, "away_score": 0, "result": MatchResult.nul, "display_order": 4},
    {"home_team": "Mexique",        "away_team": "Afrique du Sud", "home_score": 1, "away_score": 0, "result": MatchResult.v1,  "display_order": 5},
]

RECENT_MATCHES_HOME = [
    {"opponent": "Serbie",    "home_or_away": "home", "goals_for": 5, "goals_against": 1, "result": MatchResult.v1,  "display_order": 1},
    {"opponent": "Australie", "home_or_away": "home", "goals_for": 1, "goals_against": 0, "result": MatchResult.v1,  "display_order": 2},
    {"opponent": "Ghana",     "home_or_away": "away", "goals_for": 2, "goals_against": 0, "result": MatchResult.v1,  "display_order": 3},
    {"opponent": "Belgique",  "home_or_away": "away", "goals_for": 1, "goals_against": 1, "result": MatchResult.nul, "display_order": 4},
    {"opponent": "Portugal",  "home_or_away": "home", "goals_for": 0, "goals_against": 0, "result": MatchResult.nul, "display_order": 5},
    {"opponent": "Islande",   "home_or_away": "home", "goals_for": 4, "goals_against": 0, "result": MatchResult.v1,  "display_order": 6},
]

RECENT_MATCHES_AWAY = [
    {"opponent": "Panama",   "home_or_away": "away", "goals_for": 1, "goals_against": 2, "result": MatchResult.v2,  "display_order": 1},
    {"opponent": "Panama",   "home_or_away": "home", "goals_for": 1, "goals_against": 1, "result": MatchResult.nul, "display_order": 2},
    {"opponent": "Cameroun", "home_or_away": "away", "goals_for": 1, "goals_against": 2, "result": MatchResult.v2,  "display_order": 3},
    {"opponent": "Zimbabwe", "home_or_away": "home", "goals_for": 3, "goals_against": 2, "result": MatchResult.v1,  "display_order": 4},
    {"opponent": "Égypte",   "home_or_away": "away", "goals_for": 0, "goals_against": 1, "result": MatchResult.v2,  "display_order": 5},
]

H2H_STATS = {
    "home_possession": 59.0, "away_possession": 41.0,
    "home_fouls":      20.5, "away_fouls":      None,
    "home_corners":     8.5, "away_corners":    None,
    "home_shots_on":    9.5, "away_shots_on":   None,
    "home_yellow":      3.5, "away_yellow":     None,
    "home_red":        None, "away_red":        None,
    "home_shots":      22.5, "away_shots":      None,
    "home_offsides":    2.5, "away_offsides":   None,
    "home_goals":      None, "away_goals":      None,
}

TEAM_STATS = {
    "home": {
        "possession":     58.0,
        "goals_scored":    2.1,
        "goals_conceded":  0.5,
        "corners":         6.8,
        "shots_on":        6.2,
        "shots":          None,
        "yellow_cards":   None,
        "red_cards":      None,
        "fouls":          None,
        "offsides":       None,
        "touches":        None,
        "saves":          None,
    },
    "away": {
        "possession":     44.0,
        "goals_scored":    1.2,
        "goals_conceded":  1.5,
        "corners":         4.7,
        "shots_on":        4.1,
        "shots":          None,
        "yellow_cards":   None,
        "red_cards":      None,
        "fouls":          None,
        "offsides":       None,
        "touches":        None,
        "saves":          None,
    },
}

PERCENTAGES = {
    "pct_home_win":       64.0,
    "pct_draw":           22.0,
    "pct_away_win":       14.0,
    "pct_v1_or_v2":       78.0,
    "pct_over_1_5":       78.0,
    "pct_over_2_5":       54.0,
    "pct_over_3_5":       28.0,
    "pct_over_4_5":       12.0,
    "possession_home":    58.0,
    "fouls_threshold":    19.5, "fouls_pct":          None,
    "corners_threshold":   8.5, "corners_pct":        None,
    "shots_on_threshold":  8.5, "shots_on_pct":       None,
    "cards_threshold":     3.5, "cards_pct":          None,
    "touches_threshold":  28.5, "touches_pct":        None,
    "shots_threshold":    21.5, "shots_pct":          None,
    "offsides_threshold":  2.5, "offsides_pct":       None,
}

PRONOSTICS = [
    {"category": PronosticCategory.H,   "code": "H1",   "display_order": 1, "label": "Mexique moins de 20.5 fautes"},
    {"category": PronosticCategory.H,   "code": "H2",   "display_order": 2, "label": "Mexique ou nul + plus de 1.5 buts"},
    {"category": PronosticCategory.H,   "code": "H3",   "display_order": 3, "label": "Afrique du Sud plus de 1.5 cartons"},
    {"category": PronosticCategory.W,   "code": "W1",   "display_order": 4, "label": "Plus de 7.5 corners"},
    {"category": PronosticCategory.W,   "code": "W2",   "display_order": 5, "label": "Plus de 8.5 tirs cadrés"},
    {"category": PronosticCategory.RSM, "code": "RSM1", "display_order": 6, "label": "Moins de 35.5 touches"},
    {"category": PronosticCategory.RSM, "code": "RSM2", "display_order": 7, "label": "Gardien Afrique du Sud 3.5+ arrêts"},
]

VERDICT = {
    "predicted_score": "2-0",
    "confidence":      ConfidenceLevel.haute,
    "summary": (
        "Le Mexique part favori grâce à l'avantage du terrain, une meilleure dynamique récente, "
        "une défense plus stable et une qualité technique supérieure. "
        "L'Afrique du Sud peut néanmoins poser des problèmes physiques et jouer en contre. "
        "Le scénario le plus probable reste une victoire du Mexique avec au moins 2 buts, "
        "plusieurs corners et cartons."
    ),
}


# =========================================================
# SEED
# =========================================================

async def seed(session):

    # --- Équipes ---
    home = await _get_team(session, "Mexique")
    away = await _get_team(session, "Afrique du Sud")

    # --- Match ---
    match = Match(
        home_team_id=home.id,
        away_team_id=away.id,
        competition=COMPETITION,
        match_date=MATCH_DATE,
        is_published=False,
    )
    session.add(match)
    await session.flush()  # récupère match.id sans commit

    # --- Contexte ---
    session.add(MatchContext(match_id=match.id, **CONTEXT))

    # --- H2H ---
    for h in H2H_MATCHES:
        session.add(H2HMatch(match_id=match.id, competition=COMPETITION, played_at=datetime(2020, 1, 1), **h))

    # --- Forme récente ---
    for rm in RECENT_MATCHES_HOME:
        session.add(TeamRecentMatch(match_id=match.id, team_id=home.id, played_at=datetime(2025, 1, 1), competition=COMPETITION, **rm))
    for rm in RECENT_MATCHES_AWAY:
        session.add(TeamRecentMatch(match_id=match.id, team_id=away.id, played_at=datetime(2025, 1, 1), competition=COMPETITION, **rm))

    # --- Stats H2H ---
    session.add(H2HStats(match_id=match.id, **H2H_STATS))

    # --- Stats forme ---
    session.add(TeamFormStats(match_id=match.id, team_id=home.id, **TEAM_STATS["home"]))
    session.add(TeamFormStats(match_id=match.id, team_id=away.id, **TEAM_STATS["away"]))

    # --- Pourcentages ---
    session.add(MatchPercentages(match_id=match.id, **PERCENTAGES))

    # --- Pronostics ---
    for p in PRONOSTICS:
        session.add(Pronostic(match_id=match.id, **p))

    # --- Verdict ---
    session.add(MatchVerdict(match_id=match.id, **VERDICT))

    await session.commit()
    print(f"✅ Match '{home.name} vs {away.name}' inséré avec succès (id={match.id})")


async def _get_team(session, name: str) -> Team:
    result = await session.execute(select(Team).where(Team.name == name))
    team = result.scalar_one_or_none()
    if not team:
        team = Team(name=name, short_name=name[:3].upper(), country="")
        session.add(team)
        await session.flush()
        print(f"⚠️  Équipe '{name}' créée à la volée — pense à compléter logo_url et country.")
    return team


async def main():
    async with LineAISessionLocal() as session:
        await seed(session)


if __name__ == "__main__":
    asyncio.run(main())