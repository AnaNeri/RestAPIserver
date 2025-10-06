import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.anonymizer import Anonymizer
from app.services.rule_based import RuleBasedDetector
from app.services.nlp_based import NLPBasedDetector
from app.utils.token_manager import TokenManager

# Initialize the anonymizers
rule_based_anonymizer = RuleBasedDetector()
nlp_entity_detector = NLPBasedDetector()


### Test Rule-Based Detection
def test_rule_based_emails():
    text = "Contact me at john.doe@example.com or jane@example.org."
    result = rule_based_anonymizer.detect(text)
    assert "john.doe@example.com" in result
    assert "jane@example.org" in result
    assert result["john.doe@example.com"]["type"] == "email"

def test_rule_based_phones():
    text = "Call me at +351 123 456 789 or 123-456-7890."
    result = rule_based_anonymizer.detect(text)
    assert "+351 123 456 789" in result
    assert "123-456-7890" in result
    assert result["123-456-7890"]["type"] == "phone_or_nif"

def test_rule_based_portuguese_nif():
    text = "Companies NIF: 123456789."
    result = rule_based_anonymizer.detect(text)
    assert "123456789" in result
    assert result["123456789"]["type"] == "phone_or_nif"

def test_rule_based_phones_edge_cases():
    text = """
    +351123456789,
    +1 (123) 456-7890,
    123.456.7890,
    1234567890
    """
    result = rule_based_anonymizer.detect(text)
    assert "+351123456789" in result
    assert "+1 (123) 456-7890" in result
    assert "123.456.7890" in result
    assert "1234567890" in result


### Test NLP-Based Detection (English)
def test_nlp_based_english():
    text = "John Doe works at Acme Corp in New York."
    result = nlp_entity_detector.detect(text, lang="en")
    assert "John Doe" in result
    assert result["John Doe"]["type"] == "PERSON"
    assert "Acme Corp" in result
    assert result["Acme Corp"]["type"] == "ORG"


### Test NLP-Based Detection (Portuguese)
def test_nlp_based_portuguese():
    text = "João Silva trabalha na Empresa XYZ em Lisboa."
    result = nlp_entity_detector.detect(text, lang="pt")
    assert "João Silva" in result
    assert result["João Silva"]["type"] == "PER"  # Note: Portuguese model uses "PER"
    assert "Empresa XYZ" in result
    assert result["Empresa XYZ"]["type"] == "ORG"


### Test Auto-Language Detection
def test_nlp_based_auto_language():
    # English text
    text_en = "Mary works at Google."
    result_en = nlp_entity_detector.detect(text_en, lang="auto")
    assert "Mary" in result_en
    assert "en" in result_en["Mary"]["languages"]

    # Portuguese text
    text_pt = "Maria é funcionária na Microsoft."
    result_pt = nlp_entity_detector.detect(text_pt, lang="auto")
    assert "Maria" in result_pt
    assert "pt" in result_pt["Maria"]["languages"]


### Test Edge Cases
def test_rule_based_no_entities():
    text = "This text has no entities."
    result = rule_based_anonymizer.detect(text)
    assert len(result) == 0

def test_nlp_based_no_entities():
    text = "This text has no entities."
    result = nlp_entity_detector.detect(text, lang="en")
    assert len(result) == 0

def test_nlp_based_mixed_language():
    text = "John and João are friends."
    result = nlp_entity_detector.detect(text, lang="auto")
    assert "John" in result or "João" in result


#------------------------------------------------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------



@pytest.fixture
def mock_rule_based():
    mock = MagicMock(spec=RuleBasedDetector)
    mock.detect.return_value = {
        "john.doe@example.com": {"method": "rule_based", "type": "email"},
        "+351 123 456 789": {"method": "rule_based", "type": "phone_or_nif"}
    }
    return mock

@pytest.fixture
def mock_nlp_based():
    mock = MagicMock(spec=NLPBasedDetector)
    mock.detect.return_value = {
        "John Doe": {"method": "nlp", "type": "PERSON", "languages": ["en"]},
        "Acme Corp": {"method": "nlp", "type": "ORG", "languages": ["en"]}
    }
    return mock

@pytest.fixture
def anonymizer(mock_rule_based, mock_nlp_based):
    # Create anonymizer with mocked dependencies
    anony = Anonymizer(strategy="consistent_tokens", lang="en")
    anony.rule_based = mock_rule_based
    anony.nlp_based = mock_nlp_based
    return anony

def test_anonymizer_initialization():
    anony = Anonymizer(strategy="masking", lang="pt")
    assert anony.strategy == "masking"
    assert anony.lang == "pt"
    assert isinstance(anony.token_manager, TokenManager)
    assert hasattr(anony, 'rule_based')
    assert hasattr(anony, 'nlp_based')

def test_anonymize_calls_entities(anonymizer, mock_rule_based, mock_nlp_based):
    text = "Test text"
    result = anonymizer.anonymize(text)

    # Verify both detectors were called
    mock_rule_based.detect.assert_called_once_with(text)
    mock_nlp_based.detect.assert_called_once_with(text)

