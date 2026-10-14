
from decimal import Decimal
from threading import Lock

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.paypal_service import (
    create_paypal_order,
    capture_paypal_order,
    get_paypal_checkout_config,
)

router = APIRouter(prefix="/paypal", tags=["PayPal Payments"])
DEMO_AMOUNT = Decimal("10.00")
DEMO_CURRENCY = "USD"
_issued_order_ids: set[str] = set()
_issued_orders_lock = Lock()


class CaptureRequest(BaseModel):
    order_id: str = Field(min_length=1, max_length=100)


@router.get("/checkout-config", include_in_schema=False)
def paypal_checkout_config():
    """Expose only the public Sandbox client ID needed by the browser SDK."""
    try:
        return get_paypal_checkout_config()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/create-order")
def paypal_create_order():
    try:
        order = create_paypal_order(
            amount=str(DEMO_AMOUNT),
            currency=DEMO_CURRENCY,
        )
        order_id = order["id"]

        with _issued_orders_lock:
            _issued_order_ids.add(order_id)

        return {
            "order_id": order_id,
            "status": order["status"],
            "currency": DEMO_CURRENCY,
            "amount": format(DEMO_AMOUNT, ".2f"),
            "message": "Sandbox order created. Buyer approval is required.",
        }

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail="PayPal rejected the order request.",
        ) from exc

    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/capture-order")
def paypal_capture_order(request: CaptureRequest):
    order_id = request.order_id.strip()

    with _issued_orders_lock:
        if order_id not in _issued_order_ids:
            raise HTTPException(
                status_code=400,
                detail="This checkout session did not create that order.",
            )
        _issued_order_ids.remove(order_id)

    try:
        result = capture_paypal_order(order_id)

        if result.get("status") != "COMPLETED":
            raise RuntimeError("PayPal did not complete the order capture.")

        return {
            "order_id": result.get("id", order_id),
            "status": "COMPLETED",
            "message": "Sandbox payment completed successfully.",
        }

    except httpx.HTTPStatusError as exc:
        with _issued_orders_lock:
            _issued_order_ids.add(order_id)
        raise HTTPException(
            status_code=502,
            detail="PayPal could not capture this order. "
                   "Buyer approval may be required.",
        ) from exc

    except (RuntimeError, ValueError) as exc:
        with _issued_orders_lock:
            _issued_order_ids.add(order_id)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
