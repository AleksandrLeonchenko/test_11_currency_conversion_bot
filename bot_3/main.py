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

from bot_3.config import TOKEN, EXCHANGE_API_KEY


token = TOKEN
api_key = EXCHANGE_API_KEY

# Установка уровня логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Определение состояний для машины состояний
CONVERT_AMOUNT, CONVERT_FROM, CONVERT_TO, PERFORM_CONVERSION = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Начало разговора и запрос у пользователя о его поле.

    Возвращает:
    - int: Состояние машины состояний - ожидание ввода суммы.
    """
    logger.info("Start command received.")

    await update.message.reply_text(
        "Привет! Я бот для конвертации валют. Я могу помочь тебе узнать текущий курс валюты "
        "и выполнить конвертацию среди различных валют. Для начала конвертации используй команду /convert."
        "\n\nПример использования:"
        "\n`/convert`"
        "\nдалее вводи сумму для конвертирования, например 100"
        "\nдалее вводи валюту, из которой нужно конвертировать, например USD"
        "\nдалее вводи валюту, в которую нужно конвертировать, например RUB"
        "\n\nТакже, ты можешь использовать команду /help для получения списка команд "
        "\nи команду /cancel отмены текущего действия."
    )
    return CONVERT_AMOUNT


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправить сообщение с информацией о доступных командах.

    Параметры:
    - update: Update, объект с информацией о сообщении.
    - context: ContextTypes.DEFAULT_TYPE, объект с информацией о контексте.

    Возвращает:
    - None
    """
    logger.info("Help command received.")
    await update.message.reply_text(
        "Доступные команды:"
        "\n/start - Запуск бота"
        "\n/convert - Начать конвертацию валют"
        "\n/cancel - Отменить текущее действие"
        "\n/help - Получить справку о доступных командах"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Отменить текущее действие и попрощаться с пользователем.

    Параметры:
    - update: Update, объект с информацией о сообщении.
    - context: ContextTypes.DEFAULT_TYPE, объект с информацией о контексте.

    Возвращает:
    - int: Состояние машины состояний - конец разговора.
    """
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        f"До свидания, {user.first_name}! Надеюсь, мы еще увидимся.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def greet_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Приветствие пользователя.

    Параметры:
    - update: Update, объект с информацией о сообщении.
    - context: ContextTypes.DEFAULT_TYPE, объект с информацией о контексте.

    Возвращает:
    - None
    """
    logger.info("Greet user message received.")
    await update.message.reply_text("Привет! Как я могу вам помочь?")


async def say_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Прощание с пользователем.

    Параметры:
    - update: Update, объект с информацией о сообщении.
    - context: ContextTypes.DEFAULT_TYPE, объект с информацией о контексте.

    Возвращает:
    - None
    """
    logger.info("Goodbye message received.")
    await update.message.reply_text("До свидания! Если у вас возникнут вопросы, обращайтесь.")


async def convert_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработчик команды /convert, ожидающий ввода суммы.

    Параметры:
    - update: Update, объект с информацией о сообщении.
    - context: ContextTypes.DEFAULT_TYPE, объект с информацией о контексте.

    Возвращает:
    - int: Состояние машины состояний - ожидание ввода суммы.
    """
    logger.info("Convert command received. Waiting for amount.")
    await update.message.reply_text("Введите сумму, которую вы хотите конвертировать")
    return CONVERT_FROM


async def convert_from(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработчик ввода суммы, ожидающий ввода валюты из которой конвертировать.

    Параметры:
    - update: Update, объект с информацией о сообщении.
    - context: ContextTypes.DEFAULT_TYPE, объект с информацией о контексте.

    Возвращает:
    - int: Состояние машины состояний - ожидание ввода валюты из которой конвертировать.
    """
    context.user_data['amount'] = float(update.message.text)
    logger.info("Amount received: %f", context.user_data['amount'])
    await update.message.reply_text("Введите валюту, из которой вы хотите конвертировать")
    return CONVERT_TO


async def convert_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработчик ввода валюты из которой конвертировать, ожидающий ввода валюты в которую конвертировать.

    Параметры:
    - update: Update, объект с информацией о сообщении.
    - context: ContextTypes.DEFAULT_TYPE, объект с информацией о контексте.

    Возвращает:
    - int: Состояние машины состояний - ожидание выполнения конвертации.
    """
    context.user_data['from_currency'] = update.message.text.upper()
    logger.info("From currency received: %s", context.user_data['from_currency'])
    await update.message.reply_text("Введите валюту, в которую вы хотите конвертировать")
    return PERFORM_CONVERSION


async def perform_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
     Обработчик выполнения конвертации, запрос к API.

     Параметры:
     - update: Update, объект с информацией о сообщении.
     - context: ContextTypes.DEFAULT_TYPE, объект с информацией о контексте.

     Возвращает:
     - int: Состояние машины состояний - ожидание ввода суммы.
     """
    user_data = context.user_data
    from_currency = user_data['from_currency']
    user_data['to_currency'] = update.message.text.upper()

    logger.info("To currency received: %s", update.message.text.upper())
    logger.info("To currency received: %s", user_data['to_currency'])

    try:
        url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/{from_currency}'

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

    return CONVERT_AMOUNT


def main() -> None:
    """
    Главная функция для запуска бота.

    Возвращает:
    - None
    """
    application = Application.builder().token(token).build()
    logger.info("Bot launched successfully.")

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

    greet_handler = MessageHandler(
        filters.Regex(r'\b(?:привет|здравствуй|добрый день)\b') | filters.Regex(r'\b(?:hello|hi|good day)\b'),
        greet_user
    )
    goodbye_handler = MessageHandler(
        filters.Regex(r'\b(?:пока|до свидания)\b') | filters.Regex(r'\b(?:bye|see|you)\b'),
        say_goodbye
    )

    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)
    application.add_handler(greet_handler)
    application.add_handler(goodbye_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
