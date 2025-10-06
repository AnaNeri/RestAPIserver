import spacy
from langdetect import detect, LangDetectException
from config import SPACY_MODELS

class NLPBasedDetector:
    def __init__(self):
        """Initialize the NLP models for English and Portuguese."""
        self.models = {}
        missing_models = []

        for lang, model_name in SPACY_MODELS.items():
            try:
                self.models[lang] = spacy.load(model_name)
            except OSError:
                missing_models.append(lang)

        if missing_models:
            raise RuntimeError(f"Failed to load spaCy models for languages: {', '.join(missing_models)}")


    def detect(self, text: str, lang: str = "auto") -> dict[str, dict]:
        """
        Detects entities in text using spaCy's Models for English or Portuguese.
        Args:
            text: Input text.
            lang: "en" (English), "pt" (Portuguese), or "auto" (default: auto-detect).
        Returns:
            Dictionary of entities with their types, detection method, and languages.
        """
        entities = {}

         # Auto-detect language if needed
        if lang == "auto":
            try:
                detected_lang = detect(text)
                lang = "pt" if detected_lang == "pt" else "en"
            except LangDetectException:
                # If auto-detection fails, run both models as a fallback
                return self._detect_with_both_models(text)

        # Use the model specified in the config
        if lang in self.models:
            doc = self.models[lang](text)
            # Extract entities from the processed document
            for ent in doc.ents:
                if ent.text not in entities:
                    entities[ent.text] = {
                        "method": "nlp",
                        "type": ent.label_,
                        "languages": [lang],
                    }
        else:
            # If the specified language is not available, use both models
            return self._detect_with_both_models(text)

        return entities

    def _detect_with_both_models(self, text: str) -> dict[str, dict]:
        """
        Detects entities using both English and Portuguese models as a fallback.
        """
        entities = {}

        # Run both models
        for lang, model in self.models.items():
            doc = model(text)
            for ent in doc.ents:
                if ent.text not in entities:
                    entities[ent.text] = {
                        "method": "nlp",
                        "type": ent.label_,
                        "languages": [lang],
                    }
                else:
                    if lang not in entities[ent.text]["languages"]:
                        entities[ent.text]["languages"].append(lang)

        return entities



