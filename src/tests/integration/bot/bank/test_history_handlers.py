from typing import List

import pytest
from telegram import Update
from telegram.ext import CallbackContext

from app.internal.bank.db.models import BankAccount
from app.internal.bank.presentation.handlers.bot.history.handlers import (
    _DOCUMENTS_SESSION,
    _LIST_EMPTY_MESSAGE,
    _STUPID_CHOICE,
    handle_getting_document,
    handle_start,
)
from app.internal.bank.presentation.handlers.bot.history.HistoryStates import HistoryStates
from app.internal.user.db.models import TelegramUser
from tests.integration.bot.conftest import assert_conversation_end, assert_conversation_start


@pytest.mark.django_db
@pytest.mark.integration
def test_start(
    update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser, bank_accounts: List[BankAccount]
) -> None:
    next_state = handle_start(update, context)

    assert next_state == HistoryStates.DOCUMENT
    assert_conversation_start(context)
    update.message.reply_text.assert_called_once()
    assert _DOCUMENTS_SESSION in context.user_data
    assert sorted(context.user_data[_DOCUMENTS_SESSION].values(), key=str) == sorted(bank_accounts, key=str)


@pytest.mark.django_db
@pytest.mark.integration
def test_start__documents_is_empty(
    update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser
) -> None:
    next_state = handle_start(update, context)

    assert_conversation_end(next_state, context)
    assert _DOCUMENTS_SESSION not in context.user_data
    update.message.reply_text.assert_called_once_with(_LIST_EMPTY_MESSAGE)


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_document(
    update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser, bank_account: BankAccount
) -> None:
    update.message.text = "1"
    context.user_data[_DOCUMENTS_SESSION] = {int(update.message.text): bank_account}

    next_state = handle_getting_document(update, context)

    assert_conversation_end(next_state, context)
    update.message.reply_document.assert_called_once()


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_document__stupid_choice(
    update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser, bank_account: BankAccount
) -> None:
    update.message.text = "-1"
    context.user_data[_DOCUMENTS_SESSION] = {1: bank_account}

    next_state = handle_getting_document(update, context)

    assert next_state == HistoryStates.DOCUMENT
    update.message.reply_text.assert_called_once_with(_STUPID_CHOICE)
