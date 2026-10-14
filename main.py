from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from routes.payments import router as payments_router


PROJECT_ROOT = Path(__file__).resolve().parent
STATIC_DIR = PROJECT_ROOT / "static"

app = FastAPI(
    title="DriftGuard AI",
    description="Experimental payment risk analysis API",
    version="0.2.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(payments_router, prefix="")


@app.get("/checkout", include_in_schema=False)
def checkout_page():
    return FileResponse(STATIC_DIR / "checkout.html")


class Transaction(BaseModel):
    amount: float = Field(gt=0, le=1_000_000)
    transaction_count_last_hour: int = Field(ge=0, le=10000)
    account_age_days: int = Field(ge=0, le=36500)


@app.get("/")
def home():
    return {
        "project": "DriftGuard AI",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/risk/score")
def score_transaction(tx: Transaction):
    score = 0
    reasons = []

    if tx.amount >= 1000:
        score += 35
        reasons.append("High transaction amount")

    if tx.transaction_count_last_hour >= 10:
        score += 35
        reasons.append("High transaction frequency")

    if tx.account_age_days < 7:
        score += 30
        reasons.append("New account")

    score = min(score, 100)

    if score >= 60:
        category = "high"
    elif score >= 30:
        category = "medium"
    else:
        category = "low"

    return {
        "risk_score": score,
        "risk_category": category,
        "reasons": reasons,
        "assessment_type": "experimental_rule_based",
        "warning": (
            "This is a demonstration score, not a trained model "
            "or a calibrated probability of fraud."
        ),
    }
