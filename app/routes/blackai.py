import logging
from fastapi import APIRouter

from app.schemas import Question
from app.services.intent import normalize, get_special_response
from app.services.filter import filter_search_results
from app.services.prompt import build_prompt
from app.services.cleaner import clean_markdown
from app.services.search import search_web
from app.services.ai import generate_answer
from app.services.cache import get_cache, set_cache

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/blackai")
async def blackai(data: Question):
    question = data.question.strip()

    if not question:
        return {"source": "error", "answer": "❌ Question vide."}

    normalized_q = normalize(question)

    # 🎯 1. INTENT
    special = get_special_response(question)
    if special:
        return {"source": "direct", "answer": special}

    # 💾 2. CACHE
    cached = get_cache(normalized_q)
    if cached:
        return {"source": "cache", "answer": cached}

    # 🔎 3. SEARCH
    try:
        search_data = await search_web(question)
        print(f"✅ SEARCH OK: {type(search_data)}")
    except Exception as e:
        print(f"❌ SEARCH ERREUR: {repr(e)}")
        search_data = {"results": []}

    # 🧹 4. FILTER
    try:
        context = filter_search_results(search_data)
        print(f"✅ CONTEXT OK: {len(context)} chars")
    except Exception as e:
        print(f"❌ FILTER ERREUR: {repr(e)}")
        context = "Aucun contexte disponible."

    # 🧠 5. PROMPT
    try:
        prompt = build_prompt(context, question)
        print(f"✅ PROMPT OK: {len(prompt)} chars")
    except Exception as e:
        print(f"❌ PROMPT ERREUR: {repr(e)}")
        return {"source": "error", "answer": f"❌ Erreur prompt: {e}"}

    # 🤖 6. IA
    try:
        raw_answer = await generate_answer(prompt, question)
        print(f"✅ IA OK: {raw_answer[:100] if raw_answer else 'VIDE'}")
    except Exception as e:
        print(f"❌ IA ERREUR: {repr(e)}")
        return {"source": "error", "answer": f"❌ Erreur IA: {e}"}

    # 🧼 7. CLEAN
    try:
        answer = clean_markdown(raw_answer)
    except Exception as e:
        print(f"❌ CLEAN ERREUR: {repr(e)}")
        answer = raw_answer

    # 💾 8. CACHE SAVE
    set_cache(normalized_q, answer)

    return {"source": "live", "answer": answer}