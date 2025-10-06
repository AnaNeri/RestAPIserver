import re

class RuleBasedDetector:
    def detect(self, text: str) -> dict[str, dict]:
        """
        Detects entities in text using regex patterns.
        Returns a dictionary of entities with their types and detection method.
        """
        entities = {}

        # Regex patterns for common entities
        patterns = {
            "email": r"\b[\w\.-]+@[\w\.-]+\b",
            "phone_or_nif": r"(?:\+\d{1,3}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?){2}\d{3,4}",
            "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
            }

        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                # Avoid duplicates (e.g., overlapping matches)
                if match not in entities:
                    entities[match] = {
                        "method": "rule_based",
                        "type": entity_type,
                    }

        return entities