import re

def clean_markdown(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^\s*[o•]\s+", "- ", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    return text