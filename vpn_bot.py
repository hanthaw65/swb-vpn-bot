
import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Bot Token (replace with your actual bot token)
TOKEN = "8269899598:AAFPgXN3sbgbxgXuxCkUWbeM1L0YavLxOQg"

# File to store user data and admin ID
USER_DATA_FILE = "user_data.json"

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"admin_id": None, "users": {}}

def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    if user_id not in user_data["users"]:
        user_data["users"][user_id] = {"first_name": update.effective_user.first_name, "last_name": update.effective_user.last_name}
        save_user_data(user_data)

    welcome_message = (
        "🔐 SWB VPN Store မှ ကြိုဆိုပါတယ်! 🔐\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "✅ မြန်ဆန်တဲ့ Speed\n"
        "✅ လုံခြုံတဲ့ Connection  \n"
        "✅ Device အားလုံးမှာ သုံးလို့ရ\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📦 အောက်က Package တစ်ခုကို ရွေးချယ်ပါ 👇"
    )

    keyboard = [
        [InlineKeyboardButton("1 Month - 4,000 MMK (100GB)", callback_data="package_1m")],
        [InlineKeyboardButton("3 Months - 11,000 MMK (300GB)", callback_data="package_3m")],
        [InlineKeyboardButton("6 Months - 22,000 MMK (600GB)", callback_data="package_6m")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    payment_details = (
        "💸 ငွေပေးချေရန် အသေးစိတ် 💸\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "KBZPay / WavePay\n"
        "ဖုန်းနံပါတ်: 09760559778\n"
        "အမည်: Han Thaw Min\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "ငွေလွှဲပြီးပါက screenshot ပို့ပေးပါ။ Admin က စစ်ဆေးပြီး VPN key ကို ပို့ပေးပါမယ်။"
    )
    await query.edit_message_text(text=payment_details)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name
    user_last_name = update.effective_user.last_name if update.effective_user.last_name else ""
    username = update.effective_user.username if update.effective_user.username else ""

    user_data = load_user_data()
    admin_id = user_data["admin_id"]

    if admin_id:
        photo_file = await update.message.photo[-1].get_file()
        caption = f"New payment screenshot from User ID: {user_id}\n"
        caption += f"Name: {user_first_name} {user_last_name}\n"
        if username: caption += f"Username: @{username}\n"
        caption += f"Chat ID: {update.effective_chat.id}"

        await context.bot.send_photo(chat_id=admin_id, photo=photo_file.file_id, caption=caption)
        await update.message.reply_text("📸 Screenshot လက်ခံရရှိပါပြီ။ Admin က စစ်ဆေးပြီး VPN key ကို 5 မိနစ်အတွင်း ပို့ပေးပါမယ်။ ကျေးဇူးတင်ပါတယ်! 🙏")
    else:
        await update.message.reply_text("Admin ကို မသတ်မှတ်ရသေးပါဘူး။ /admin command ကို အသုံးပြုပြီး admin ကို သတ်မှတ်ပေးပါ။")

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.lower()

    if "vpn" in text or "အသေးစိတ်" in text:
        await start(update, context) # Re-use start command to show package list
    elif "speed" in text or "မြန်" in text:
        await update.message.reply_text("ကျွန်တော်တို့ VPN က မြန်ဆန်တဲ့ speed ရပါတယ်။ Server location ပေါ်မူတည်ပြီး 50-100 Mbps အထိ ရနိုင်ပါတယ်။")
    elif "device" in text or "ဖုန်း" in text or "ကွန်ပျူတာ" in text:
        await update.message.reply_text("Android, iOS, Windows, Mac, Linux အားလုံးမှာ သုံးလို့ရပါတယ်။ Device 1 လုံးအတွက် key 1 ခု လိုပါတယ်။")
    elif "outline" in text:
        await update.message.reply_text("Outline VPN ဆိုတာ Google ရဲ့ Jigsaw team က ဖန်တီးထားတဲ့ လုံခြုံပြီး မြန်ဆန်တဲ့ VPN ဖြစ်ပါတယ်။ Open source ဖြစ်ပြီး ကမ္ဘာတစ်ဝှမ်း သုံးနေကြပါတယ်။")
    else:
        await update.message.reply_text("မင်္ဂလာပါ! VPN key ဝယ်ယူချင်ရင် /start နှိပ်ပါ။ မေးစရာရှိရင် မေးနိုင်ပါတယ်။")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()

    if user_data["admin_id"] is None:
        user_data["admin_id"] = user_id
        save_user_data(user_data)
        await update.message.reply_text(f"You ({user_id}) have been set as the admin.")
        logger.info(f"Admin set to: {user_id}")
    elif user_data["admin_id"] == user_id:
        await update.message.reply_text("You are already the admin.")
    else:
        await update.message.reply_text("Admin is already set. Only the current admin can change it.")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()

    if user_data["admin_id"] == user_id:
        if not context.args:
            await update.message.reply_text("Usage: /broadcast <message>")
            return

        message_to_send = " ".join(context.args)
        sent_count = 0
        for chat_id in user_data["users"]:
            try:
                await context.bot.send_message(chat_id=chat_id, text=message_to_send)
                sent_count += 1
            except Exception as e:
                logger.error(f"Could not send message to {chat_id}: {e}")
        await update.message.reply_text(f"Broadcast message sent to {sent_count} users.")
    else:
        await update.message.reply_text("You are not authorized to use this command.")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))

    logger.info("Bot started polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
