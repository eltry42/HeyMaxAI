from telegram import CallbackQuery, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
import os
import service as svc
from constants import LOGIN, SIGNUP, GUEST

def start_keyboard():
    keyboard = [[LOGIN],[SIGNUP],[GUEST]]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

def filter_keyboard():
    keyboard = [[InlineKeyboardButton("Previous", callback_data="previous"), InlineKeyboardButton("Next", callback_data="next")]]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    svc.setup_user(update.effective_chat.id, update.effective_user.id, update.effective_user.username, update.effective_user.first_name, update.effective_user.last_name)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to HeyMax Bot!", reply_markup=start_keyboard())
    return "start"

async def force_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please login, signup or continue as guest.", reply_markup=start_keyboard())
    return "start"

async def handle_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Login to HeyMax")
    return ConversationHandler.END

async def handle_signup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Signup for HeyMax")
    return ConversationHandler.END

async def handle_guest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Continue as Guest")
    return ConversationHandler.END

async def filter_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keywords = context.args
    msg = svc.filter_messages(keywords, 0)

    return_msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, reply_markup=filter_keyboard())

    msg_id = return_msg.id
    context.chat_data[msg_id] = {
        "id": msg_id,
        "offset": 0,
        "keyword": keywords
    }

    return "toggle"

async def filter_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    msg_id = query.message.id
    msg_data = context.chat_data.get(msg_id)
    if not msg_data.get("max_offset"):
        msg = svc.filter_messages(msg_data["keyword"], msg_data["offset"] + 1)
    else:
        msg = None

    if msg is None:
        msg_data["max_offset"] = True
        await query.answer("No more content")
        return "toggle"
    msg_data["offset"] += 1
    await query.answer()
    await query.edit_message_text(text=msg, reply_markup=filter_keyboard())
    return "toggle"

async def filter_previous(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    msg_id = query.message.id
    msg_data = context.chat_data.get(msg_id)
    if msg_data["offset"] == 0:
        await query.answer("No more content")
        return "toggle"
    msg = svc.filter_messages(msg_data["keyword"], max(msg_data["offset"] - 1, 0))
    msg_data["offset"] = max(msg_data["offset"] - 1, 0)
    if msg_data.get("max_offset"):
        msg_data.pop("max_offset")
    await query.answer()
    await query.edit_message_text(text=msg, reply_markup=filter_keyboard())
    return "toggle"

async def filter_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


def setup_bot():
    print("Setting up Bot...")
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    
    start_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        "start": [MessageHandler(filters.Regex(LOGIN), handle_login), MessageHandler(filters.Regex(SIGNUP), handle_signup), MessageHandler(filters.Regex(GUEST), handle_guest)],
    },
    fallbacks=[MessageHandler(filters.ALL, force_start)],
    per_message=False
    )
    application.add_handler(start_handler)

    filter_handler = ConversationHandler(
        entry_points=[CommandHandler('filter', filter_messages)],
        states={
            "toggle": [CallbackQueryHandler(filter_next, pattern="next"), CallbackQueryHandler(filter_previous, pattern="previous")],
        },
        fallbacks=[CommandHandler('filter', filter_messages), MessageHandler(filters.ALL, filter_done)],
        per_message=False
    )
    application.add_handler(filter_handler)

    return application
    
def run_bot_polling():
    application = setup_bot()
    print("Starting Bot...")    
    application.run_polling()
    print("Bot Stopped!")
