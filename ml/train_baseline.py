
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "processed"
MODEL_DIR = BASE_DIR / "ml" / "models"

TARGET = "isFraud"

# Exclude identifiers, target labels, and the existing flag.
FEATURES = [
    "step",
    "type",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
]


def load_split(name):
    return pd.read_csv(DATA_DIR / f"{name}.csv")


def main():
    train = load_split("train")
    validation = load_split("validation")
    test = load_split("test")

    X_train, y_train = train[FEATURES], train[TARGET]
    X_val, y_val = validation[FEATURES], validation[TARGET]
    X_test, y_test = test[FEATURES], test[TARGET]

    numeric_features = [
        "step",
        "amount",
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest",
    ]
    categorical_features = ["type"]

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    preprocessor = ColumnTransformer([
        ("numeric", numeric_pipeline, numeric_features),
        ("categorical", categorical_pipeline, categorical_features),
    ])

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=100,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )),
    ])

    model.fit(X_train, y_train)

    # Use validation data for preliminary model assessment.
    val_scores = model.predict_proba(X_val)[:, 1]
    print("\nVALIDATION PR-AUC (Average Precision):")
    print(round(average_precision_score(y_val, val_scores), 4))

    # Final evaluation on the later, held-out test period.
    test_scores = model.predict_proba(X_test)[:, 1]
    predictions = (test_scores >= 0.5).astype(int)

    print("\nTEST PR-AUC (Average Precision):")
    print(round(average_precision_score(y_test, test_scores), 4))

    print("\nTEST CLASSIFICATION REPORT:")
    print(classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        zero_division=0,
    ))

    print("\nTEST CONFUSION MATRIX:")
    print(confusion_matrix(y_test, predictions, labels=[0, 1]))

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / "random_forest_baseline.joblib"
    joblib.dump(model, model_path)
    print(f"\nModel saved to: {model_path}")


if __name__ == "__main__":
    main()

