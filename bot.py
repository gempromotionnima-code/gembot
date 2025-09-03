
import json
import logging
import os
from typing import Dict, List
import html

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, Defaults

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

DATA_FILE = "نمایندگان.json"
BOT_TOKEN = os.getenv("BOT_TOKEN", "")


def load_data() -> Dict[str, List[Dict[str, str]]]:
    if not os.path.exists(DATA_FILE):
        logger.error("Data file not found: %s", DATA_FILE)
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


data_by_province = load_data()


def normalize_phone(raw: str) -> str:
    digits = "".join(ch for ch in (raw or "") if ch.isdigit())
    return digits


def format_rep(rep: Dict[str, str]) -> str:
    name = html.escape(rep.get("نام", "-") or "-")
    store = html.escape(rep.get("فروشگاه", "-") or "-")
    phone = (rep.get("شماره", "-") or "-").strip()
    phone_display = html.escape(phone)
    phone_link = normalize_phone(phone)
    if phone_link:
        phone_html = f"<a href=\"tel:{phone_link}\">{phone_display}</a>"
    else:
        phone_html = phone_display
    return f"نام: {name}\nفروشگاه: {store}\nشماره: {phone_html}"


def build_provinces_keyboard() -> InlineKeyboardMarkup:
    provinces_list = sorted(list(data_by_province.keys()))
    # Create buttons, 3 per row
    rows: List[List[InlineKeyboardButton]] = []
    current_row: List[InlineKeyboardButton] = []
    for prov in provinces_list:
        btn = InlineKeyboardButton(text=prov, callback_data=f"prov:{prov}")
        current_row.append(btn)
        if len(current_row) == 3:
            rows.append(current_row)
            current_row = []
    if current_row:
        rows.append(current_row)
    return InlineKeyboardMarkup(rows)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not data_by_province:
        await update.message.reply_text("داده‌ای موجود نیست.")
        return
    await update.message.reply_text(
        "استان خود را انتخاب کنید:", reply_markup=build_provinces_keyboard()
    )


async def provinces(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not data_by_province:
        await update.message.reply_text("داده‌ای موجود نیست.")
        return
    await update.message.reply_text(
        "استان‌ها:", reply_markup=build_provinces_keyboard()
    )


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("لطفاً نام استان را وارد کنید. مثال: /search تهران")
        return
    province = " ".join(context.args).strip()
    await send_province_reps(update, province)


async def send_province_reps(update_or_query, province: str) -> None:
    reps = data_by_province.get(province)
    if not reps:
        text = "چیزی یافت نشد. نام استان را دقیق وارد کنید."
        if hasattr(update_or_query, "message") and update_or_query.message:
            await update_or_query.message.reply_text(text)
        else:
            await update_or_query.edit_message_text(text)
        return
    chunks: List[str] = []
    for rep in reps:
        chunks.append(format_rep(rep))
    text = (f"نمایندگان استان {html.escape(province)}:\n\n" + "\n\n".join(chunks))
    # Telegram message limit safety
    if hasattr(update_or_query, "message") and update_or_query.message:
        for i in range(0, len(text), 3500):
            await update_or_query.message.reply_text(text[i:i+3500])
    else:
        # In callback, edit first message and then send extra parts if needed
        await update_or_query.edit_message_text(text[:3500])
        extra = text[3500:]
        while extra:
            await update_or_query.message.reply_text(extra[:3500])
            extra = extra[3500:]


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    data = query.data or ""
    if data.startswith("prov:"):
        province = data.split(":", 1)[1]
        await send_province_reps(query, province)


def main() -> None:
    token = BOT_TOKEN or os.getenv("TELEGRAM_BOT_TOKEN") or ""
    if not token:
        token = ""
    application = Application.builder().token(token).defaults(Defaults(parse_mode=ParseMode.HTML)).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("provinces", provinces))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CallbackQueryHandler(on_callback))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
