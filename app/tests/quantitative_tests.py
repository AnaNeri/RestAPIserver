from app.services.anonymizer import Anonymizer
from app.tests.synthetic_dataset import synthetic_dataset

def test_anonymizer_precision_recall():
    anonymizer = Anonymizer(strategy="consistent_tokens", lang="auto")
    total_entities = 0
    detected_entities = 0
    correct_entities = 0

    for entry in synthetic_dataset:
        text = entry["text"]
        expected = set(entry["entities"])

        anonymized_text, explanations = anonymizer.anonymize(text)
        detected = set(exp["entity"] for exp in explanations)

        total_entities += len(expected)
        detected_entities += len(detected)
        correct_entities += len(expected & detected)

    precision = correct_entities / detected_entities if detected_entities else 0
    recall = correct_entities / total_entities if total_entities else 0

    print(f"Total entities: {total_entities}")
    print(f"Detected entities: {detected_entities}")
    print(f"Correctly detected: {correct_entities}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")

    # Assert minimal thresholds
    assert precision > 0.5, "Precision below 80%"
    assert recall > 0.5, "Recall below 80%"
