import httpx
import os
import random
import re

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# =========================
# 🔤 NORMALISATION TEXTE
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

    if t in THANKS or any(word in t.split() for word in THANKS):
        return "thanks"

    if t in GREETINGS:
        return "greeting"

    return None


# =========================
# 💬 RESPONSES
# =========================
RESPONSES = {
    "greeting": [
        "Bonjour ! 👋 Comment puis-je vous aider ?",
        "Salut ! 😊 Une question ?",
        "Hey ! 👋 Je suis là pour toi.",
    ],
    "thanks": [
        "Avec plaisir ! 😊",
        "De rien ! 👍",
        "Toujours là pour aider ! ✨",
    ],
    "goodbye": [
        "Au revoir ! 👋",
        "À bientôt ! 😊",
        "Prends soin de toi ! 🌟",
    ],
}


def get_special_response(question: str) -> str | None:
    intent = detect_intent(question)

    if intent:
        return random.choice(RESPONSES[intent])

    return None


# =========================
# 🤖 GEMINI
# =========================
async def gemini_generate(prompt: str):
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY manquante")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.post(url, json={
            "contents": [{"parts": [{"text": prompt}]}]
        })

        data = res.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            raise Exception(f"Gemini error: {data}")


# =========================
# 🤖 OPENROUTER
# =========================
async def openrouter_generate(prompt: str):
    if not OPENROUTER_API_KEY:
        raise Exception("OPENROUTER_API_KEY manquante")

    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
            },
        )

        data = res.json()

        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            raise Exception(f"OpenRouter error: {data}")


# =========================
# 🧠 MAIN GENERATOR
# =========================
async def generate_answer(prompt: str, question: str = None):
    # 🎯 Détection rapide (évite appel IA inutile)
    if question:
        special = get_special_response(question)
        if special:
            print(f"⚡ Intent détecté → {question}")
            return special

    errors = []

    # 🔥 GEMINI
    try:
        print("🔥 GEMINI")
        return await gemini_generate(prompt)

    except Exception as e:
        print("❌ GEMINI:", e)
        errors.append(str(e))

    # 🔥 FALLBACK OPENROUTER
    try:
        print("🔥 OPENROUTER (fallback)")
        return await openrouter_generate(prompt)

    except Exception as e:
        print("❌ OPENROUTER:", e)
        errors.append(str(e))

    # ❌ ERREUR FINALE
    return "❌ Impossible de répondre pour le moment. Réessaie plus tard."


# =========================
# 🧠 PROMPT INTELLIGENT
# =========================
async def generate_clean_answer(question: str, search_data: str):
    prompt = f"""
Tu es un assistant intelligent.

Règles :
- Réponds clairement et simplement
- Utilise des emojis si pertinent
- Structure avec des listes ou tableaux si utile
- Si info insuffisante → dis-le

Données :
{search_data}

Question :
{question}
"""

    return await generate_answer(prompt, question)