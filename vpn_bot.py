
import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

TOKEN = "8269899598:AAFPgXN3sbgbxgXuxCkUWbeM1L0YavLxOQg"

USER_DATA_FILE = "user_data.json"

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"admin_id": None, "users": {}}

def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_main_menu_keyboard():
    keyboard = [
        [KeyboardButton("📦 Package ရွေးမယ်"), KeyboardButton("📖 အသုံးပြုနည်း")],
        [KeyboardButton("💰 ဈေးနှုန်း"), KeyboardButton("❓ မေးခွန်းမေးမယ်")],
        [KeyboardButton("📞 ဆက်သွယ်ရန်")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

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
        "✅ လုံခြုံတဲ့ Connection\n"
        "✅ Device အားလုံးမှာ သုံးလို့ရ\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "အောက်က Menu ကနေ ရွေးချယ်ပါ 👇"
    )

    await update.message.reply_text(welcome_message, reply_markup=get_main_menu_keyboard())

async def show_packages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("1 Month - 4,000 MMK (100GB)", callback_data="package_1m")],
        [InlineKeyboardButton("3 Months - 11,000 MMK (300GB)", callback_data="package_3m")],
        [InlineKeyboardButton("6 Months - 22,000 MMK (600GB)", callback_data="package_6m")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    package_text = (
        "📦 Package & ဈေးနှုန်း\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "▪️ 1 Month = 4,000 MMK (100GB)\n"
        "▪️ 3 Months = 11,000 MMK (300GB)\n"
        "▪️ 6 Months = 22,000 MMK (600GB)\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "ဝယ်ယူချင်တဲ့ Package ကို နှိပ်ပါ 👇"
    )

    await update.message.reply_text(package_text, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    package_info = {
        "package_1m": "1 Month - 4,000 MMK (100GB)",
        "package_3m": "3 Months - 11,000 MMK (300GB)",
        "package_6m": "6 Months - 22,000 MMK (600GB)",
    }

    selected = package_info.get(query.data, "")

    payment_details = (
        f"✅ ရွေးချယ်ထားသော Package: {selected}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💳 ငွေပေးချေရန်\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "KBZPay / WavePay\n"
        "📱 09760559778\n"
        "👤 Han Thaw Min\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "ငွေလွှဲပြီးပါက screenshot ကို ဒီ chat ထဲ ပို့ပေးပါ။\n"
        "Admin က စစ်ဆေးပြီး VPN key ကို 5 မိနစ်အတွင်း ပို့ပေးပါမယ်။ 🚀"
    )
    await query.edit_message_text(text=payment_details)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name
    user_last_name = update.effective_user.last_name if update.effective_user.last_name else ""
    username = update.effective_user.username if update.effective_user.username else ""

    user_data = load_user_data()
    admin_id = user_data["admin_id"]

    # Admin replying with photo to customer
    if str(user_id) == admin_id and update.message.reply_to_message:
        replied_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
        customer_chat_id = None
        for line in replied_text.split("\n"):
            if "Chat ID:" in line:
                try:
                    customer_chat_id = line.split("Chat ID:")[1].strip()
                except:
                    pass
        if customer_chat_id:
            try:
                photo_file = update.message.photo[-1].file_id
                caption = update.message.caption if update.message.caption else ""
                await context.bot.send_photo(chat_id=customer_chat_id, photo=photo_file, caption=caption)
                await update.message.reply_text("✅ Customer ဆီ ပုံ ပို့ပြီးပါပြီ။")
            except Exception as e:
                await update.message.reply_text(f"❌ ပို့လို့မရပါ: {e}")
            return

    if admin_id:
        photo_file = await update.message.photo[-1].get_file()
        caption = f"💰 Payment Screenshot\n"
        caption += f"━━━━━━━━━━━━━━━━━━\n"
        caption += f"👤 Name: {user_first_name} {user_last_name}\n"
        if username: caption += f"📎 Username: @{username}\n"
        caption += f"🆔 User ID: {user_id}\n"
        caption += f"💬 Chat ID: {update.effective_chat.id}"

        await context.bot.send_photo(chat_id=admin_id, photo=photo_file.file_id, caption=caption)
        await update.message.reply_text("📸 Screenshot လက်ခံရရှိပါပြီ။ Admin က စစ်ဆေးပြီး VPN key ကို 5 မိနစ်အတွင်း ပို့ပေးပါမယ်။ ကျေးဇူးတင်ပါတယ်! 🙏")
    else:
        await update.message.reply_text("⚠️ Admin ကို မသတ်မှတ်ရသေးပါဘူး။")

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    admin_id = user_data.get("admin_id")

    # Admin reply to customer
    if user_id == admin_id and update.message.reply_to_message:
        replied_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
        customer_chat_id = None
        for line in replied_text.split("\n"):
            if "Chat ID:" in line:
                try:
                    customer_chat_id = line.split("Chat ID:")[1].strip()
                except:
                    pass
        if customer_chat_id:
            try:
                await context.bot.send_message(chat_id=customer_chat_id, text=text)
                await update.message.reply_text("✅ Customer ဆီ ပို့ပြီးပါပြီ။")
            except Exception as e:
                await update.message.reply_text(f"❌ ပို့လို့မရပါ: {e}")
            return

    # Menu button handlers
    if text == "📦 Package ရွေးမယ်" or text == "💰 ဈေးနှုန်း":
        await show_packages(update, context)
        return
    
    if text == "📖 အသုံးပြုနည်း":
        usage_guide = (
            "VPN အသုံးပြုနည်း👇\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "🔽 App ကို download လုပ်ပါ\n"
            "Android: https://play.google.com/store/apps/details?id=org.outline.android.client\n"
            "iPhone: https://itunes.apple.com/app/outline-app/id1356177741\n\n"
            "🔑 အသုံးပြုနည်း\n"
            "1. App ကိုဖွင့်ပါ\n"
            "2. Add Server ကိုနှိပ်ပါ\n"
            "3. VPN Key ကို paste လုပ်ပါ\n"
            "4. Connect ကိုနှိပ်ပါ\n\n"
            "Connected ဖြစ်ရင် အသုံးပြုနိုင်ပါပြီ။ ✅"
        )
        await update.message.reply_text(usage_guide)
        return

    if text == "❓ မေးခွန်းမေးမယ်":
        faq_text = (
            "❓ မေးလေ့ရှိတဲ့ မေးခွန်းများ\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "🔹 Speed ဘယ်လောက်ရလဲ?\n"
            "→ Server ပေါ်မူတည်ပြီး 50-100 Mbps ရပါတယ်\n\n"
            "🔹 ဘယ် Device တွေမှာ သုံးလို့ရလဲ?\n"
            "→ Android, iOS, Windows, Mac, Linux အကုန်ရပါတယ်\n\n"
            "🔹 Outline VPN ဆိုတာ ဘာလဲ?\n"
            "→ Google ရဲ့ Jigsaw team ဖန်တီးထားတဲ့ လုံခြုံတဲ့ VPN ပါ\n\n"
            "🔹 Key ဘယ်နှစ်ခါ သုံးလို့ရလဲ?\n"
            "→ Device 1 လုံးအတွက် key 1 ခု လိုပါတယ်\n\n"
            "တခြား မေးစရာရှိရင် ဒီ chat ထဲမှာ တိုက်ရိုက် မေးနိုင်ပါတယ်! 😊"
        )
        await update.message.reply_text(faq_text)
        return

    if text == "📞 ဆက်သွယ်ရန်":
        contact_text = (
            "📞 ဆက်သွယ်ရန်\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "📱 Telegram: @hanthawmin\n"
            "📱 Viber: 09781704651\n"
            "📢 Channel: @smartworkburmese\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "မေးစရာရှိရင် အချိန်မရွေး ဆက်သွယ်နိုင်ပါတယ်! 🙏"
        )
        await update.message.reply_text(contact_text)
        return

    # Auto reply for text messages
    text_lower = text.lower()

    if "အသုံးပြုနည်း" in text or "သုံးနည်း" in text or "how to use" in text:
        usage_guide = (
            "VPN အသုံးပြုနည်း👇\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "🔽 App ကို download လုပ်ပါ\n"
            "Android: https://play.google.com/store/apps/details?id=org.outline.android.client\n"
            "iPhone: https://itunes.apple.com/app/outline-app/id1356177741\n\n"
            "🔑 အသုံးပြုနည်း\n"
            "1. App ကိုဖွင့်ပါ\n"
            "2. Add Server ကိုနှိပ်ပါ\n"
            "3. VPN Key ကို paste လုပ်ပါ\n"
            "4. Connect ကိုနှိပ်ပါ\n\n"
            "Connected ဖြစ်ရင် အသုံးပြုနိုင်ပါပြီ။ ✅"
        )
        await update.message.reply_text(usage_guide)
    elif "vpn" in text_lower or "အသေးစိတ်" in text or "package" in text_lower or "ဈေး" in text:
        await show_packages(update, context)
    elif "speed" in text_lower or "မြန်" in text:
        await update.message.reply_text("ကျွန်တော်တို့ VPN က မြန်ဆန်တဲ့ speed ရပါတယ်။ Server location ပေါ်မူတည်ပြီး 50-100 Mbps အထိ ရနိုင်ပါတယ်။ 🚀")
    elif "device" in text_lower or "ဖုန်း" in text or "ကွန်ပျူတာ" in text:
        await update.message.reply_text("Android, iOS, Windows, Mac, Linux အားလုံးမှာ သုံးလို့ရပါတယ်။ Device 1 လုံးအတွက် key 1 ခု လိုပါတယ်။ 📱💻")
    elif "outline" in text_lower:
        await update.message.reply_text("Outline VPN ဆိုတာ Google ရဲ့ Jigsaw team က ဖန်တီးထားတဲ့ လုံခြုံပြီး မြန်ဆန်တဲ့ VPN ဖြစ်ပါတယ်။ Open source ဖြစ်ပြီး ကမ္ဘာတစ်ဝှမ်း သုံးနေကြပါတယ်။ 🌍")
    else:
        await update.message.reply_text("မင်္ဂလာပါ! 🙏\nVPN key ဝယ်ယူချင်ရင် အောက်က Menu ကနေ ရွေးချယ်နိုင်ပါတယ်။\nမေးစရာရှိရင် မေးနိုင်ပါတယ်။", reply_markup=get_main_menu_keyboard())

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_data = load_user_data()

    if user_data["admin_id"] is None:
        user_data["admin_id"] = user_id
        save_user_data(user_data)
        await update.message.reply_text(f"✅ You ({user_id}) have been set as the admin.")
        logger.info(f"Admin set to: {user_id}")
    elif user_data["admin_id"] == user_id:
        await update.message.reply_text("✅ You are already the admin.")
    else:
        await update.message.reply_text("⛔ Admin is already set. Only the current admin can change it.")

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
        await update.message.reply_text(f"✅ Broadcast message sent to {sent_count} users.")
    else:
        await update.message.reply_text("⛔ You are not authorized to use this command.")

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
