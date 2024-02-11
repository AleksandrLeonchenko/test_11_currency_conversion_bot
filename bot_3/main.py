TOKEN = '6335546830:AAFojQ0Jho4qTKXUnbz2AL57wfiHxPCIoBs'
EXCHANGE_API_KEY = 'a65d431a1dccf962c4b22009'

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

# Установка уровня логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# Установка более высокого уровня логирования для httpx, чтобы избежать записи всех запросов GET и POST
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Определение состояний для машины состояний
CONVERT_AMOUNT, CONVERT_FROM, CONVERT_TO, PERFORM_CONVERSION = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Начало разговора и запрос у пользователя о его поле."""
    logger.info("Start command received.")

    await update.message.reply_text(
        "Привет! Я бот для конвертации валют. Я могу помочь тебе узнать текущий курс валюты "
        "и выполнить конвертацию среди различных валют. Для начала конвертации используй команду /convert."
        "\n\nПример использования:"
        "\n`/convert 100 USD to EUR`"
        "\n\nТакже, ты можешь использовать команду /help для получения дополнительной информации."
    )

    return CONVERT_AMOUNT


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправить сообщение с информацией о доступных командах."""
    logger.info("Help command received.")
    await update.message.reply_text(
        "Доступные команды:"
        "\n/start - Начать разговор"
        "\n/convert - Начать конвертацию валют"
        "\n/cancel - Отменить текущее действие"
        "\n/help - Получить справку о доступных командах"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        f"До свидания, {user.first_name}! Надеюсь, мы еще увидимся.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


async def convert_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Convert command received. Waiting for amount.")
    await update.message.reply_text("Введите сумму, которую вы хотите конвертировать")
    print('-----convert_amount----context----------', context)
    return CONVERT_FROM


async def convert_from(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['amount'] = float(update.message.text)
    logger.info("Amount received: %f", context.user_data['amount'])
    print('--1---convert_from----context----------', context.user_data['amount'])
    await update.message.reply_text("Введите валюту, из которой вы хотите конвертировать")
    print('--2---convert_from----context----------', context.user_data['amount'])
    return CONVERT_TO


async def convert_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['from_currency'] = update.message.text.upper()
    logger.info("From currency received: %s", context.user_data['from_currency'])
    print('--1---convert_to----context----------', context.user_data['from_currency'])
    await update.message.reply_text("Введите валюту, в которую вы хотите конвертировать")
    print('--2---convert_to----context----------', context.user_data['from_currency'])
    return PERFORM_CONVERSION


async def perform_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    from_currency = user_data['from_currency']
    logger.info("To currency received: %s", update.message.text.upper())
    print('--3---xxx----------', from_currency)
    user_data['to_currency'] = update.message.text.upper()
    logger.info("To currency received: %s", user_data['to_currency'])
    print('--3---user_data[to_currency]----------', user_data['to_currency'])

    try:
        # base_currency = 'USD'
        base_currency = from_currency
        url = f'https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/{base_currency}'

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()

        if 'conversion_rates' not in data:
            raise ValueError(f"Invalid response from the exchange rate API: {data}")

        exchange_rates = data['conversion_rates']

        if user_data['from_currency'] not in exchange_rates or user_data['to_currency'] not in exchange_rates:
            raise ValueError("Invalid currency codes")

        amount = user_data['amount']
        from_rate = exchange_rates[user_data['from_currency']]
        to_rate = exchange_rates[user_data['to_currency']]
        converted_amount = amount * (to_rate / from_rate)

        await update.message.reply_text(
            f'{amount} {user_data["from_currency"]} is equal to {converted_amount:.2f} {user_data["to_currency"]}'
        )
    except ValueError as e:
        await update.message.reply_text(f"Error: {str(e)}")

    # Переход в состояние CONVERT_AMOUNT
    return CONVERT_AMOUNT


async def greet_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветствие пользователя."""
    logger.info("Greet user message received.")
    await update.message.reply_text("Привет! Как я могу вам помочь?")


async def say_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Goodbye message received.")
    """Прощание с пользователем."""
    await update.message.reply_text("До свидания! Если у вас возникнут вопросы, обращайтесь.")


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    logging.basicConfig(
        filename='bot_logs.log',
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    # logger.info("Бот успешно запущен.")

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CONVERT_AMOUNT: [CommandHandler("convert", convert_amount)],
            CONVERT_FROM: [MessageHandler(filters.TEXT & ~filters.COMMAND, convert_from)],
            CONVERT_TO: [MessageHandler(filters.TEXT & ~filters.COMMAND, convert_to)],
            PERFORM_CONVERSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, perform_conversion)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # application.add_handler(CommandHandler("help", help_command))
    # application.add_handler(conv_handler)

    # Обработчики сообщений:
    greet_handler = MessageHandler(
        filters.Regex(r'\b(?:привет|здравствуй|добрый день)\b') | filters.Regex(r'\b(?:hello|hi|good day)\b'),
        greet_user
    )
    goodbye_handler = MessageHandler(
        filters.Regex(r'\b(?:пока|до свидания)\b') | filters.Regex(r'\b(?:bye|see|you)\b'),
        say_goodbye
    )
    # Регистрируем обработчики в приложении
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)

    application.add_handler(greet_handler)
    application.add_handler(goodbye_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
