... import random
... import string
... import logging
... from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
... from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
... import pandas as pd
... 
... # Включаем логирование
... logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
... logger = logging.getLogger(__name__)
... 
... # Этапы разговора
... PROMO_CODE, MAIN_MENU, CITY, NAME, INTERESTS, ADDRESS = range(6)
... 
... # Генерация промокода (8 символов, цифры и буквы)
... def generate_promo_code():
...     characters = string.ascii_letters + string.digits
...     return ''.join(random.choice(characters) for _ in range(8))
... 
... # Начало общения
... def start(update: Update, context: CallbackContext) -> int:
...     reply_markup = ReplyKeyboardMarkup([[KeyboardButton("Ввести промокод")]], one_time_keyboard=True)
...     update.message.reply_text(
...         "Хо-хо-хо! 🎅 Это Тайный Санта.\n\n"
...         "Чтобы принять участие в игре, пожалуйста, предъяви свой талон. 🎟\n\n"
...         "Если у тебя уже есть талон — отправляй его сюда, и мы продолжим! 🎄",
...         reply_markup=reply_markup
...     )
...     return PROMO_CODE
... 
... # Ввод промокода
... def promo_code(update: Update, context: CallbackContext) -> int:
    promo_input = update.message.text.strip()

    # Валидация промокода
    if len(promo_input) != 8 or not promo_input.isalnum():
        update.message.reply_text("Упс! Этот талон недействителен. Попробуй ввести снова")
        return PROMO_CODE

    # Сохранение промокода
    context.user_data['promo_code'] = promo_input

    # Главное меню
    reply_markup = ReplyKeyboardMarkup([
        [KeyboardButton("Стать тайным сантой"), KeyboardButton("Личный промокод")],
        [KeyboardButton("Служба заботы эльфов"), KeyboardButton("Покормить эльфов")]
    ], one_time_keyboard=True)
    
    update.message.reply_text(
        "Привет!🎄 Я — твой бот для участия в игре «Тайный Санта»! 🎅\n"
        "Моя цель — сделать этот праздник ещё ярче и теплее, ведь дарить и получать подарки всегда приятно. 🎁\n\n"
        "Регистрация открыта до 20 декабря.\n"
        "Уже 21 декабря ты узнаешь, кто станет твоим 'Тайным Сантой', и подаришь человеку радость и новые эмоции.\n\n"
        "🎉 Супербонус!\n"
        "28 декабря мы проведем розыгрыш шикарных призов среди всех участников:\n\n"
        "1. Новый iPhone 16\n"
        "2. AirPods Max\n"
        "3. Apple Watch Series 10\n"
        "А также более 20 классных подарков!\n\n"
        "✨ Участие в игре абсолютно бесплатное.\n"
        "Готов начать? Выбирай необходимое действие! 😊",
        reply_markup=reply_markup
    )
    return MAIN_MENU

# Главное меню
def main_menu(update: Update, context: CallbackContext) -> int:
    choice = update.message.text
    if choice == "Стать тайным сантой":
        return city(update, context)
    elif choice == "Личный промокод":
        return personal_promo(update, context)
    elif choice == "Служба заботы эльфов":
        return elf_care(update, context)
    elif choice == "Покормить эльфов":
        update.message.reply_text("Эльфы благодарят тебя за внимание! 🍪")
        return MAIN_MENU

# Выбор города
def city(update: Update, context: CallbackContext) -> int:
    reply_markup = ReplyKeyboardMarkup([
        [KeyboardButton("🌆 Москва"), KeyboardButton("🌉 Санкт-Петербург")],
        [KeyboardButton("Главное меню")]
    ], one_time_keyboard=True)

    update.message.reply_text("Чтобы начать, выбери город:", reply_markup=reply_markup)
    return CITY

# Обработка города
def city_chosen(update: Update, context: CallbackContext) -> int:
    city = update.message.text
    if city == "Главное меню":
        return main_menu(update, context)
    
    context.user_data['city'] = city
    update.message.reply_text("Как можно к тебе обращаться?\n(Укажи Имя и Фамилию. Это необходимо для отправления подарка)")
    return NAME

# Имя
def name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    update.message.reply_text(
        "Расскажи о себе и своих увлечениях, чтобы твой Санта смог подготовить для тебя наилучший подарок. "
        "(Стоимость подарка ограничивается 1 500 рублей)"
    )
    return INTERESTS

