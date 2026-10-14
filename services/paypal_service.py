
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

PAYPAL_API_BASE = os.getenv(
    "PAYPAL_API_BASE",
    "https://api-m.sandbox.paypal.com",
).rstrip("/")


def get_paypal_access_token() -> str:
    client_id = os.getenv("PAYPAL_CLIENT_ID")
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError(
            "PayPal Sandbox credentials are missing. "
            "Check your local .env file."
        )

    response = httpx.post(
        f"{PAYPAL_API_BASE}/v1/oauth2/token",
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

    response = httpx.post(
        f"{PAYPAL_API_BASE}/v2/checkout/orders",
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

    response = httpx.post(
        f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={},
        timeout=20.0,
    )
    response.raise_for_status()
    return response.json()
