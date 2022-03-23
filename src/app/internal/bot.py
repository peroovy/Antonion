from django.conf import settings
from telegram.ext import CommandHandler, Updater

from app.internal.transport.bot import (
    handle_getting_balance_by_account,
    handle_getting_balance_by_card,
    handle_me,
    handle_set_phone,
    handle_start,
)


def start() -> None:
    handlers = [
        CommandHandler("start", handle_start),
        CommandHandler("set_phone", handle_set_phone),
        CommandHandler("me", handle_me),
        CommandHandler("balance", handle_getting_balance_by_account),
        CommandHandler("card_balance", handle_getting_balance_by_card),
    ]

    updater = Updater(settings.TELEGRAM_BOT_TOKEN)
    for handler in handlers:
        updater.dispatcher.add_handler(handler)

    updater.start_polling()
    updater.idle()