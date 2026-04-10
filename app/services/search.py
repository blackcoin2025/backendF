import httpx
import os

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")


async def tavily_search(query: str):
    """Recherche via Tavily API"""
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": "basic"
            }
        )
        return res.json()


async def firecrawl_search(query: str):
    """Recherche via Firecrawl API (fallback)"""
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(
            "https://api.firecrawl.dev/search",
            json={
                "query": query
            },
            headers={
                "Authorization": f"Bearer {FIRECRAWL_API_KEY}"
            }
        )
        return res.json()


async def search_web(query: str):
    """Recherche web avec fallback intelligent (Tavily → Firecrawl)"""
    errors = []
    
    # Essai Tavily d'abord
    try:
        print("🔍 TRYING TAVILY...")
        result = await tavily_search(query)
        if result and "results" in result:
            print("✅ TAVILY SUCCESS")
            return result
        else:
            errors.append("Tavily: no results")
    except Exception as e:
        print(f"❌ TAVILY ERROR: {e}")
        errors.append(f"Tavily: {str(e)}")
    
    # Fallback Firecrawl
    try:
        print("🔍 TRYING FIRECRAWL (fallback)...")
        result = await firecrawl_search(query)
        if result and "results" in result:
            print("✅ FIRECRAWL SUCCESS")
            return result
        else:
            errors.append("Firecrawl: no results")
    except Exception as e:
        print(f"❌ FIRECRAWL ERROR: {e}")
        errors.append(f"Firecrawl: {str(e)}")
    
    # Échec complet
    return {"error": "search failed", "details": " | ".join(errors)}