
import pandas as pd
import pytest

from ml.drift import calculate_psi, detect_feature_drift


def test_identical_distributions_have_near_zero_psi():
    values = pd.Series([10, 20, 30, 40, 50, 60, 70, 80])
    psi = calculate_psi(values, values.copy())
    assert abs(psi) < 0.01


def test_large_distribution_shift_is_detected():
    reference = pd.DataFrame({"amount": [10, 20, 30, 40, 50]})
    current = pd.DataFrame({"amount": [500, 600, 700, 800, 900]})

    result = detect_feature_drift(
        reference, current, ["amount"], threshold=0.2
    )

    assert result["features"]["amount"]["drift_detected"] is True
    assert result["drift_detected"] is True


def test_empty_reference_is_rejected():
    with pytest.raises(ValueError):
        calculate_psi(pd.Series(dtype=float), pd.Series([1, 2, 3]))


def test_invalid_numeric_values_are_rejected():
    with pytest.raises(ValueError):
        calculate_psi(
            pd.Series(["bad", "invalid"]),
            pd.Series([1, 2, 3]),
        )


def test_constant_reference_with_shifted_current_data():
    reference = pd.Series([100, 100, 100, 100, 100])
    current = pd.Series([500, 600, 700, 800, 900])

    psi = calculate_psi(reference, current)

    assert psi > 0.2


def test_negative_threshold_is_rejected():
    reference = pd.DataFrame({"amount": [10, 20, 30]})
    current = pd.DataFrame({"amount": [10, 20, 30]})

    with pytest.raises(ValueError):
        detect_feature_drift(
            reference, current, ["amount"], threshold=-0.1
        )


def test_missing_feature_is_rejected():
    reference = pd.DataFrame({"amount": [10, 20, 30]})
    current = pd.DataFrame({"amount": [10, 20, 30]})

    with pytest.raises(ValueError, match="Missing features"):
        detect_feature_drift(
            reference, current, ["unknown_feature"]
        )
