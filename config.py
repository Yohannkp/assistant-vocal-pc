# Configuration de l'Assistant Vocal PC
# Modifiez ces paramètres selon vos besoins

# Configuration Ollama
OLLAMA_URL = "http://127.0.0.1:11434"
MODEL_NAME = "mistral:instruct"
TIMEOUT_API = 30  # Timeout en secondes pour les requêtes API

# Configuration reconnaissance vocale
LANGUAGE = "fr-FR"  # Langue pour la reconnaissance vocale
LISTEN_TIMEOUT = 5  # Timeout d'écoute en secondes
PHRASE_TIME_LIMIT = 10  # Limite de temps pour une phrase

# Configuration synthèse vocale (TTS)
TTS_RATE = 180  # Vitesse de parole (mots par minute)
TTS_VOLUME = 0.9  # Volume (0.0 à 1.0)
PREFER_FRENCH_VOICE = True  # Préférer une voix française si disponible

# Configuration microphone
ADJUST_FOR_NOISE = True  # Ajustement automatique du bruit ambiant
NOISE_ADJUSTMENT_DURATION = 1  # Durée d'ajustement en secondes

# Mots de réveil acceptés (en minuscules)
WAKE_WORDS = ["assistant", "assistante", "hey assistant"]

# Commandes d'arrêt acceptées (en minuscules)
STOP_COMMANDS = ["quit", "exit", "stop", "au revoir", "arrêt", "fermer"]

# Prompts pour Mistral
SYSTEM_PROMPT = "Réponds en français de manière concise et naturelle à cette question ou demande : "
GREETING_MESSAGE = "Bonjour ! Je suis votre assistant vocal. Dites 'Assistant' pour me réveiller."

# Configuration d'affichage
SHOW_TIMING = True  # Afficher les temps de réponse
SHOW_TOKENS = True  # Afficher le nombre de tokens
SHOW_DEBUG = False  # Afficher les informations de débogage

# Modèles alternatifs (décommentez pour utiliser)
# MODEL_NAME = "deepseek-coder:latest"
# MODEL_NAME = "llama2:latest"
# MODEL_NAME = "codellama:latest"

# Configuration audio avancée
MICROPHONE_INDEX = None  # Index du microphone (None = défaut)
ENERGY_THRESHOLD = 300  # Seuil d'énergie pour détecter la parole
DYNAMIC_ENERGY_THRESHOLD = True  # Ajustement dynamique du seuil
