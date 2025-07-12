import telebot
from telebot import types
import time

admins = [7695954295, 6553262004]
TOKEN = "8186069801:AAFH16HooN7da4FzEwXJIACp3p9zu_MKT0o"
bot = telebot.TeleBot(TOKEN)

users = {}
pending_withdrawals = []
payment_screenshot_target = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id in admins:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📋 View Users", callback_data="view_users"))
        markup.add(types.InlineKeyboardButton("📤 Send Payment SS", callback_data="send_payment_ss"))
        markup.add(types.InlineKeyboardButton("💸 Check/Add Balance", callback_data="balance_admin"))
        markup.add(types.InlineKeyboardButton("💳 Pending Withdrawals", callback_data="pending_withdrawals"))
        markup.add(types.InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"))
        markup.add(types.InlineKeyboardButton("✅ Unban User", callback_data="unban_user"))
        bot.send_message(
            chat_id,
            """👑 Admin Panel\nSelect an action:""",
            parse_mode="Markdown",
            reply_markup=markup
        )
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add('🇬🇧 English', '🇮🇳 Hindi', '🇮🇳 Hinglish')
        bot.send_message(
            chat_id,
            """👋 Welcome to Nobita Earning Bot!

💼 Earn ₹1.5 per contact by adding members to WhatsApp groups.

Choose your language:""",
            parse_mode="Markdown",
            reply_markup=markup
        )

@bot.message_handler(func=lambda m: m.text in ['🇬🇧 English', '🇮🇳 Hindi', '🇮🇳 Hinglish'])
def set_language(message):
    chat_id = message.chat.id
    users[chat_id] = {'language': message.text, 'balance': 0, 'banned': False}
    rules = (
        """📜 Rules:\n
1️⃣ One WhatsApp number = One file.\n
2️⃣ Max 50 contacts/day/user.\n
3️⃣ Add members one by one.\n
4️⃣ Don’t delete contacts until payment.\n
⚠️ Violation = Ban.\n
💸 Payments within 24 hours."""
    )
    bot.send_message(chat_id, rules, parse_mode="Markdown")
    bot.send_message(chat_id, "✅ Type /agree to accept the rules.")

@bot.message_handler(commands=['agree'])
def agree(message):
    chat_id = message.chat.id
    if users.get(chat_id, {}).get('banned', False):
        bot.send_message(chat_id, "🚫 You are banned.")
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📹 Training Video", callback_data="training"))
    markup.add(types.InlineKeyboardButton("📁 Get File", callback_data="getfile"))
    markup.add(types.InlineKeyboardButton("💸 Withdraw Request", callback_data="withdraw"))
    markup.add(types.InlineKeyboardButton("📊 Check Balance", callback_data="balance"))
    bot.send_message(
        chat_id,
        "✅ Rules accepted!\n🎯 Main Menu:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "send_payment_ss")
def send_payment_ss(call):
    chat_id = call.message.chat.id
    if chat_id in admins:
        if not users:
            bot.send_message(chat_id, "❌ No users found to send payment screenshot.")
            return
        markup = types.InlineKeyboardMarkup()
        for user_id in users:
            markup.add(types.InlineKeyboardButton(f"User {user_id}", callback_data=f"select_user_{user_id}"))
        bot.send_message(chat_id, "👤 Select a user to send payment screenshot:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_user_"))
def select_user_for_ss(call):
    admin_id = call.message.chat.id
    user_id = int(call.data.split("_")[2])
    payment_screenshot_target[admin_id] = user_id
    bot.send_message(admin_id, f"📥 Send the payment screenshot now for User {user_id}")

@bot.message_handler(content_types=['photo'])
def handle_payment_screenshot(message):
    admin_id = message.chat.id
    if admin_id in payment_screenshot_target:
        target_user_id = payment_screenshot_target[admin_id]
        try:
            bot.send_photo(
                target_user_id,
                photo=message.photo[-1].file_id,
                caption="💸 Your payment has been processed!\n✅ Check your UPI app for confirmation.",
                parse_mode="Markdown"
            )
            bot.send_message(admin_id, "✅ Payment screenshot sent successfully.")
        except Exception as e:
            bot.send_message(admin_id, f"❌ Failed to send screenshot: {e}")
        del payment_screenshot_target[admin_id]

# ✅ Start Bot
if _name_ == "_main_":
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout = 30)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)