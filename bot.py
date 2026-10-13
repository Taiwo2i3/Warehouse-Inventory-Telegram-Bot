from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from inventory import Inventory, InventoryItem

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Demo data is intentionally in memory. Use a database before production.
inventory = Inventory([
    InventoryItem(sku="DEMO-001", name="Demo cartons", quantity=12, low_stock_threshold=5),
    InventoryItem(sku="DEMO-002", name="Demo labels", quantity=3, low_stock_threshold=5),
])


def allowed(update: Update) -> bool:
    """Optional allow-list. Empty configuration permits all users; set it for real use."""
    configured = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").strip()
    if not configured:
        return True
    allowed_ids = {part.strip() for part in configured.split(",") if part.strip()}
    user = update.effective_user
    return bool(user and str(user.id) in allowed_ids)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "Welcome to the Warehouse Inventory Bot.\n"
            "Use /help to see commands. This starter uses temporary in-memory demo data."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "Commands:\n"
            "/stock - list current stock\n"
            "/lowstock - show items at or below threshold\n"
            "/receive SKU QUANTITY - receive stock\n"
            "/issue SKU QUANTITY - issue stock\n"
            "/help - show this help\n\n"
            "Example: /receive DEMO-001 4"
        )


async def stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    items = inventory.all_items()
    if not items:
        await update.message.reply_text("No inventory items have been added.")
        return
    lines = ["Current stock:"]
    lines.extend(
        f"- {item.sku} | {item.name} | Qty: {item.quantity} | Low-stock at: {item.low_stock_threshold}"
        for item in items
    )
    await update.message.reply_text("\n".join(lines))


async def lowstock_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        items = inventory.low_stock_items()
        if not items:
            await update.message.reply_text("Low-stock check: no alerts.")
            return
        lines = ["Low-stock alert:"]
        lines.extend(f"- {item.sku} ({item.name}): {item.quantity} remaining" for item in items)
        await update.message.reply_text("\n".join(lines))


async def _change_stock(update: Update, context: ContextTypes.DEFAULT_TYPE, receive: bool) -> None:
    if not update.message:
        return
    if not allowed(update):
        await update.message.reply_text("You are not authorised to change inventory.")
        return
    if len(context.args) != 2:
        verb = "receive" if receive else "issue"
        await update.message.reply_text(f"Usage: /{verb} SKU QUANTITY")
        return
    sku = context.args[0].strip().upper()
    try:
        quantity = int(context.args[1])
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        item = (
            inventory.receive(sku, quantity, reason="telegram receive", actor=str(update.effective_user.id if update.effective_user else "unknown"))
            if receive
            else inventory.issue(sku, quantity, reason="telegram issue", actor=str(update.effective_user.id if update.effective_user else "unknown"))
        )
    except (ValueError, KeyError) as exc:
        await update.message.reply_text(f"Could not update stock: {exc}")
        return
    action = "Received" if receive else "Issued"
    await update.message.reply_text(f"{action} {quantity} unit(s). {item.sku} now has {item.quantity}.")


async def receive_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _change_stock(update, context, receive=True)


async def issue_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _change_stock(update, context, receive=False)


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "TELEGRAM_BOT_TOKEN is missing. Copy .env.example to .env and add your bot token."
        )
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stock", stock_command))
    app.add_handler(CommandHandler("lowstock", lowstock_command))
    app.add_handler(CommandHandler("receive", receive_command))
    app.add_handler(CommandHandler("issue", issue_command))
    logger.info("Starting Warehouse Inventory Telegram Bot.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
