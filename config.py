# Default settings
DEFAULT_STRATEGY = "consistent_tokens"
DEFAULT_LANGUAGE = "auto"

# Supported strategies
SUPPORTED_STRATEGIES = ["consistent_tokens", "masking", "hashing"]

# Supported languages
SUPPORTED_LANGUAGES = ["en", "pt", "auto"]

# Configuration for spaCy models
SPACY_MODELS = {
    "en": "en_core_web_sm",
    "pt": "pt_core_news_sm"
}
