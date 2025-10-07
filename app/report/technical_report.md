# Technical Report: RestAPIserver Anonymization Service
*By Ana Neri, October 2025*

## Project Overview

This project implements a modular anonymization service supporting multiple anonymization strategies for text data. 

The codebase is organized under the `app` package, with clear separation of concerns across models, services, utilities, static assets, templates, and tests.

## Design Overview

* The project was implemented with Python, with libraries such as FastAPI, pytest and spaCy. 
* The three anonymization strategies are available to allow for flexible use cases. 
* The model uses a hybrid application of Regex and NLP-based detector. LLM was considered to be added as an optional third stage, but not implemented per time constraints. 
* The tests include both unit tests and quantitative tests to evaluate precision and recall.
* Tests can easily be run locally with FastAPI swagger. 
* The service is made available online by running a server using ngrok which is not on by default.
* The service may be accessed via webpage via REST API ( curl example is given bellow). While the webpage only allows a user to provide the text, through API service more control is allowed (selecting language and strategy).
* The config file was setup to easily change some default parameters such as language, spaCy models, anonymization strategies.

## Anonymization Strategies

Three anonymization options are provided:

- **Masking:** Sensitive entities are replaced with generic tokens (e.g., `***`).
- **Hashing:** Entities are replaced with hashed values for irreversible anonymization.
- **Consistent Tokenization:** Entities are replaced with consistent tokens, ensuring the same entity is always mapped to the same token.

These options provide flexibility for different use cases, such as privacy-preserving analytics or irreversible data redaction.

## Detection Methods

- **Regex-based Detection:** Used for numbers and simple patterns. This method is efficient but limited by pattern complexity.
- **NLP-based Detection:** Utilizes spaCy models for named entity recognition (NER), which is more robust for names and other entities affected by capitalization and context. Due to the nature of this project, small/light spaCy models were selected, but heavier models are recommended to improve performance in production.

### Language Support

- The NLP-based detection works for both **English** and **Portuguese**.
- The system attempts to **automatically detect the language** of the input text.
- If language detection fails, it tries entity recognition with **both English and Portuguese models** to maximize detection accuracy.

## Configuration

The main configuration is defined in `config.py`:
- **Default strategy:** `consistent_tokens`
- **Default language:** `auto`
- **Supported strategies:** `consistent_tokens`, `masking`, `hashing`
- **Supported languages:** `en`, `pt`, `auto`
- **spaCy models:** English (`en_core_web_sm`), Portuguese (`pt_core_news_sm`)

## Usage Example

You can use the API with a POST request to the `/anonymize` endpoint.  
Here is an example using `curl`:

```sh
curl -X POST <ENDPOINT>/anonymize \
     -H "Content-Type: application/json" \
     -d '{"text":"John Doe lives in Lisbon. Email: john.doe@example.com","strategy":"masking","language":"en"}'
```

- `text`: The input text to anonymize.
- `strategy`: The anonymization strategy (`masking`, `hashing`, or `consistent_tokens`).
- `language`: The language for entity detection (`en`, `pt`, or `auto`).

## Testing

- **Unit Tests:** Located in `app/tests/unit_tests.py`, these ensure individual components function as expected.
- **Quantitative Tests:** Found in `app/tests/quantitative_tests.py`, these evaluate the precision and recall of the anonymizer on synthetic datasets, providing metrics for detection quality.

```
Total entities: 159
Detected entities: 191
Correctly detected: 111
Precision: 0.58
Recall: 0.70
```

## Recommendations

- **Model Enhancement:** Consider selecting larger spaCy models and possibly performing fine-tuning for improved entity detection.
- **Test Coverage:** Expand unit and quantitative tests to cover more edge cases and real-world data.
- **User Experience:** Consider improving the look and feel of the web page and implementing more options.
