import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import app
from routes import payments
from services import paypal_service


class CheckoutTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        with payments._issued_orders_lock:
            payments._issued_order_ids.clear()

    def test_checkout_page_and_script_are_served(self):
        checkout = self.client.get("/checkout")
        self.assertEqual(checkout.status_code, 200)
        self.assertIn('src="/static/js/checkout.js"', checkout.text)
        self.assertNotIn("YOUR_SANDBOX_CLIENT_ID", checkout.text)

        script = self.client.get("/static/js/checkout.js")
        self.assertEqual(script.status_code, 200)
        self.assertIn("/paypal/checkout-config", script.text)

    @patch("routes.payments.get_paypal_checkout_config")
    def test_checkout_config_exposes_only_client_id(self, mock_checkout_config):
        mock_checkout_config.return_value = {"client_id": "sandbox-client-id"}

        response = self.client.get("/paypal/checkout-config")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"client_id": "sandbox-client-id"})

    def test_checkout_config_rejects_non_sandbox_api(self):
        with patch.dict(
            os.environ,
            {"PAYPAL_API_BASE": "https://api-m.paypal.com"},
            clear=False,
        ):
            with self.assertRaisesRegex(RuntimeError, "only permits the PayPal Sandbox API"):
                paypal_service.get_paypal_checkout_config()

    @patch("routes.payments.create_paypal_order")
    def test_create_order_uses_server_side_demo_amount(self, mock_create_order):
        mock_create_order.return_value = {"id": "TESTORDER", "status": "CREATED"}

        response = self.client.post("/paypal/create-order", json={"amount": "0.01"})

        self.assertEqual(response.status_code, 200)
        mock_create_order.assert_called_once_with(amount="10.00", currency="USD")
        self.assertEqual(response.json()["amount"], "10.00")

    def test_capture_rejects_order_not_created_by_this_process(self):
        response = self.client.post("/paypal/capture-order", json={"order_id": "UNKNOWN"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("did not create", response.json()["detail"])

    
    @patch("routes.payments.capture_paypal_order")
    def test_capture_requires_completed_paypal_result(self, mock_capture_order):
        with payments._issued_orders_lock:
            payments._issued_order_ids.add("TESTORDER")

        mock_capture_order.return_value = {
            "id": "TESTORDER",
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "payments": {
                        "captures": [
                            {
                                "status": "COMPLETED",
                                "amount": {
                                    "currency_code": "USD",
                                    "value": "10.00",
                                },
                            }
                        ]
                    }
                }
            ],
        }

        response = self.client.post(
            "/paypal/capture-order",
            json={"order_id": "TESTORDER"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "COMPLETED")
        self.assertEqual(response.json()["amount"], "10.00")
        self.assertEqual(response.json()["currency"], "USD")



if __name__ == "__main__":
    unittest.main()
