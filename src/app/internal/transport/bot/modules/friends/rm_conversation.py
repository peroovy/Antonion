from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler

from app.internal.models.user import TelegramUser
from app.internal.services.friend import get_friends_with_enums, try_remove_from_friends
from app.internal.services.user import get_user
from app.internal.transport.bot.decorators import (
    if_phone_is_set,
    if_update_message_exists,
    if_user_exist,
    if_user_is_not_in_conversation,
)
from app.internal.transport.bot.modules.filters import INT
from app.internal.transport.bot.modules.friends.FriendStates import FriendStates
from app.internal.transport.bot.modules.general import cancel, mark_conversation_end, mark_conversation_start

_WELCOME = "Выберите пользователя, который плохо себя ведёт:\n\n"
_LIST_EMPTY = "К сожалению, у вас нет друзей :("
_REMOVE_SUCCESS = "Товарищ покинул ваш чат..."
_REMOVE_MESSAGE = "Товарищ {username} оставил вас за бортом... Вы больше не друзья:("
_STUPID_CHOICE = "Проверьте свои кракозябры и повторите попытку, либо /cancel"
_FRIEND_VARIANT = "{num}) {username}"
_REMOVE_ERROR = "Произошла ошибка"

_USERNAMES_SESSION = "usernames"
_USER_SESSION = "user"


@if_update_message_exists
@if_user_exist
@if_phone_is_set
@if_user_is_not_in_conversation
def handle_rm_friend_start(update: Update, context: CallbackContext) -> int:
    mark_conversation_start(context, entry_point.command)

    user = get_user(update.effective_user.id)
    friends = get_friends_with_enums(user)

    context.user_data[_USERNAMES_SESSION] = friends
    context.user_data[_USER_SESSION] = user

    update.message.reply_text(
        _WELCOME
        + "\n".join(_FRIEND_VARIANT.format(num=num, username=friend.username) for num, friend in friends.items())
    )

    return FriendStates.INPUT


@if_update_message_exists
def handle_rm_friend(update: Update, context: CallbackContext) -> int:
    user: TelegramUser = context.user_data[_USER_SESSION]
    friend: TelegramUser = context.user_data[_USERNAMES_SESSION].get(int(update.message.text))

    if not friend:
        update.message.reply_text(_STUPID_CHOICE)
        return FriendStates.INPUT

    if not try_remove_from_friends(user, friend):
        update.message.reply_text(_REMOVE_ERROR)
        return mark_conversation_end(context)

    update.message.reply_text(_REMOVE_SUCCESS)

    context.bot.send_message(chat_id=friend.id, text=get_notification(user))

    return mark_conversation_end(context)


def get_notification(source: TelegramUser) -> str:
    return _REMOVE_MESSAGE.format(username=source.username)


entry_point = CommandHandler("rm", handle_rm_friend_start)


rm_friend_conversation = ConversationHandler(
    entry_points=[entry_point],
    states={
        FriendStates.INPUT: [MessageHandler(INT, handle_rm_friend)],
    },
    fallbacks=[cancel],
)