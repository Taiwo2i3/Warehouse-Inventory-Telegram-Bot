# Warehouse Inventory Telegram Bot

A Python Telegram bot starter for stock visibility, receiving and issuing stock, and low-stock checks.

## Commands

- `/start` — welcome message
- `/help` — list commands
- `/stock` — show inventory
- `/lowstock` — show items at or below their threshold
- `/receive SKU QUANTITY` — receive stock
- `/issue SKU QUANTITY` — issue stock

The repository includes demo SKUs so the bot can be explored without connecting to a real warehouse system.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, create a bot with Telegram's official BotFather, and place its token in `TELEGRAM_BOT_TOKEN`. Run:

```bash
python bot.py
```

Set `TELEGRAM_ALLOWED_USER_IDS` to a comma-separated list of numeric Telegram user IDs before allowing anyone to update real stock. If left empty, the demo allows all users to change its in-memory data.

## Tests

Run the inventory unit tests with:

```bash
python -m unittest discover -s tests -v
```

## Limitations before production

- Inventory is in memory and resets on restart.
- No persistent database or automatic Telegram alert delivery is connected.
- Configure and test access controls before handling real stock.
- Add durable audit logging, backups, deployment monitoring, and tests before production use.

Never commit bot tokens, warehouse records, or customer data.
