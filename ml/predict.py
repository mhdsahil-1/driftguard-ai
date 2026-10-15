
from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = (
    Path(__file__).parent
    / "models"
    / "random_forest_baseline.joblib"
)

FEATURE_NAMES = [
    "step",
    "type",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
]


def load_model():
    """Load the trained Random Forest pipeline."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def predict_transaction(transaction: dict) -> dict:
    """Predict a transaction using the PaySim-trained model."""

    missing_features = [
        feature
        for feature in FEATURE_NAMES
        if feature not in transaction
    ]

    if missing_features:
        raise ValueError(
            f"Missing required features: {missing_features}"
        )

    # Build a DataFrame with the exact training feature names.
    input_data = pd.DataFrame(
        [[transaction[name] for name in FEATURE_NAMES]],
        columns=FEATURE_NAMES,
    )

    model = load_model()

    prediction = int(model.predict(input_data)[0])
    probabilities = model.predict_proba(input_data)[0]
    classes = list(model.classes_)

    # Explicitly retrieve the probability for fraud class 1.
    if 1 not in classes:
        raise ValueError(
            "The trained model does not contain fraud class 1."
        )

    fraud_index = classes.index(1)
    fraud_probability = float(probabilities[fraud_index])

    return {
        "prediction": prediction,
        "predicted_class": (
            "fraud" if prediction == 1 else "non_fraud"
        ),
        "fraud_probability": round(fraud_probability, 4),
        "model": "random_forest_baseline",
        "dataset_context": "PaySim synthetic transaction data",
        "assessment_type": "experimental_ml_prediction",
        "warning": (
            "This model was trained on PaySim synthetic data. "
            "Its output is not a calibrated probability of "
            "real-world PayPal fraud and is not a PayPal "
            "fraud decision."
        ),
    }
