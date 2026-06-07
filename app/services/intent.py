import random
import re

GREETINGS = {"salut", "bonjour", "bonsoir", "coucou", "hello", "hey", "yo", "hi", "good morning", "good evening"}
THANKS = {"merci", "thanks", "thank you", "thx", "gracias", "شكرا"}
GOODBYES = {"au revoir", "bye", "goodbye", "ciao", "adieu", "hasta luego", "مع السلامة"}

CASUAL_PATTERNS = [
    "comment tu vas", "comment vas-tu", "comment ca va", "comment ça va",
    "tu vas bien", "ca va toi", "ça va toi",
    "how are you", "how r u", "how do you do",
    "como estas", "como estás",
    "tu es qui", "t'es qui", "qui es-tu",
    "who are you", "what are you",
    "quien eres", "quién eres",
    "من أنت",
]

# ✅ Réponses multilingues
RESPONSES = {
    "greeting": {
        "fr": ["Bonjour 👋\n\nComment puis-je t'aider ?", "Salut 😊\n\nPose-moi ta question."],
        "en": ["Hello 👋\n\nHow can I help you?", "Hi there 😊\n\nWhat can I do for you?"],
        "es": ["¡Hola 👋\n\n¿En qué puedo ayudarte?", "¡Buenas! 😊\n\nDime tu pregunta."],
        "ar": ["مرحباً 👋\n\nكيف يمكنني مساعدتك؟", "أهلاً 😊\n\nاسألني أي سؤال."],
    },
    "greeting_chat": {
        "fr": ["Bonjour 😊\n\nJe vais très bien, merci ! Et toi ?\n\nComment puis-je t'aider ?"],
        "en": ["Hello 😊\n\nI'm doing great, thanks! And you?\n\nHow can I help?"],
        "es": ["¡Hola 😊\n\n¡Muy bien, gracias! ¿Y tú?\n\n¿En qué puedo ayudarte?"],
        "ar": ["مرحباً 😊\n\nأنا بخير شكراً! وأنت؟\n\nكيف يمكنني مساعدتك؟"],
    },
    "casual": {
        "fr": ["Je suis LineAI, ton assistant intelligent 🤖\n\nJe peux répondre à tes questions, faire des recherches et bien plus.\n\nQue puis-je faire pour toi ?"],
        "en": ["I'm LineAI, your intelligent assistant 🤖\n\nI can answer questions, search the web and much more.\n\nWhat can I do for you?"],
        "es": ["Soy LineAI, tu asistente inteligente 🤖\n\nPuedo responder preguntas, buscar información y mucho más.\n\n¿Qué puedo hacer por ti?"],
        "ar": ["أنا LineAI، مساعدك الذكي 🤖\n\nيمكنني الإجابة على أسئلتك والبحث في الويب وأكثر.\n\nماذا يمكنني أن أفعل لك؟"],
    },
    "thanks": {
        "fr": ["Avec plaisir 😊", "De rien 👍"],
        "en": ["You're welcome 😊", "No problem 👍"],
        "es": ["De nada 😊", "¡Con gusto 👍"],
        "ar": ["على الرحب والسعة 😊", "لا شكر على واجب 👍"],
    },
    "goodbye": {
        "fr": ["À bientôt 👋", "Au revoir 😊"],
        "en": ["Goodbye 👋", "See you soon 😊"],
        "es": ["¡Hasta luego 👋!", "¡Adiós 😊!"],
        "ar": ["مع السلامة 👋", "إلى اللقاء 😊"],
    },
}


def normalize(text: str) -> str:
    return re.sub(r"[^\w\s]", "", text.lower()).strip()


def detect_lang(text: str) -> str:
    """Détection simple de langue par mots-clés."""
    t = text.lower()

    arabic_chars = sum(1 for c in t if '\u0600' <= c <= '\u06ff')
    if arabic_chars > 2:
        return "ar"

    en_words = {"the", "is", "are", "how", "what", "why", "when", "where", "who", "can", "you", "your", "i", "my", "help", "hello", "hi"}
    es_words = {"hola", "como", "qué", "que", "por", "favor", "gracias", "buenos", "estás", "estas", "puedo", "ayuda"}

    words = set(t.split())

    if words & es_words:
        return "es"
    if words & en_words:
        return "en"

    return "fr"  # défaut


def detect_intent(text: str) -> str | None:
    t = normalize(text)
    words = set(t.split())

    if t in GOODBYES:
        return "goodbye"

    if any(word in THANKS for word in words) and len(t.split()) <= 5:
        return "thanks"

    if t in GREETINGS:
        return "greeting"

    first_word = t.split()[0] if t.split() else ""
    if first_word in GREETINGS:
        return "greeting_chat"

    for pattern in CASUAL_PATTERNS:
        if pattern in t:
            return "casual"

    return None


def get_special_response(question: str) -> str | None:
    intent = detect_intent(question)
    if not intent:
        return None

    lang = detect_lang(question)
    options = RESPONSES.get(intent, {}).get(lang) or RESPONSES.get(intent, {}).get("fr", [])

    if options:
        return random.choice(options)
    return None