from typing import Callable, Optional

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from app.internal.services.user import get_user

_USER_DOESNT_EXIST = "Моя вас не знать. Моя предложить знакомиться с вами! (команда /start)"
_UNDEFINED_PHONE = "Вы забыли уведомить нас о вашей мобилке. Пожалуйста, продиктуйте! (команда /set_phone)"


def if_update_message_exist(handler: Callable) -> Callable:
    def wrapper(update: Update, context: CallbackContext) -> Optional[int]:
        if update.message is None:
            return

        return handler(update, context)

    return wrapper


def if_user_exist(handler: Callable) -> Callable:
    def wrapper(update: Update, context: CallbackContext) -> Optional[int]:
        user = get_user(update.effective_user.id)

        if user:
            return handler(update, context)

        update.message.reply_text(_USER_DOESNT_EXIST)

        return ConversationHandler.END

    return wrapper


def if_phone_is_set(handler: Callable) -> Callable:
    def wrapper(update: Update, context: CallbackContext) -> Optional[int]:
        user = get_user(update.effective_user.id)

        if user.phone:
            return handler(update, context)

        update.message.reply_text(_UNDEFINED_PHONE)

        return ConversationHandler.END

    return wrapper