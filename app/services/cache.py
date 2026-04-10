import time
from threading import Lock

cache_store = {}
cache_lock = Lock()

CACHE_TTL = 60 * 60 * 24  # 🔥 24h
MAX_CACHE_SIZE = 1000     # 🔥 limite sécurité


def get_cache(key: str):
    now = time.time()

    with cache_lock:
        data = cache_store.get(key)

        if not data:
            return None

        # ⏳ Expiration
        if now - data["time"] > CACHE_TTL:
            del cache_store[key]
            return None

        return data["value"]


def set_cache(key: str, value):
    now = time.time()

    with cache_lock:
        # 🔥 Limite mémoire
        if len(cache_store) >= MAX_CACHE_SIZE:
            # supprime les plus anciens
            oldest_key = min(cache_store, key=lambda k: cache_store[k]["time"])
            del cache_store[oldest_key]

        cache_store[key] = {
            "value": value,
            "time": now
        }


def clean_cache():
    """Nettoyage global (optionnel mais recommandé)"""
    now = time.time()

    with cache_lock:
        keys_to_delete = [
            k for k, v in cache_store.items()
            if now - v["time"] > CACHE_TTL
        ]

        for k in keys_to_delete:
            del cache_store[k]