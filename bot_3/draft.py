import logging

import httpx
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

TOKEN = '6335546830:AAFojQ0Jho4qTKXUnbz2AL57wfiHxPCIoBs'
EXCHANGE_API_KEY = 'a65d431a1dccf962c4b22009'

import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Установка уровня логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# Установка более высокого уровня логирования для httpx, чтобы избежать записи всех запросов GET и POST
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Определение состояний для машины состояний
# GENDER, CONVERT, PHOTO, LOCATION, BIO = range(5)
GENDER, PHOTO, LOCATION, BIO = range(4)
CONVERT_AMOUNT, CONVERT_FROM, CONVERT_TO, PERFORM_CONVERSION = range(4, 8)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало разговора и запрос у пользователя о его поле."""
    reply_keyboard = [["Boy", "Girl", "Other"]]

    await update.message.reply_text(
        "Hi! My name is Professor Bot. I will hold a conversation with you. "
        "Send /cancel to stop talking to me.\n\n"
        "Are you a boy or a girl?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Boy or Girl?"
        ),
    )

    return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохранение выбранного пола и запрос фотографии."""
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "I see! Please send me a photo of yourself, "
        "so I know what you look like, or send /skip if you don't want to.",
        reply_markup=ReplyKeyboardRemove(),
    )

    # return PHOTO
    # return CONVERT
    return CONVERT_AMOUNT

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохранение фотографии и запрос местоположения."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("user_photo.jpg")
    logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg")
    await update.message.reply_text(
        "Gorgeous! Now, send me your location please, or send /skip if you don't want to."
    )

    return LOCATION

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Пропуск запроса фотографии и запрос местоположения."""
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    await update.message.reply_text(
        "I bet you look great! Now, send me your location please, or send /skip."
    )

    return LOCATION

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохранение местоположения и запрос информации о пользователе."""
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    await update.message.reply_text(
        "Maybe I can visit you sometime! At last, tell me something about yourself."
    )

    return BIO

async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Пропуск запроса местоположения и запрос информации о пользователе."""
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    await update.message.reply_text(
        "You seem a bit paranoid! At last, tell me something about yourself."
    )

    return BIO

async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохранение информации о пользователе и завершение разговора."""
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text("Thank you! I hope we can talk again some day.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена и завершение разговора."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END





async def convert_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите сумму, которую вы хотите конвертировать")
    print('-----convert_amount----context----------', context)
    return CONVERT_FROM

async def convert_from(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['amount'] = float(update.message.text)
    print('--1---convert_from----context----------', context.user_data['amount'])
    await update.message.reply_text("Введите валюту, из которой вы хотите конвертировать")
    print('--2---convert_from----context----------', context.user_data['amount'])
    return CONVERT_TO

async def convert_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['from_currency'] = update.message.text.upper()
    print('--1---convert_to----context----------', context.user_data['from_currency'])
    await update.message.reply_text("Введите валюту, в которую вы хотите конвертировать")
    print('--2---convert_to----context----------', context.user_data['from_currency'])
    return PERFORM_CONVERSION

# async def perform_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_data = context.user_data
#     user_data['to_currency'] = update.message.text.upper()
#     print('--1---perform_conversion----user_data----------', user_data)
#     print('--1---perform_conversion----user_data[to_currency]----------', user_data['to_currency'])
#
#     try:
#         # Выполняем запрос к API для получения актуального курса валют
#         url = 'https://open.er-api.com/v6/latest'
#         params = {'api_key': EXCHANGE_API_KEY}
#
#         async with httpx.AsyncClient() as client:
#             response = await client.get(url, params=params)
#             data = response.json()
#
#         if 'conversion_rates' not in data:
#             raise ValueError(f"Invalid response from the exchange rate API: {data}")
#
#         exchange_rates = data['conversion_rates']
#
#         # Проверяем, есть ли валюты в ответе API
#         if user_data['from_currency'] not in exchange_rates or user_data['to_currency'] not in exchange_rates:
#             raise ValueError("Invalid currency codes")
#
#         # Проводим конвертацию
#         amount = user_data['amount']
#         from_rate = exchange_rates[user_data['from_currency']]
#         to_rate = exchange_rates[user_data['to_currency']]
#         converted_amount = amount * (to_rate / from_rate)
#
#         # Отправляем результат пользователю
#         await update.message.reply_text(
#             f'{amount} {user_data["from_currency"]} is equal to {converted_amount:.2f} {user_data["to_currency"]}'
#         )
#     except ValueError as e:
#         # В случае ошибки отправляем сообщение об ошибке
#         await update.message.reply_text(f"Error: {str(e)}")
#
#     return GENDER


async def perform_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    user_data['to_currency'] = update.message.text.upper()

    try:
        # Выполняем запрос к API для получения актуального курса валют
        base_currency = 'USD'  # Указываем базовую валюту (из которой конвертируем)
        url = f'https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/{base_currency}'

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()

        if 'conversion_rates' not in data:
            raise ValueError(f"Invalid response from the exchange rate API: {data}")

        exchange_rates = data['conversion_rates']

        # Проверяем, есть ли валюты в ответе API
        if user_data['from_currency'] not in exchange_rates or user_data['to_currency'] not in exchange_rates:
            raise ValueError("Invalid currency codes")

        # Проводим конвертацию
        amount = user_data['amount']
        from_rate = exchange_rates[user_data['from_currency']]
        to_rate = exchange_rates[user_data['to_currency']]
        converted_amount = amount * (to_rate / from_rate)

        # Отправляем результат пользователю
        await update.message.reply_text(
            f'{amount} {user_data["from_currency"]} is equal to {converted_amount:.2f} {user_data["to_currency"]}'
        )
    except ValueError as e:
        # В случае ошибки отправляем сообщение об ошибке
        await update.message.reply_text(f"Error: {str(e)}")

    return GENDER


def main() -> None:
    # Создание приложения и передача ему токена вашего бота.
    application = Application.builder().token(TOKEN).build()

    # Добавление обработчика разговора с состояниями GENDER, PHOTO, LOCATION, BIO и CONVERT_AMOUNT, CONVERT_FROM, CONVERT_TO

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [MessageHandler(filters.Regex("^(Boy|Girl|Other)$"), gender)],
            PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_photo)],
            LOCATION: [
                MessageHandler(filters.LOCATION, location),
                CommandHandler("skip", skip_location),
            ],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
            CONVERT_AMOUNT: [CommandHandler("convert", convert_amount)],
            # CONVERT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, convert_amount)],
            CONVERT_FROM: [MessageHandler(filters.TEXT & ~filters.COMMAND, convert_from)],
            CONVERT_TO: [MessageHandler(filters.TEXT & ~filters.COMMAND, convert_to)],
            PERFORM_CONVERSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, perform_conversion)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Запуск бота до тех пор, пока пользователь не нажмет Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)



if __name__ == "__main__":
    main()
