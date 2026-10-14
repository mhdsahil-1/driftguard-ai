
import os
from pathlib import Path
from urllib.parse import quote

import httpx
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SANDBOX_API_BASE = "https://api-m.sandbox.paypal.com"

load_dotenv(PROJECT_ROOT / ".env")


def get_paypal_checkout_config() -> dict[str, str]:
    """Return only browser-safe PayPal Sandbox SDK settings."""
    _get_sandbox_api_base()
    return {"client_id": _get_paypal_client_id()}


def _get_paypal_client_id() -> str:
    client_id = os.getenv("PAYPAL_CLIENT_ID", "").strip()
    if not client_id or client_id.lower().startswith("your_sandbox_client_id"):
        raise RuntimeError(
            "PayPal Sandbox client ID is missing. Set PAYPAL_CLIENT_ID in the local .env file."
        )
    return client_id


def _get_sandbox_api_base() -> str:
    api_base = os.getenv("PAYPAL_API_BASE", SANDBOX_API_BASE).rstrip("/")
    if api_base != SANDBOX_API_BASE:
        raise RuntimeError(
            "This demo only permits the PayPal Sandbox API. "
            "Set PAYPAL_API_BASE to https://api-m.sandbox.paypal.com."
        )
    return api_base


def get_paypal_access_token() -> str:
    client_id = _get_paypal_client_id()
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET", "").strip()

    if not client_secret or client_secret.lower().startswith("your_sandbox_client_secret"):
        raise RuntimeError(
            "PayPal Sandbox credentials are missing. "
            "Check your local .env file."
        )

    api_base = _get_sandbox_api_base()

    response = httpx.post(
        f"{api_base}/v1/oauth2/token",
        auth=(client_id, client_secret),
        data={"grant_type": "client_credentials"},
        headers={"Accept": "application/json"},
        timeout=20.0,
    )
    response.raise_for_status()

    return response.json()["access_token"]


def create_paypal_order(amount: str, currency: str = "USD") -> dict:
    """Create a PayPal Sandbox checkout order."""
    from decimal import Decimal, InvalidOperation

    try:
        value = Decimal(amount)
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Amount must be a valid number.")

    if not value.is_finite() or value <= 0 or value > Decimal("10000"):
        raise ValueError("Amount must be greater than 0 and at most 10000.")

    if value.as_tuple().exponent < -2:
        raise ValueError("Amount cannot have more than two decimal places.")

    if currency != "USD":
        raise ValueError("This demo currently supports USD only.")

    token = get_paypal_access_token()
    api_base = _get_sandbox_api_base()

    response = httpx.post(
        f"{api_base}/v2/checkout/orders",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": currency,
                        "value": format(value, ".2f"),
                    },
                    "description": "DriftGuard AI demo checkout",
                }
            ],
        },
        timeout=20.0,
    )
    response.raise_for_status()
    return response.json()

def capture_paypal_order(order_id: str) -> dict:
    """Capture a buyer-approved PayPal Sandbox order."""
    if not order_id or not order_id.strip():
        raise ValueError("A PayPal order ID is required.")

    token = get_paypal_access_token()
    api_base = _get_sandbox_api_base()
    safe_order_id = quote(order_id.strip(), safe="")

    response = httpx.post(
        f"{api_base}/v2/checkout/orders/{safe_order_id}/capture",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={},
        timeout=20.0,
    )
    response.raise_for_status()
    return response.json()
