import pytest
from telegram import Update
from telegram.ext import CallbackContext

from app.internal.user.db.models import SecretKey, TelegramUser
from app.internal.user.db.repositories import SecretKeyRepository, TelegramUserRepository
from app.internal.user.presentation.handlers.bot.password.conversation import (
    _CONFIRM_PASSWORD,
    _CREATE_TIP,
    _CREATING_SUCCESS,
    _CREATING_WELCOME,
    _INPUT_PASSWORD,
    _PASSWORD_SESSION,
    _SECRET_KEY_ERROR,
    _SECRET_KEY_SESSION,
    _TIP_SESSION,
    _UPDATING_SUCCESS,
    _UPDATING_WELCOME,
    _WRONG_PASSWORD,
    _handle_confirmation,
    _handle_entering,
    _handle_saving_secret_parameter,
    handle_confirmation_in_creating,
    handle_confirmation_in_updating,
    handle_confirmation_secret_key,
    handle_entering_in_creating,
    handle_entering_in_updating,
    handle_saving_secret_key,
    handle_saving_tip,
    handle_start,
)
from app.internal.user.presentation.handlers.bot.password.PasswordStates import PasswordStates
from tests.conftest import KEY, PASSWORD, TIP, WRONG_KEY, WRONG_PASSWORD
from tests.integration.bot.conftest import assert_conversation_end, assert_conversation_start


@pytest.mark.django_db
@pytest.mark.integration
def test_start(update: Update, context: CallbackContext, telegram_user_with_password: TelegramUser) -> None:
    handle_start(update, context)

    assert_conversation_start(context)


@pytest.mark.django_db
@pytest.mark.integration
def test_start__exists(update: Update, context: CallbackContext, telegram_user_with_password: TelegramUser) -> None:
    next_state = handle_start(update, context)

    assert next_state == PasswordStates.SECRET_CONFIRMATION
    update.message.reply_text.assert_called_once_with(
        _UPDATING_WELCOME.format(tip=telegram_user_with_password.secret_key.tip)
    )


@pytest.mark.django_db
@pytest.mark.integration
def test_confirmation_secret_key(
    update: Update, context: CallbackContext, telegram_user_with_password: TelegramUser
) -> None:
    update.message.text = KEY

    next_state = handle_confirmation_secret_key(update, context)

    update.message.delete.assert_called_once()
    assert next_state == PasswordStates.PASSWORD_ENTERING_IN_UPDATING
    update.message.reply_text.assert_called_once_with(_INPUT_PASSWORD)


@pytest.mark.django_db
@pytest.mark.integration
def test_confirmation_secret__wrong(
    update: Update, context: CallbackContext, telegram_user_with_password: TelegramUser
) -> None:
    update.message.text = WRONG_KEY

    next_state = handle_confirmation_secret_key(update, context)

    update.message.delete.assert_called_once()
    update.message.reply_text.assert_called_once_with(_SECRET_KEY_ERROR)
    assert_conversation_end(next_state, context)


@pytest.mark.django_db
@pytest.mark.integration
def test_entering_in_updating(
    update: Update, context: CallbackContext, telegram_user_with_password: TelegramUser
) -> None:
    update.message.text = WRONG_PASSWORD
    next_state = handle_entering_in_updating(update, context)

    assert next_state == PasswordStates.PASSWORD_CONFIRMATION_IN_UPDATING
    update.message.reply_text.assert_called_once_with(_CONFIRM_PASSWORD)
    assert context.user_data.get(_PASSWORD_SESSION) == update.message.text


@pytest.mark.django_db
@pytest.mark.integration
def test_confirmation_in_updating(
    update: Update, context: CallbackContext, telegram_user_with_password: TelegramUser
) -> None:
    update.message.text = context.user_data[_PASSWORD_SESSION] = WRONG_PASSWORD
    next_state = handle_confirmation_in_updating(update, context)

    assert_conversation_end(next_state, context)
    update.message.reply_text.assert_called_with(_UPDATING_SUCCESS)

    telegram_user_with_password.refresh_from_db(fields=["password"])
    assert telegram_user_with_password.password == TelegramUserRepository._hash(WRONG_PASSWORD)


@pytest.mark.django_db
@pytest.mark.integration
def test_confirmation_in_updating__wrong(
    update: Update, context: CallbackContext, telegram_user_with_password: TelegramUser
) -> None:
    context.user_data[_PASSWORD_SESSION] = PASSWORD
    update.message.text = WRONG_PASSWORD
    next_state = handle_confirmation_in_updating(update, context)

    assert_conversation_end(next_state, context)
    update.message.reply_text.assert_called_once_with(_WRONG_PASSWORD)


@pytest.mark.django_db
@pytest.mark.integration
def test_start__undefined(update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser) -> None:
    next_state = handle_start(update, context)

    assert next_state == PasswordStates.SECRET_CREATING
    update.message.reply_text.assert_called_once_with(_CREATING_WELCOME)