def test_consistent_tokens_strategy(anonymizer):
    text = "John Doe's email is john.doe@example.com and his phone is +351 123 456 789. He works at Acme Corp."
    anonymizer.strategy = "consistent_tokens"

    # Define entities in the order they appear in the text
    entities = {
        "John Doe": {"method": "nlp", "type": "PERSON"},
        "john.doe@example.com": {"method": "rule_based", "type": "email"},
        "+351 123 456 789": {"method": "rule_based", "type": "phone_or_nif"},
        "Acme Corp": {"method": "nlp", "type": "ORG"}
    }

    # Create a mapping from entity to token for verification
    entity_to_token = {
        "John Doe": "TOKEN_123",
        "john.doe@example.com": "TOKEN_456",
        "+351 123 456 789": "TOKEN_789",
        "Acme Corp": "TOKEN_abc"
    }

    # Mock token_manager.get_token to return the correct token for each entity
    def get_token_side_effect(entity):
        return entity_to_token[entity]

    anonymizer.token_manager = MagicMock()
    anonymizer.token_manager.get_token.side_effect = get_token_side_effect

    # Call _apply_strategy
    result_text, result_explanations = anonymizer._apply_strategy(text, entities)

    # Verify the result by replacing entities in the original text with their tokens
    expected_text = text
    for entity, token in entity_to_token.items():
        expected_text = expected_text.replace(entity, token)

    assert result_text == expected_text
    assert len(result_explanations) == 4

    # Verify each explanation
    for explanation in result_explanations:
        assert explanation["replacement"] == entity_to_token[explanation["entity"]]


def test_hashing_strategy(anonymizer):
    text = "John Doe's email is john.doe@example.com"
    anonymizer.strategy = "hashing"

    # Mock token_manager.hash_entity to return predictable values
    anonymizer.token_manager = MagicMock()
    anonymizer.token_manager.hash_entity.side_effect = [
        "HASH_123", "HASH_456"
    ]

    result_text, result_explanations = anonymizer._apply_strategy(text, {
        "John Doe": {"method": "nlp", "type": "PERSON"},
        "john.doe@example.com": {"method": "rule_based", "type": "email"}
    })

    expected_text = "HASH_123's email is HASH_456"
    assert result_text == expected_text
    assert len(result_explanations) == 2
    anonymizer.token_manager.hash_entity.assert_called()

def test_masking_strategy(anonymizer):
    text = "John Doe's email is john.doe@example.com"
    anonymizer.strategy = "masking"

    # Mock token_manager.mask_entity to return predictable values
    anonymizer.token_manager = MagicMock()
    anonymizer.token_manager.mask_entity.side_effect = [
        "J*** D**", "j****@example.com"
    ]

    result_text, result_explanations = anonymizer._apply_strategy(text, {
        "John Doe": {"method": "nlp", "type": "PERSON"},
        "john.doe@example.com": {"method": "rule_based", "type": "email"}
    })

    expected_text = "J*** D**'s email is j****@example.com"
    assert result_text == expected_text
    assert len(result_explanations) == 2
    anonymizer.token_manager.mask_entity.assert_called()

def test_init_with_unknown_strategy():
    with pytest.raises(ValueError, match="Unknown strategy: unknown"):
        Anonymizer(strategy="unknown", lang="en")

def test_init_with_unsupported_language():
    with pytest.raises(ValueError, match="Unsupported language: fr"):
        Anonymizer(strategy="consistent_tokens", lang="fr")

def test_anonymize_with_empty_entities(anonymizer):
    text = "No entities here"
    # Mock detectors to return empty dicts
    anonymizer.rule_based.detect.return_value = {}
    anonymizer.nlp_based.detect.return_value = {}

    result_text, result_explanations = anonymizer.anonymize(text)
    assert result_text == text  # Should return original text if no entities
    assert len(result_explanations) == 0

def test_overlapping_entities(anonymizer):
    text = "John Doe and John Smith"
    anonymizer.strategy = "consistent_tokens"

    # Mock token_manager.get_token to return predictable values
    anonymizer.token_manager = MagicMock()
    anonymizer.token_manager.get_token.side_effect = ["TOKEN_1", "TOKEN_2"]

    result_text, result_explanations = anonymizer._apply_strategy(text, {
        "John Doe": {"method": "nlp", "type": "PERSON"},
        "John Smith": {"method": "nlp", "type": "PERSON"}
    })

    expected_text = "TOKEN_1 and TOKEN_2"
    assert result_text == expected_text
    assert len(result_explanations) == 2
    anonymizer.token_manager.get_token.assert_called()

def test_anonymize_method(anonymizer):
    text = "John Doe's email is john.doe@example.com"
    # Mock detectors to return entities
    anonymizer.rule_based.detect.return_value = {
        "john.doe@example.com": {"method": "rule_based", "type": "email"}
    }
    anonymizer.nlp_based.detect.return_value = {
        "John Doe": {"method": "nlp", "type": "PERSON"}
    }

    # Mock token_manager.get_token to return predictable values
    anonymizer.token_manager = MagicMock()
    anonymizer.token_manager.get_token.side_effect = ["TOKEN_123", "TOKEN_456"]

    result_text, result_explanations = anonymizer.anonymize(text)

    expected_text = "TOKEN_123's email is TOKEN_456"
    assert result_text == expected_text
    assert len(result_explanations) == 2