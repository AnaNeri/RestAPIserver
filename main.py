from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.models.models import AnonymizationRequest, AnonymizationResponse, EntityExplanation
from config import DEFAULT_STRATEGY, DEFAULT_LANGUAGE, SUPPORTED_STRATEGIES, SUPPORTED_LANGUAGES
from app.services.anonymizer import Anonymizer

# Initialize FastAPI
app = FastAPI(title="Text Anonymization API")

# Mount static files (for optional CSS/JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="app/templates")


# --------------------------
# FRONTEND ROUTE
# --------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve a simple HTML interface for the API."""
    return templates.TemplateResponse("index.html", {"request": request})


# --------------------------
# API ENDPOINTS
# --------------------------
@app.post("/anonymize", response_model=AnonymizationResponse)
async def anonymize(request: Request, text: str = Form(None)):
    try:
        # Try to parse JSON
        data = await request.json()
        text = data.get("text", text)
        strategy = data.get("strategy", DEFAULT_STRATEGY)
        language = data.get("language", DEFAULT_LANGUAGE)
    except Exception:
        # Fallback if it's form-data
        strategy = DEFAULT_STRATEGY
        language = DEFAULT_LANGUAGE

    if not text:
        raise HTTPException(status_code=400, detail="No text provided")

    anonymizer = Anonymizer(strategy=strategy, lang=language)
    anonymized_text, explanations_data = anonymizer.anonymize(text)

    explanations = [
        EntityExplanation(
            entity=exp["entity"],
            method=exp["method"],
            type=exp["type"],
            replacement=exp["replacement"]
        )
        for exp in explanations_data
    ]

    return AnonymizationResponse(
        original=text,
        anonymized=anonymized_text,
        explanations=explanations
    )

@app.get("/info")
async def api_info():
    """Basic API info (JSON)."""
    return {
        "message": "Anonymization API is running",
        "supported_strategies": SUPPORTED_STRATEGIES,
        "supported_languages": SUPPORTED_LANGUAGES,
        "default_strategy": DEFAULT_STRATEGY,
        "default_language": DEFAULT_LANGUAGE
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