@pytest.mark.django_db
@pytest.mark.integration
def test_saving_secret_key(update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser) -> None:
    update.message.text = PASSWORD
    next_state = handle_saving_secret_key(update, context)

    assert next_state == PasswordStates.TIP_CREATING
    update.message.reply_text.assert_called_once_with(_CREATE_TIP)
    assert context.user_data.get(_SECRET_KEY_SESSION) == update.message.text


@pytest.mark.django_db
@pytest.mark.integration
def test_saving_tip(update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser) -> None:
    update.message.text = TIP
    next_state = handle_saving_tip(update, context)

    assert next_state == PasswordStates.PASSWORD_ENTERING_IN_CREATING
    update.message.reply_text.assert_called_once_with(_INPUT_PASSWORD)
    assert context.user_data.get(_TIP_SESSION) == update.message.text


@pytest.mark.django_db
@pytest.mark.integration
def test_entering_in_creating(update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser) -> None:
    update.message.text = PASSWORD
    next_state = handle_entering_in_creating(update, context)

    assert next_state == PasswordStates.PASSWORD_CONFIRMATION_IN_CREATING
    update.message.reply_text.assert_called_once_with(_CONFIRM_PASSWORD)
    assert context.user_data.get(_PASSWORD_SESSION) == update.message.text


@pytest.mark.django_db
@pytest.mark.integration
def test_confirmation_in_creating(
    update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser
) -> None:
    update.message.text = context.user_data[_PASSWORD_SESSION] = PASSWORD
    context.user_data[_SECRET_KEY_SESSION] = KEY
    context.user_data[_TIP_SESSION] = TIP

    next_state = handle_confirmation_in_creating(update, context)

    assert_conversation_end(next_state, context)
    update.message.reply_text.assert_called_with(_CREATING_SUCCESS)
    update.message.delete.assert_called_once()

    telegram_user_with_phone.refresh_from_db(fields=["password"])
    key = SecretKey.objects.filter(telegram_user=telegram_user_with_phone).first()
    assert telegram_user_with_phone.password == TelegramUserRepository._hash(PASSWORD)
    assert key.value == SecretKeyRepository._hash(KEY)
    assert key.tip == TIP


@pytest.mark.django_db
@pytest.mark.integration
def test_confirmation_in_creating__wrong(
    update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser
) -> None:
    update.message.text = WRONG_PASSWORD
    context.user_data[_PASSWORD_SESSION] = PASSWORD
    context.user_data[_SECRET_KEY_SESSION] = KEY
    context.user_data[_TIP_SESSION] = TIP

    next_state = handle_confirmation_in_creating(update, context)

    assert_conversation_end(next_state, context)
    update.message.reply_text.assert_called_with(_WRONG_PASSWORD)
    update.message.delete.assert_called_once()


@pytest.mark.django_db
@pytest.mark.integration
def test_confirmation_password__correct(
    update: Update, context: CallbackContext, telegram_user_with_password: TelegramUser
) -> None:
    context.user_data[_PASSWORD_SESSION] = telegram_user_with_password.password
    update.message.text = str(telegram_user_with_password.password)

    next_state = _handle_confirmation(update, context)

    assert next_state == PasswordStates.CONFIRMATION_OK
    update.message.reply_text.assert_not_called()
    update.message.delete.assert_called_once()


@pytest.mark.django_db
@pytest.mark.integration
def test_confirmation_password__wrong(
    update: Update, context: CallbackContext, telegram_user_with_password: TelegramUser
) -> None:
    context.user_data[_PASSWORD_SESSION] = telegram_user_with_password.password
    update.message.text = str(hash(telegram_user_with_password.password))

    next_state = _handle_confirmation(update, context)

    assert_conversation_end(next_state, context)
    update.message.reply_text.assert_called_once_with(_WRONG_PASSWORD)
    update.message.delete.assert_called_once()


@pytest.mark.django_db
@pytest.mark.integration
def test_entering(update: Update, context: CallbackContext) -> None:
    update.message.text = PASSWORD

    _handle_entering(update, context)

    update.message.delete.assert_called_once()
    assert context.user_data.get(_PASSWORD_SESSION) == update.message.text
    update.message.reply_text.assert_called_once_with(_CONFIRM_PASSWORD)


@pytest.mark.django_db
@pytest.mark.integration
def test_saving_secret_parameter(update: Update, context: CallbackContext) -> None:
    session_key, value, next_message = "key", "value", "Next message"

    _handle_saving_secret_parameter(update, context, session_key, value, next_message)

    update.message.delete.assert_called_once()
    assert context.user_data.get(session_key) == value
    update.message.reply_text.assert_called_once_with(next_message)
