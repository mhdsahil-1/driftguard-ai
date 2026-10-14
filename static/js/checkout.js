
const SDK_URL = "https://www.paypal.com/sdk/js";

function setCheckoutStatus(message) {
  const statusElement = document.getElementById("checkout-status");
  if (statusElement) {
    statusElement.textContent = message;
  }
}

async function getCheckoutConfig() {
  const response = await fetch("/paypal/checkout-config", { cache: "no-store" });
  const data = await response.json().catch(() => ({}));

  if (!response.ok || !data.client_id) {
    throw new Error(data.detail || "PayPal Sandbox is not configured.");
  }

  return data;
}

function loadPayPalSdk(clientId) {
  if (window.paypal) {
    return Promise.resolve();
  }

  const query = new URLSearchParams({
    "client-id": clientId,
    currency: "USD",
    intent: "capture",
    components: "buttons"
  });

  return new Promise((resolve, reject) => {
    const sdkScript = document.createElement("script");
    sdkScript.src = `${SDK_URL}?${query}`;
    sdkScript.onload = resolve;
    sdkScript.onerror = () => reject(new Error("PayPal SDK failed to load."));
    document.head.append(sdkScript);
  });
}

async function initializePayPalCheckout() {
  try {
    setCheckoutStatus("Loading PayPal Sandbox checkout...");
    const config = await getCheckoutConfig();
    await loadPayPalSdk(config.client_id);

    if (!window.paypal) {
      throw new Error("PayPal SDK did not initialize.");
    }

    const container = document.getElementById("paypal-button-container");

    if (!container) {
      throw new Error("Checkout button container was not found.");
    }

    window.paypal.Buttons({
      createOrder: async () => {
        setCheckoutStatus("Creating your sandbox order...");

        const response = await fetch("/paypal/create-order", { method: "POST" });
        const data = await response.json().catch(() => ({}));

        if (!response.ok || !data.order_id) {
          throw new Error(data.detail || "Could not create the order.");
        }

        return data.order_id;
      },

      onApprove: async (data) => {
        setCheckoutStatus("Payment approved. Capturing sandbox order...");

        const response = await fetch("/paypal/capture-order", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ order_id: data.orderID })
        });
        const result = await response.json().catch(() => ({}));

        if (!response.ok || result.status !== "COMPLETED") {
          throw new Error(result.detail || "Order capture failed.");
        }

        setCheckoutStatus("Sandbox payment completed successfully.");
      },

      onCancel: () => {
        setCheckoutStatus("Checkout cancelled. No payment was captured.");
      },

      onError: (error) => {
        console.error("PayPal checkout error:", error);
        setCheckoutStatus("Checkout failed. No payment was captured.");
      }
    }).render(container);
  } catch (error) {
    console.error("PayPal checkout setup error:", error);
    setCheckoutStatus("Sandbox checkout is unavailable. Check the local configuration.");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initializePayPalCheckout();
});
