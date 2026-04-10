from fastapi import APIRouter
from pydantic import BaseModel
import random
import re

from app.services.search import search_web
from app.services.ai import generate_answer
from app.services.cache import get_cache, set_cache

router = APIRouter()


class Question(BaseModel):
    question: str


# =========================
# 🔤 NORMALISATION
# =========================
def normalize(text: str) -> str:
    return re.sub(r"[^\w\s]", "", text.lower()).strip()


# =========================
# 🎯 INTENT DETECTION
# =========================
GREETINGS = {"salut", "bonjour", "bonsoir", "coucou", "hello", "hey", "yo"}
THANKS = {"merci", "thanks", "thank you", "thx"}
GOODBYES = {"au revoir", "bye", "goodbye", "ciao", "adieu"}


def detect_intent(text: str) -> str | None:
    t = normalize(text)

    if t in GOODBYES:
        return "goodbye"

    # ⚠️ éviter faux positif genre "merci pour info mais..."
    words = t.split()

    if any(word in THANKS for word in words) and len(words) <= 4:
        return "thanks"

    if t in GREETINGS:
        return "greeting"

    return None


def get_special_response(question: str) -> str | None:
    intent = detect_intent(question)

    responses = {
        "greeting": [
            "Bonjour ! 👋 Comment puis-je vous aider ?",
            "Salut ! 😊 Une question ?",
        ],
        "thanks": [
            "Avec plaisir ! 😊",
            "De rien ! 👍",
        ],
        "goodbye": [
            "Au revoir ! 👋",
            "À bientôt ! 😊",
        ],
    }

    if intent:
        return random.choice(responses[intent])

    return None


# =========================
# 🔎 FILTER SEARCH
# =========================
def filter_search_results(search_data: dict, max_chars: int = 2000) -> str:
    if not search_data or "results" not in search_data:
        return "Aucune information pertinente trouvée."

    parts = []
    total = 0

    for r in search_data["results"]:
        title = r.get("title", "")
        content = r.get("content") or r.get("snippet", "")

        if not content:
            continue

        content = content[:500]

        block = f"Titre: {title}\nExtrait: {content}\n---\n"

        if total + len(block) > max_chars:
            break

        parts.append(block)
        total += len(block)

    return "\n".join(parts) if parts else "Informations insuffisantes."


# =========================
# 🚀 ROUTE PRINCIPALE
# =========================
@router.post("/blackai")
async def blackai(data: Question):
    question = data.question.strip()

    if not question:
        return {"source": "error", "answer": "❌ Question vide."}

    normalized_q = normalize(question)

    # 🎯 1. INTENT RAPIDE
    special = get_special_response(question)
    if special:
        return {"source": "direct", "answer": special}

    # 💾 2. CACHE (clé propre)
    cached = get_cache(normalized_q)
    if cached:
        return {"source": "cache", "answer": cached}

    try:
        # 🔎 3. SEARCH
        search_data = await search_web(question)

        # 🧹 4. CLEAN
        filtered = filter_search_results(search_data)

        # 🧠 5. PROMPT
        prompt = f"""
Tu es un assistant intelligent.

Règles :
- Réponds clairement
- Structure avec listes ou tableaux si utile
- N'invente rien
- Si info insuffisante → dis-le

Données :
{filtered}

Question :
{question}
"""

        # 🤖 6. IA
        answer = await generate_answer(prompt, question)

    except Exception as e:
        print("❌ ERROR:", e)
        return {
            "source": "error",
            "answer": "❌ Une erreur est survenue. Réessaie plus tard."
        }

    # 💾 7. CACHE SAVE
    set_cache(normalized_q, answer)

    return {
        "source": "live",
        "answer": answer
    }