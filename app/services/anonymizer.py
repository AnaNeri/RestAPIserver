from app.services.rule_based import RuleBasedDetector
from app.services.nlp_based import NLPBasedDetector
#from app.services.llm_based import LLMAnonimizer
from app.utils.token_manager import TokenManager
from config import SUPPORTED_STRATEGIES, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, DEFAULT_STRATEGY

class Anonymizer:
    def __init__(self, strategy: str = DEFAULT_STRATEGY, lang: str = DEFAULT_LANGUAGE):
        if strategy not in SUPPORTED_STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy}")
        if lang not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {lang}")
        self.strategy = strategy
        self.lang = lang
        self.token_manager = TokenManager()
        self.rule_based = RuleBasedDetector()
        self.nlp_based = NLPBasedDetector()
        #self.llm_based = LLMAnonimizer(lang)

    def anonymize(self, text: str) -> dict[str, str]:
        # Combine results from all strategies
        rule_entities = self.rule_based.detect(text)
        nlp_entities = self.nlp_based.detect(text)
        #llm_entities = self.llm_based.detect(text)

        #all_entities = {**rule_entities, **nlp_entities, **llm_entities}
        all_entities = {**rule_entities, **nlp_entities}
        
        return self._apply_strategy(text, all_entities)

    def _apply_strategy(self, text: str, entities: dict[str, dict]) -> tuple[str, list[dict]]:
        """
        Apply the selected anonymization strategy and generate explanations.

        Args:
            text: Input text.
            entities: Dictionary of entities to anonymize.

        Returns:
            Tuple containing anonymized text and list of explanations.
        """
        anonymized_text = text
        explanations = []
        
        # Sort entities by length in descending order to handle substrings
        for entity in sorted(entities.keys(), key=len):
        
            # Apply the selected anonymization strategy
            if self.strategy == "consistent_tokens":
                replacement = self.token_manager.get_token(entity)
            elif self.strategy == "masking":
                replacement  = self.token_manager.mask_entity(entity)
            elif self.strategy == "hashing":
                replacement  = self.token_manager.hash_entity(entity)
            
            
            anonymized_text = anonymized_text.replace(entity, replacement)
            
            # Add explanation
            explanations.append({
                "entity": entity,
                "method": entities[entity]["method"],
                "type": entities[entity].get("type", ""),
                "replacement": replacement
            })

        return anonymized_text, explanations
        
    