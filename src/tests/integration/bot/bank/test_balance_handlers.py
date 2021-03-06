from typing import List

import pytest
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from app.internal.bank.db.models import BankAccount, BankCard, BankObject
from app.internal.bank.presentation.handlers.bot.balance.handlers import (
    _BALANCE_BY_BANK_ACCOUNT,
    _BALANCE_BY_CARD,
    _DOCUMENTS_SESSION,
    _LIST_EMPTY_MESSAGE,
    _STUPID_CHOICE,
    BalanceStates,
    handle_choice,
    handle_start,
)
from app.internal.user.db.models import TelegramUser


@pytest.mark.django_db
@pytest.mark.integration
def test_start(
    update: Update,
    context: CallbackContext,
    telegram_user_with_phone: TelegramUser,
    bank_accounts: List[BankAccount],
    cards: List[BankCard],
) -> None:
    next_state = handle_start(update, context)

    assert next_state == BalanceStates.CHOICE
    assert _DOCUMENTS_SESSION in context.user_data
    assert type(context.user_data[_DOCUMENTS_SESSION]) is dict
    assert sorted(context.user_data[_DOCUMENTS_SESSION].values(), key=str) == sorted([*bank_accounts, *cards], key=str)


@pytest.mark.django_db
@pytest.mark.integration
def test_start__documents_len_is_zero(
    update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser
) -> None:
    next_state = handle_start(update, context)

    assert next_state == ConversationHandler.END
    assert _DOCUMENTS_SESSION not in context.user_data
    update.message.reply_text.assert_called_once_with(_LIST_EMPTY_MESSAGE)
    assert len(context.user_data) == 0


@pytest.mark.django_db
@pytest.mark.integration
def test_choice__bank_account(update: Update, context: CallbackContext, bank_account: BankAccount) -> None:
    _test_balance__bank_object(update, context, bank_account, _BALANCE_BY_BANK_ACCOUNT)


@pytest.mark.django_db
@pytest.mark.integration
def test_choice__card(update: Update, context: CallbackContext, card: BankCard) -> None:
    _test_balance__bank_object(update, context, card, _BALANCE_BY_CARD)


def _test_balance__bank_object(update: Update, context: CallbackContext, obj: BankObject, details: str) -> None:
    update.message.text = "1"
    context.user_data[_DOCUMENTS_SESSION] = {1: obj}

    next_state = handle_choice(update, context)

    assert next_state == ConversationHandler.END
    update.message.reply_text.assert_called_once_with(
        details.format(number=obj.short_number, balance=obj.get_balance())
    )
    assert len(context.user_data) == 0


@pytest.mark.django_db
@pytest.mark.integration
def test_choice__stupid(update: Update, context: CallbackContext, bank_account: BankAccount) -> None:
    update.message.text = "-1"
    context.user_data[_DOCUMENTS_SESSION] = {1: bank_account}

    next_state = handle_choice(update, context)

    assert next_state == BalanceStates.CHOICE
    update.message.reply_text.assert_called_once_with(_STUPID_CHOICE)
