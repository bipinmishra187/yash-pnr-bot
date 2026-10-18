
import os
import logging
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
QRAIL_API_KEY = os.environ["QRAIL_API_KEY"]
QRAIL_URL = "https://api.qrail.in/api/v1/trains/pnr/status"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "नमस्ते! 🚆 PNR Status Bot में आपका स्वागत है।\n\n"
        "PNR चेक करने के लिए:\n"
        "/pnr 1234567890\n\n"
        "/help - मदद"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "PNR चेक करने के लिए लिखें:\n/pnr 1234567890"
    )


async def pnr_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "कृपया PNR नंबर दें। उदाहरण: /pnr 1234567890"
        )
        return

    pnr = context.args[0].strip()

    if not pnr.isdigit() or len(pnr) != 10:
        await update.message.reply_text(
            "कृपया 10 अंकों का सही PNR नंबर डालें।"
        )
        return

    await update.message.reply_text("⏳ PNR स्टेटस चेक हो रहा है...")

    try:
        response = requests.post(
            QRAIL_URL,
            headers={
                "Authorization": f"Bearer {QRAIL_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"pnr": pnr},
            timeout=20,
        )

        if response.ok:
            await update.message.reply_text(
                "QRAIL API का जवाब:\n" + response.text[:3500]
            )
        else:
            log.warning("QRAIL API HTTP status: %s", response.status_code)
            await update.message.reply_text(
                f"QRAIL API ने अनुरोध स्वीकार नहीं किया "
                f"(HTTP {response.status_code})। API विवरण जाँचें।"
            )

    except requests.RequestException:
        log.exception("QRAIL request failed")
        await update.message.reply_text(
            "अभी API से संपर्क नहीं हो पाया। कृपया बाद में प्रयास करें।"
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("pnr", pnr_command))
    app.run_polling()


if __name__ == "__main__":
    main()
  