# Интересы
def interests(update: Update, context: CallbackContext) -> int:
    context.user_data['interests'] = update.message.text
    update.message.reply_text(
        "Куда доставить твой подарок?\n"
        "Укажи всю необходимую информацию, чтобы твой Санта смог найти тебя и без проблем отправить подарок."
    )
    return ADDRESS

# Адрес
def address(update: Update, context: CallbackContext) -> int:
    context.user_data['address'] = update.message.text
    
    # Сохраняем данные в Excel
    df = pd.DataFrame([context.user_data])
    df.to_excel("participants.xlsx", mode="a", header=False, index=False)

    update.message.reply_text(
        "Поздравляем! 🎉 Ты успешно зарегистрировался!\n"
        "Уже 21 декабря ты станешь Тайным Сантой и порадуешь своего получателя. 🎁\n"
        "Подарок нужно будет отправить до 28 декабря!\n\n"
        "🎉 Напоминаем про Супербонус!\n"
        "28 декабря мы проведем розыгрыш шикарных призов среди всех участников:\n\n"
        "1. Новый iPhone 16\n"
        "2. AirPods Max\n"
        "3. Apple Watch Series 10\n"
        "А также более 20 классных подарков!\n\n"
        "Хочешь что-то уточнить? Пиши мне в любое время эльфам! 🎄"
    )
    
    # Главное меню
    reply_markup = ReplyKeyboardMarkup([
        [KeyboardButton("Личный промокод"), KeyboardButton("Служба заботы эльфов"), KeyboardButton("Покормить эльфов")]
    ], one_time_keyboard=True)
    update.message.reply_text("Главное меню", reply_markup=reply_markup)
    
    return MAIN_MENU

# Личный промокод
def personal_promo(update: Update, context: CallbackContext) -> int:
    promo = generate_promo_code()
    context.user_data['personal_promo'] = promo
    update.message.reply_text(
        f"🎟 Твой уникальный номер промокода - {promo}\n\n"
        "Поделись этим промокодом с 5 друзьями, чтобы они тоже смогли принять участие и стать Тайными Сантами! 🎅\n\n"
        "Не упусти шанс — скорее приглашай друзей и делитесь праздничным настроением! 🎄",
        reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Скопировать промокод"), KeyboardButton("Главное меню")]
        ], one_time_keyboard=True)
    )
    return MAIN_MENU

# Служба заботы эльфов
def elf_care(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Если у тебя появились вопросы, просто напиши их сюда, и наша заботливая команда эльфов обязательно тебе поможет! 🎄✨")
    return MAIN_MENU

# Обработка текста и передача в канал
def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    user_name = update.message.from_user.full_name
    context.bot.send_message(chat_id='-1002311993514', text=f"От {user_name}: {user_message}")
    update.message.reply_text("Спасибо! Наши заботливые эльфы уже работают над решением твоего вопроса. Скоро свяжемся с тобой! 🎄✨")

# Основная функция
def main():
    # Вставь свой токен
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)

    dp = updater.dispatcher
    
    # Создаем ConversationHandler
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PROMO_CODE: [MessageHandler(Filters.text & ~Filters.command, promo_code)],
            MAIN_MENU: [MessageHandler(Filters.text & ~Filters.command, main_menu)],
            CITY: [MessageHandler(Filters.text & ~Filters.command, city_chosen)],
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
            INTERESTS: [MessageHandler(Filters.text & ~Filters.command, interests)],
            ADDRESS: [MessageHandler(Filters.text & ~Filters.command, address)],
        },
        fallbacks=[],
    )

    dp.add_handler(conversation_handler)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

TOKEN = "7454294617:AAFDXIlMmzlfZnhmToBl05dO4utSW6_Jh1Y"
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

app = Flask(__name__)

# Обработчик команды /start
def start(update, context):
    update.message.reply_text("Привет! Я ваш бот на Render!")

# Регистрируем команды
dispatcher.add_handler(CommandHandler("start", start))

# Webhook-обработка запросов от Telegram
@app.route(f"/{7454294617:AAFDXIlMmzlfZnhmToBl05dO4utSW6_Jh1Y}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
