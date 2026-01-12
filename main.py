import telebot
from telebot import types
import random

# التوكن الجديد الخاص بك
TOKEN = '8582240483:AAEgBW5nRD6ObNlKUN2jPSwyA1xDh2sKEC8'
bot = telebot.TeleBot(TOKEN)

# تخزين الألعاب النشطة
games = {}

@bot.inline_handler(lambda query: True)
def query_text(inline_query):
    try:
        # إنشاء معرف فريد لكل لعبة روليت جديدة
        game_id = f"g_{random.randint(1000, 9999)}"
        games[game_id] = {'players': [], 'status': 'open'}
        
        markup = types.InlineKeyboardMarkup()
        btn_join = types.InlineKeyboardButton("انضمام للروليت ➕", callback_data=f"join_{game_id}")
        markup.add(btn_join)
        
        # تجهيز الرسالة التي ستظهر في المحادثة
        r = types.InlineQueryResultArticle(
            id=game_id,
            title='🎡 إرسال لعبة روليت جديدة',
            description='اضغط هنا لبدء لعبة روليت في هذه المجموعة',
            input_message_content=types.InputTextMessageContent(
                "🎡 **بدأت لعبة روليت جديدة!**\n\nاضغط على الزر أدناه للانضمام.",
                parse_mode="Markdown"
            ),
            reply_markup=markup
        )
        bot.answer_inline_query(inline_query.id, [r], cache_time=1)
    except Exception as e:
        print(f"Error: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data.startswith("join_"):
        game_id = call.data.split("_")[1]
        user_name = call.from_user.first_name
        
        if game_id not in games:
            bot.answer_callback_query(call.id, "عذراً، هذه اللعبة انتهت أو غير موجودة.")
            return

        if call.from_user.id not in games[game_id]['players']:
            games[game_id]['players'].append(call.from_user.id)
            bot.answer_callback_query(call.id, f"تم انضمامك يا {user_name} ✅")
            
            # تحديث الرسالة بعدد المنضمين
            count = len(games[game_id]['players'])
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("انضمام للروليت ➕", callback_data=f"join_{game_id}"))
            
            bot.edit_message_text(
                f"🎡 **بدأت لعبة روليت جديدة!**\n\nعدد المنضمين الآن: {count}",
                inline_message_id=call.inline_message_id,
                reply_markup=markup,
                parse_mode="Markdown"
            )
        else:
            bot.answer_callback_query(call.id, "أنت منضم بالفعل! ⚠️")

# تشغيل البوت
print("Bot is running...")
bot.infinity_polling()
