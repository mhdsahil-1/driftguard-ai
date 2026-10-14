
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.paypal_service import (
    create_paypal_order,
    capture_paypal_order,
)

router = APIRouter(prefix="/paypal", tags=["PayPal Payments"])


class CheckoutRequest(BaseModel):
    amount: float = Field(gt=0, le=10000)


class CaptureRequest(BaseModel):
    order_id: str = Field(min_length=1, max_length=100)


@router.post("/create-order")
def paypal_create_order(request: CheckoutRequest):
    try:
        order = create_paypal_order(
            amount=str(request.amount),
            currency="USD",
        )

        return {
            "order_id": order["id"],
            "status": order["status"],
            "currency": "USD",
            "amount": f"{request.amount:.2f}",
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
    try:
        result = capture_paypal_order(request.order_id)

        return {
            "order_id": result.get("id", request.order_id),
            "status": result.get("status", "UNKNOWN"),
            "message": "PayPal returned the capture result.",
        }

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail="PayPal could not capture this order. "
                   "Buyer approval may be required.",
        ) from exc

    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
