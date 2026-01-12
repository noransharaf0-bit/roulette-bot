from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import random

games = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("➕ ابدأ لعبة الروليت", callback_data="create_game")]]
    await update.message.reply_text("اضغط لبدء لعبة جديدة:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    data = query.data

    if data == "create_game":
        games[chat_id] = {"owner": user_id, "players": []}
        keyboard = [[InlineKeyboardButton("انضمام", callback_data="join_game")],
                    [InlineKeyboardButton("🎡 تدوير العجلة", callback_data="spin_wheel")]]
        await query.message.edit_text("🎯 *لعبة روليت جديدة!*\nاضغط انضمام للمشاركة.\nالحد: 30 لاعب.",
                                      reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if data == "join_game":
        if chat_id not in games:
            await query.answer("❌ لا توجد لعبة!")
            return
        if len(games[chat_id]["players"]) >= 30:
            await query.answer("❌ العدد مكتمل!")
            return
        if user_id in games[chat_id]["players"]:
            await query.answer("✔️ أنت منضم بالفعل!")
            return
        games[chat_id]["players"].append(user_id)
        await query.answer("تم انضمامك!")
        return

    if data == "spin_wheel":
        if chat_id not in games:
            await query.answer("❌ لا توجد لعبة!")
            return
        if games[chat_id]["owner"] != user_id:
            await query.answer("❌ فقط من أنشأ اللعبة يستطيع التدوير!")
            return
        players = games[chat_id]["players"]
        if not players:
            await query.answer("❌ لا يوجد لاعبين!")
            return
        winner = random.choice(players)
        await query.message.reply_text(f"🥳 الفائز بالروليت هو: [{winner}](tg://user?id={winner})", parse_mode="Markdown")

application = ApplicationBuilder().token(8245385209:AAFbYtj4vEAk5cZBA8WzLA0UchJqt1eZfBo).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_buttons))
application.run_polling()
