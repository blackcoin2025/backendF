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

        content = content.strip()[:400]
        block = f"### {title}\n{content}\n"

        if total + len(block) > max_chars:
            break

        parts.append(block)
        total += len(block)

    return "\n\n".join(parts) if parts else "Informations insuffisantes."