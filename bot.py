from __future__ import annotations

import logging
import os

from inventory import Inventory, InventoryItem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_demo_inventory() -> Inventory:
    """Build safe sample data; replace with a persistent repository in production."""
    return Inventory([
        InventoryItem(sku="DEMO-001", name="Demo cartons", quantity=12, low_stock_threshold=5),
        InventoryItem(sku="DEMO-002", name="Demo labels", quantity=3, low_stock_threshold=5),
    ])


def format_low_stock_alert(inventory: Inventory) -> str:
    """Format an alert message without sending it to Telegram."""
    items = inventory.low_stock_items()
    if not items:
        return "Low-stock check: no alerts."
    lines = ["Low-stock alert:"]
    lines.extend(f"- {item.sku} ({item.name}): {item.quantity} remaining" for item in items)
    return "\n".join(lines)


def handle_stock_command(command: str, inventory: Inventory) -> str:
    """Handle a tiny read-only command surface for local tests."""
    if command.strip().lower() == "/lowstock":
        return format_low_stock_alert(inventory)
    if command.strip().lower() == "/help":
        return "Commands: /help, /lowstock"
    return "Unknown command. Try /help."


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    inventory = build_demo_inventory()
    if not token:
        logger.info("No Telegram token configured; running a local placeholder check.")
        print(handle_stock_command("/lowstock", inventory))
        return
    logger.info("Token detected locally. Connect a Telegram application builder here after review.")


if __name__ == "__main__":
    main()
