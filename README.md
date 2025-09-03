
# Telegram Bot for نمایندگان

A simple Telegram bot that lists representatives from `نمایندگان.json`.

## Commands
- `/start` – help message
- `/provinces` – list all provinces
- `/search <استان>` – show representatives for a province (e.g., `/search تهران`)

## Local Setup
1. Install Python 3.10+
2. Create a virtualenv (optional)
3. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
4. Set environment variable:
   ```bash
   $env:BOT_TOKEN="<YOUR_TELEGRAM_BOT_TOKEN>"   # PowerShell
   # or
   export BOT_TOKEN="<YOUR_TELEGRAM_BOT_TOKEN>"  # bash
   ```
5. Run:
   ```bash
   python bot.py
   ```

## Deploy to GitHub and Render
1. Commit and push this repo to GitHub.
2. On Render:
   - New → Worker
   - Connect your repo
   - Render will detect `render.yaml`
   - Set env var `BOT_TOKEN` to your Telegram bot token
   - Deploy

## Notes
- Data source is `نمایندگان.json`. Update it and redeploy to refresh data.
- Bot uses long polling via `python-telegram-bot` v21.
