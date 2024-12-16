import random
import logging
import string
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
import pandas as pd

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Этапы разговора
PROMO_CODE, MAIN_MENU, CITY, NAME, INTERESTS, ADDRESS = range(6)

# Генерация промокода (8 символов, цифры и буквы)
def generate_promo_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(8))

# Начало общения
async def start(update: Update, context: CallbackContext) -> int:
    reply_markup = ReplyKeyboardMarkup([[KeyboardButton("Ввести промокод")]], one_time_keyboard=True)
    await update.message.reply_text(
        "Хо-хо-хо! 🎅 Это Тайный Санта.\n\n"
        "Чтобы принять участие в игре, пожалуйста, предъяви свой талон. 🎟\n\n"
        "Если у тебя уже есть талон — отправляй его сюда, и мы продолжим! 🎄",
        reply_markup=reply_markup
    )
    return PROMO_CODE

# Ввод промокода
async def promo_code(update: Update, context: CallbackContext) -> int:
    promo_input = update.message.text.strip()

    # Валидация промокода
    if len(promo_input) != 8 or not promo_input.isalnum():
        await update.message.reply_text("Упс! Этот талон недействителен. Попробуй ввести снова")
        return PROMO_CODE

    # Сохранение промокода
    context.user_data['promo_code'] = promo_input

    # Главное меню
    reply_markup = ReplyKeyboardMarkup([
        [KeyboardButton("Стать тайным сантой"), KeyboardButton("Личный промокод")],
        [KeyboardButton("Служба заботы эльфов"), KeyboardButton("Покормить эльфов")]
    ], one_time_keyboard=True)
    
    await update.message.reply_text(
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
async def main_menu(update: Update, context: CallbackContext) -> int:
    choice = update.message.text
    if choice == "Стать тайным сантой":
        return await city(update, context)
    elif choice == "Личный промокод":
        return await personal_promo(update, context)
    elif choice == "Служба заботы эльфов":
        return await elf_care(update, context)
    elif choice == "Покормить эльфов":
        await update.message.reply_text("Эльфы благодарят тебя за внимание! 🍪")
        return MAIN_MENU

# Выбор города
async def city(update: Update, context: CallbackContext) -> int:
    reply_markup = ReplyKeyboardMarkup([
        [KeyboardButton("🌆 Москва"), KeyboardButton("🌉 Санкт-Петербург")],
        [KeyboardButton("Главное меню")]
    ], one_time_keyboard=True)

    await update.message.reply_text("Чтобы начать, выбери город:", reply_markup=reply_markup)
    return CITY

# Обработка города
async def city_chosen(update: Update, context: CallbackContext) -> int:
    city = update.message.text
    if city == "Главное меню":
        return await main_menu(update, context)
    
    context.user_data['city'] = city
    await update.message.reply_text("Как можно к тебе обращаться?\n(Укажи Имя и Фамилию. Это необходимо для отправления подарка)")
    return NAME

# Имя
async def name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        "Расскажи о себе и своих увлечениях, чтобы твой Санта смог подготовить для тебя наилучший подарок. "
        "(Стоимость подарка ограничивается 1 500 рублей)"
    )
    return INTERESTS

# Интересы
async def interests(update: Update, context: CallbackContext) -> int:
    context.user_data['interests'] = update.message.text
    await update.message.reply_text(
        "Куда доставить твой подарок?\n"
        "Укажи всю необходимую информацию, чтобы твой Санта смог найти тебя и без проблем отправить подарок."
    )
    return ADDRESS

# Адрес
async def address(update: Update, context: CallbackContext) -> int:
    context.user_data['address'] = update.message.text
    
    # Сохраняем данные в Excel
    df = pd.DataFrame([context.user_data])
    df.to_excel("participants.xlsx", mode="a", header=False, index=False)

    await update.message.reply_text(
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
        [KeyboardButton("Личный промокод"), KeyboardButton("Покормить эльфов")],
        [KeyboardButton("Служба заботы эльфов"), KeyboardButton("Стать тайным сантой")]
    ], one_time_keyboard=True)
    
    await update.message.reply_text("Что бы вы хотели сделать дальше?", reply_markup=reply_markup)
    return MAIN_MENU

# Основная функция
def main() -> None:
    application = Application.builder().token("7454294617:AAFDXIlMmzlfZnhmToBl05dO4utSW6_Jh1Y").build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    
    # Создаем ConversationHandler
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PROMO_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, promo_code)],
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city_chosen)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            INTERESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, interests)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
        },
        fallbacks=[],
    )

    application.add_handler(conversation_handler)
    
    # Запуск бота
    application.run_polling()  # Заменили asyncio.run(main()) на application.run_polling()

if __name__ == "__main__":
    main()
