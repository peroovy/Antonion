import pytest
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from app.internal.general.bot.handlers import _CANCEL_OPERATION, handle_cancel


@pytest.mark.integration
def test_cancel(update: Update, context: CallbackContext) -> None:
    for i in range(10):
        context.user_data[str(i)] = None

    next_state = handle_cancel(update, context)

    assert next_state == ConversationHandler.END
    update.message.reply_text.assert_called_once_with(_CANCEL_OPERATION)
    assert len(context.user_data) == 0
