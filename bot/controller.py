from telegram import CallbackQuery, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler
import os
import service as svc

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Start")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = svc.get_status()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")


def setup_bot():
    print("Setting up Bot...")
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    
    # TODO: Convert to conversation handler
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    status_handler = CommandHandler('status', status)
    application.add_handler(status_handler)

    return application
    
def run_bot_polling():
    application = setup_bot()
    print("Starting Bot...")    
    application.run_polling()
