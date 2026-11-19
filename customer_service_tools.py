import json
from pathlib import Path

from strands import tool

# Load mock data from the JSON file sitting next to this script
DATA_FILE = Path(__file__).parent / "mockdata.json"
with open(DATA_FILE, encoding="utf-8") as f:
    _data = json.load(f)

CUSTOMERS = _data["CUSTOMERS"]
ORDERS = _data["ORDERS"]


@tool
def lookup_customer(customer_id: str) -> str:
    """Look up a customer by their ID.

    Args:
        customer_id: The customer ID (e.g. C-1001)
    """
    customer = CUSTOMERS.get(customer_id)
    if not customer:
        return f"No customer found with ID {customer_id}"
    return (
        f"Customer: {customer['name']}\n"
        f"Email: {customer['email']}\n"
        f"Phone: {customer['phone']}\n"
        f"Account Status: {customer['account_status']}"
    )


@tool
def get_order_history(customer_id: str) -> str:
    """Get order history for a customer.

    Args:
        customer_id: The customer ID (e.g. C-1001)
    """
    orders = ORDERS.get(customer_id)
    if not orders:
        return f"No orders found for customer {customer_id}"
    lines = []
    for order in orders:
        line = (
            f"Order {order['order_id']}: {order['item']} — ${order['amount']:.2f} "
            f"[{order['status']}] Ordered: {order['order_date']} "
        )
        if order.get("delivered_date"):
            line += f"Delivered: {order['delivered_date']} "
        if order.get("estimated_delivery"):
            line += f"Est. Delivery: {order['estimated_delivery']} "
        line += f"Tracking: {order['tracking']}"
        lines.append(line)
    return "\n".join(lines)


@tool
def process_refund(order_id: str, amount: float) -> str:
    """Process a refund for an order.

    Args:
        order_id: The order ID to refund
        amount: The refund amount in dollars
    """
    return f"Refund of ${amount:.2f} processed for order {order_id}. Expect 3-5 business days."