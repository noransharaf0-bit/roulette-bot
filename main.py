import telebot
from telebot import types
import random

# ضع التوكن الخاص بك هنا بين العلامتين
TOKEN = 8245385209:AAFbYtj4vEAk5cZBA8WzLA0UchJqt1eZfBo
bot = telebot.TeleBot(TOKEN)

# تخزين بيانات الألعاب في ذاكرة البوت (خفيف جداً)
games = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    # هذا الزر يسمح بنشر الروليت في القنوات والمجموعات
    btn = types.InlineKeyboardButton("بدء لعبة روليت 🎡", switch_inline_query_current_chat="")
    markup.add(btn)
    bot.reply_to(message, "مرحباً بك في بوت الروليت!\n\nاضغط على الزر أدناه لمشاركة اللعبة في قناتك:", reply_markup=markup)

@bot.inline_handler(lambda query: True)
def query_text(inline_query):
    # إنشاء معرف فريد للعبة عند كل مشاركة
    game_id = f"g_{inline_query.from_user.id}_{random.randint(100, 999)}"
    games[game_id] = {'creator': inline_query.from_user.id, 'players': [], 'status': 'open'}
    
    markup = types.InlineKeyboardMarkup()
    btn_join = types.InlineKeyboardButton("انضمام للروليت ➕", callback_data=f"join_{game_id}")
    btn_spin = types.InlineKeyboardButton("تدوير العجلة 🎡", callback_data=f"spin_{game_id}")
    markup.add(btn_join, btn_spin)
    
    # هذه الرسالة التي ستظهر للأعضاء في القناة
    r = types.InlineQueryResultArticle(
        '1', '🎡 إرسال لعبة روليت',
        types.InputTextMessageContent(f"🎡 **بدأت لعبة روليت جديدة!**\n\nعدد المنضمين الآن: 0\nالحد الأقصى: 30 عضو"),
        reply_markup=markup,
        parse_mode="Markdown"
    )
    bot.answer_inline_query(inline_query.id, [r], cache_time=1)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data.split('_')
    action = data[0]
    game_id = f"{data[1]}_{data[2]}_{data[3]}" # إعادة تكوين معرف اللعبة

    if game_id not in games:
        bot.answer_callback_query(call.id, "عذراً، هذه اللعبة قديمة أو تم حذفها.")
        return

    # زر الانضمام
    if action == "join":
        if len(games[game_id]['players']) >= 30:
            bot.answer_callback_query(call.id, "العدد اكتمل! لا يمكن الانضمام.", show_alert=True)
            return
        
        user_id = call.from_user.id
        user_name = call.from_user.first_name
        
        # التأكد من عدم الانضمام مرتين
        if user_id in [p['id'] for p in games[game_id]['players']]:
            bot.answer_callback_query(call.id, "أنت منضم بالفعل!")
        else:
            games[game_id]['players'].append({'id': user_id, 'name': user_name})
            bot.answer_callback_query(call.id, f"تم انضمامك يا {user_name} ✅")
            
            # تحديث عدد المنضمين في الرسالة الأصلية
            count = len(games[game_id]['players'])
            markup = call.message.reply_markup if call.message else None
            bot.edit_message_text(
                f"🎡 **بدأت لعبة روليت جديدة!**\n\nعدد المنضمين الآن: {count}\nالحد الأقصى: 30 عضو",
                inline_message_id=call.inline_message_id,
                reply_markup=call.message.reply_markup if call.message else None,
                parse_mode="Markdown"
            )

    # زر تدوير العجلة
    elif action == "spin":
        # التأكد أن الشخص الذي ضغط هو من أرسل اللعبة فقط
        if call.from_user.id != games[game_id]['creator']:
            bot.answer_callback_query(call.id, "عذراً، صاحب اللعبة فقط هو من يمكنه التدوير!", show_alert=True)
            return
        
        players = games[game_id]['players']
        if len(players) < 2:
            bot.answer_callback_query(call.id, "يجب أن ينضم شخصين على الأقل للبدء!", show_alert=True)
            return

        # تدوير العجلة واختيار فائز عشوائي
        winner = random.choice(players)
        
        bot.edit_message_text(
            f"🎡 **تم تدوير العجلة بنجاح...**\n\nالفائز هو: [{winner['name']}](tg://user?id={winner['id']}) 🎉🎉",
            inline_message_id=call.inline_message_id,
            parse_mode="Markdown"
        )
        # حذف اللعبة من الذاكرة بعد الانتهاء لتوفير المساحة
        del games[game_id]

# تشغيل البوت
bot.infinity_polling()
