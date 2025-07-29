import os, json, re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7000109688
user_demo_status = {}

if os.path.exists("demo_status.json"):
    with open("demo_status.json", "r") as f:
        user_demo_status = json.load(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔹 𝐓𝐲𝐩𝐞 𝟏", callback_data="type_1")],
        [InlineKeyboardButton("🔹 𝐓𝐲𝐩𝐞 𝟐", callback_data="type_2")]
    ]
    message = """📲 𝐍𝐌𝐌𝐒 𝐌𝐎𝐃 —
Choose one

🔹 𝐓𝐲𝐩𝐞 𝟏:
   𝐖𝐨𝐫𝐤𝐞𝐫𝐬 𝐜𝐨𝐮𝐧𝐭 𝐫𝐞𝐦𝐨𝐯𝐞
   𝐃𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫 𝐨𝐩𝐭𝐢𝐨𝐧𝐬 𝐛𝐲𝐩𝐚𝐬𝐬
   𝐅𝐚𝐜𝐤 𝐥𝐨𝐜𝐚𝐭𝐢𝐨𝐧 𝐛𝐲𝐩𝐚𝐬𝐬
   𝐓𝐢𝐦𝐞 𝐜𝐡𝐚𝐧𝐠𝐞 𝐞𝐧𝐚𝐛𝐥𝐞

🔹 𝐓𝐲𝐩𝐞 𝟐:
   𝐆𝐚𝐥𝐥𝐞𝐫𝐲 𝐩𝐡𝐨𝐭𝐨 𝐮𝐩𝐥𝐨𝐚𝐝
   𝐃𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫 𝐨𝐩𝐭𝐢𝐨𝐧 𝐛𝐲𝐩𝐚𝐬𝐬
   𝐅𝐚𝐜𝐤 𝐥𝐨𝐜𝐚𝐭𝐢𝐨𝐧 𝐛𝐲𝐩𝐚𝐬𝐬
   𝐓𝐢𝐦𝐞 𝐜𝐡𝐚𝐧𝐠𝐞"""
    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    first_name = query.from_user.first_name
    data = query.data

    if data in ["type_1", "type_2"]:
        price_text = (
            "Half Month: ₹1000\nFull Month: ₹2000\nDemo: Free" if data == "type_1"
            else "Half Month: ₹1500\nFull Month: ₹2500\nDemo: Free"
        )
        plan_keyboard = [
            [InlineKeyboardButton("Half Month", callback_data=f"half_{data}")],
            [InlineKeyboardButton("Full Month", callback_data=f"full_{data}")],
            [InlineKeyboardButton("Demo", callback_data=f"demo_{data}")]
        ]
        await query.message.reply_text(
            f"Choose plan for {data.replace('_', ' ').title()}:\n{price_text}",
            reply_markup=InlineKeyboardMarkup(plan_keyboard)
        )

    elif data.startswith("demo"):
        if str(user_id) in user_demo_status:
            await query.message.reply_text("❌ Demo already taken.")
        else:
            user_demo_status[str(user_id)] = True
            with open("demo_status.json", "w") as f:
                json.dump(user_demo_status, f)
            await query.message.reply_text("⏳ Please wait while we set up your demo...")
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"👤 {first_name} ({user_id}) requested a DEMO.",
                reply_markup=ForceReply()
            )

    elif data.startswith("half") or data.startswith("full"):
        plan = "Half Month" if data.startswith("half") else "Full Month"
        mod_type = "Type 1" if "type_1" in data else "Type 2"
        await query.message.reply_text(f"✅ You selected {plan} for {mod_type}. Please wait...")
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"👤 {first_name} ({user_id}) selected {plan} for {mod_type}.",
            reply_markup=ForceReply()
        )

async def admin_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        original = update.message.reply_to_message.text
        match = re.search(r"\((\d+)\)", original)
        if match:
            user_id = int(match.group(1))
            if update.message.text:
                await context.bot.send_message(chat_id=user_id, text=f"📩 Admin: {update.message.text}")
            if update.message.document or update.message.photo or update.message.video:
                await context.bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=update.message.chat_id,
                    message_id=update.message.message_id
                )
            await update.message.reply_text("✅ Sent to user.")
        else:
            await update.message.reply_text("❌ Could not extract user ID.")

# Setup app
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_click))
app.add_handler(MessageHandler(filters.ALL & filters.REPLY, admin_reply_handler))

import asyncio
async def main():
    await app.initialize()
    await app.start()
    print("🤖 Bot is running...")
    await app.run_polling()

asyncio.run(main()
