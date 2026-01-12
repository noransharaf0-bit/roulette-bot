import telebot
from telebot import types
import random

TOKEN = '8245385209:AAFbYtj4vEAk5cZBA8WzLA0UchJqt1eZfBo'
bot = telebot.TeleBot(TOKEN)
games = {}

@bot.inline_handler(lambda query: True)
def query_text(inline_query):
    game_id = f"g_{inline_query.from_user.id}_{random.randint(100, 999)}"
    games[game_id] = {'players': [], 'status': 'open'}
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("انضمام للروليت ➕", callback_data=f"join_{game_id}"))
    
    r = types.InlineQueryResultArticle(
        id=game_id, 
        title='🎡 إرسال لعبة روليت',
        input_message_content=types.InputTextMessageContent(f"🎡 **بدأت لعبة روليت جديدة!**\n\nعدد المنضمين: 0", parse_mode="Markdown"),
        reply_markup=markup
    )
    bot.answer_inline_query(inline_query.id, [r], cache_time=1)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # كود معالجة الضغطات سيعمل هنا
    pass

bot.infinity_polling()
