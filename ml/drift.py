
from typing import Any

import numpy as np
import pandas as pd


def calculate_psi(
    reference: pd.Series,
    current: pd.Series,
    bins: int = 10,
) -> float:
    """Calculate Population Stability Index for one numeric feature."""

    reference = pd.to_numeric(reference, errors="coerce").dropna()
    current = pd.to_numeric(current, errors="coerce").dropna()

    if reference.empty or current.empty:
        raise ValueError("Both datasets must contain numeric observations.")

    if bins < 2:
        raise ValueError("bins must be at least 2.")

    if not np.isfinite(reference).all() or not np.isfinite(current).all():
        raise ValueError("Feature values must be finite.")

    edges = np.unique(
        np.quantile(reference, np.linspace(0, 1, bins + 1))
    )

    if len(edges) < 2:
        value = float(reference.iloc[0])
        edges = np.array([
            -np.inf,
            value - 0.5,
            value + 0.5,
            np.inf,
        ])
    else:
        edges[0] = -np.inf
        edges[-1] = np.inf

    reference_counts = pd.cut(
        reference, bins=edges, include_lowest=True
    ).value_counts(sort=False).to_numpy(dtype=float)

    current_counts = pd.cut(
        current, bins=edges, include_lowest=True
    ).value_counts(sort=False).to_numpy(dtype=float)

    epsilon = 1e-6
    reference_pct = (reference_counts + epsilon) / (
        reference_counts.sum() + epsilon * len(reference_counts)
    )
    current_pct = (current_counts + epsilon) / (
        current_counts.sum() + epsilon * len(current_counts)
    )

    psi = np.sum(
        (current_pct - reference_pct)
        * np.log(current_pct / reference_pct)
    )

    return float(psi)


def detect_feature_drift(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    features: list[str],
    threshold: float = 0.2,
) -> dict[str, Any]:
    """Compare numeric feature distributions and report potential drift."""

    if reference.empty or current.empty:
        raise ValueError("Reference and current datasets cannot be empty.")

    if not np.isfinite(threshold) or threshold < 0:
        raise ValueError("threshold must be finite and non-negative.")

    if not features:
        raise ValueError("At least one feature must be provided.")

    if len(features) != len(set(features)):
        raise ValueError("Duplicate features are not allowed.")

    missing = [
        feature
        for feature in features
        if feature not in reference.columns
        or feature not in current.columns
    ]

    if missing:
        raise ValueError(f"Missing features: {missing}")

    results = {}

    for feature in features:
        psi = calculate_psi(reference[feature], current[feature])

        results[feature] = {
            "psi": round(psi, 4),
            "drift_detected": psi >= threshold,
        }

    return {
        "method": "Population Stability Index (PSI)",
        "threshold": threshold,
        "reference_rows": len(reference),
        "current_rows": len(current),
        "features": results,
        "drift_detected": any(
            item["drift_detected"] for item in results.values()
        ),
        "warning": (
            "Feature distribution drift does not by itself prove "
            "fraud or a decline in model performance."
        ),
    }
