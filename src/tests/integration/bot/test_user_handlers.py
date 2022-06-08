import pytest
from telegram import Update, User
from telegram.ext import CallbackContext

from app.internal.bank.db.models import BankAccount, Transaction
from app.internal.user.db.models import TelegramUser
from app.internal.user.presentation.handlers.bot.commands import (
    _RELATION_LIST_EMPTY,
    _UPDATING_DETAILS,
    _WELCOME as welcome_user,
    handle_me,
    handle_relations,
    handle_start,
)
from app.internal.user.presentation.handlers.bot.friends.FriendStates import FriendStates
from app.internal.user.presentation.handlers.bot.phone.conversation import (
    _INVALID_PHONE,
    _UPDATING_PHONE,
    _WELCOME,
    handle_phone,
    handle_phone_start,
)
from tests.integration.bot.conftest import assert_conversation_end, assert_conversation_start


@pytest.mark.django_db
@pytest.mark.integration
def test_start__adding(update: Update, user: User) -> None:
    handle_start(update, None)

    assert TelegramUser.objects.filter(
        id=user.id, first_name=user.first_name, last_name=user.last_name, username=user.username
    ).exists()
    update.message.reply_text.assert_called_once_with(welcome_user.format(username=user.username))


@pytest.mark.django_db
@pytest.mark.integration
def test_start__updating(update: Update, telegram_user: TelegramUser, user: User) -> None:
    user.username = user.username[::-1]
    user.first_name = user.first_name[::-1]
    user.last_name = user.last_name[::-1]

    update.effective_user = user

    handle_start(update, None)

    assert TelegramUser.objects.filter(
        id=telegram_user.id, first_name=user.first_name, last_name=user.last_name, username=user.username
    ).exists()
    update.message.reply_text.assert_called_once_with(_UPDATING_DETAILS)


@pytest.mark.django_db
@pytest.mark.integration
def test_me(update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser) -> None:
    handle_me(update, context)
    update.message.reply_text.assert_called_once()


@pytest.mark.django_db
@pytest.mark.integration
def test_phone_start(update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser) -> None:
    next_state = handle_phone_start(update, context)

    assert next_state == FriendStates.INPUT
    assert_conversation_start(context)
    update.message.reply_text.assert_called_once_with(_WELCOME)


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize(
    ["text", "is_set"],
    [
        ["88005553535", True],
        ["8-800-555-35-35", True],
        ["8.800.555.35.35", True],
        ["8(800)-555-35-35", True],
        ["8 (800)-555-35-35", True],
        ["8(800) 555 35 35", True],
        ["8 (800) 555 35 35", True],
        ["88005553535         ", True],
        ["8 800 555 35 35", True],
        ["88005553535 a b", True],
        ["                ", False],
        ["aaaaaaaaaaa", False],
        ["8800", False],
        ["88005553535 1 2", False],
        ["a b 88005553535", False],
        ["        88005553535", False],
        ["aaa        88005553535", False],
        ["    88005553535", False],
    ],
)
def test_phone(update: Update, context: CallbackContext, telegram_user: TelegramUser, text: str, is_set: bool) -> None:
    update.message.text = text

    next_state = handle_phone(update, context)

    actual = TelegramUser.objects.get(pk=telegram_user.pk)

    assert bool(actual.phone) == is_set
    update.message.reply_text.assert_called_once_with(_UPDATING_PHONE if is_set else _INVALID_PHONE)
    if is_set:
        assert_conversation_end(next_state, context)
    else:
        assert next_state == FriendStates.INPUT


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_relations(
    update: Update,
    context: CallbackContext,
    telegram_user_with_phone: TelegramUser,
    bank_account: BankAccount,
    another_account: BankAccount,
) -> None:
    Transaction.objects.create(source=bank_account, destination=another_account)

    handle_relations(update, context)

    update.message.reply_text.assert_called_once()


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_relations__list_is_empty(
    update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser
) -> None:
    handle_relations(update, context)

    update.message.reply_text.assert_called_once_with(_RELATION_LIST_EMPTY)
