from datetime import datetime, timedelta
from typing import Any, Dict

import pytest
from django.conf import settings
from freezegun import freeze_time

from app.internal.authentication.db.models import RefreshToken
from app.internal.authentication.domain.services.TokenTypes import TokenTypes
from app.internal.general.services import auth_service
from app.internal.user.db.models import TelegramUser
from tests.conftest import PASSWORD, WRONG_PASSWORD

CREATED_AT, TELEGRAM_ID, TOKEN_TYPE = auth_service.CREATED_AT, auth_service.TELEGRAM_ID, auth_service.TOKEN_TYPE


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_authenticated_user(telegram_user: TelegramUser) -> None:
    payload = {TELEGRAM_ID: telegram_user.id}
    actual = auth_service.get_authenticated_telegram_user(payload)

    assert actual == telegram_user


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_authenticated_user__not_exists() -> None:
    payload = {TELEGRAM_ID: 1337}
    actual = auth_service.get_authenticated_telegram_user(payload)

    assert actual is None


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_user_by_credentials(telegram_user_with_password: TelegramUser) -> None:
    correct = auth_service.get_user_by_credentials(telegram_user_with_password.username, PASSWORD)
    wrong = auth_service.get_user_by_credentials(telegram_user_with_password.username, WRONG_PASSWORD)

    assert correct == telegram_user_with_password
    assert wrong is None


@freeze_time("2022-05-21")
@pytest.mark.django_db
@pytest.mark.unit
def test_creating_tokens(telegram_user: TelegramUser) -> None:
    access, refresh = auth_service.create_access_and_refresh_tokens(telegram_user)
    actual_refresh_tokens = RefreshToken.objects.filter(telegram_user=telegram_user).all()

    _assert_tokens(access, refresh, telegram_user)
    assert len(actual_refresh_tokens) == 1
    assert actual_refresh_tokens[0].value == refresh


@freeze_time("2022-05-21")
@pytest.mark.django_db
@pytest.mark.unit
def test_updating_tokens(telegram_user: TelegramUser, refresh_token: RefreshToken) -> None:
    tokens = auth_service.update_access_and_refresh_tokens(refresh_token)

    assert tokens is not None
    _assert_tokens(tokens[0], tokens[1], telegram_user)
    assert RefreshToken.objects.filter(pk=refresh_token.pk).first().revoked
    assert RefreshToken.objects.filter(telegram_user=telegram_user, revoked=False).count() > 0


@freeze_time("2022-05-21")
@pytest.mark.django_db
@pytest.mark.unit
def test_updating_tokens__revoking_all(telegram_user: TelegramUser, refresh_token: RefreshToken) -> None:
    refresh_token.revoked = True
    refresh_token.save(update_fields=["revoked"])

    tokens = auth_service.update_access_and_refresh_tokens(refresh_token)

    assert tokens is None
    assert RefreshToken.objects.filter(telegram_user=telegram_user, revoked=False).count() == 0


def _assert_tokens(access: str, refresh: str, telegram_user: TelegramUser) -> None:
    access_payload, refresh_payload = auth_service.try_get_payload(access), auth_service.try_get_payload(refresh)

    payload = {TELEGRAM_ID: telegram_user.id, CREATED_AT: datetime.now().timestamp()}
    assert access_payload == payload | {TOKEN_TYPE: TokenTypes.ACCESS.value}
    assert refresh_payload == payload | {TOKEN_TYPE: TokenTypes.REFRESH.value}


@freeze_time("2022-06-02")
@pytest.mark.unit
def test_getting_payload(token_type=TokenTypes.ACCESS) -> None:
    expected = {TELEGRAM_ID: 123, CREATED_AT: auth_service._now().timestamp(), TOKEN_TYPE: token_type.value}

    token = auth_service.generate_token(expected[TELEGRAM_ID], token_type)

    actual = auth_service.try_get_payload(token)

    assert actual == expected


@pytest.mark.unit
def test_getting_bad_payload() -> None:
    token = "imstupidtoken"
    payload = auth_service.try_get_payload(token)

    assert payload == {}


@pytest.mark.unit
@pytest.mark.parametrize(
    ["payload", "is_valid"],
    [
        [{}, False],
        [None, False],
        [{CREATED_AT: 123}, False],
        [{CREATED_AT: 123, TELEGRAM_ID: 123}, False],
        [{CREATED_AT: 123, TELEGRAM_ID: 123, TOKEN_TYPE: "dude"}, True],
        [{CREATED_AT: 123, TELEGRAM_ID: 123, TOKEN_TYPE: "dude", "opa": 123}, False],
        [{CREATED_AT: 123, TELEGRAM_ID: 123, TOKEN_TYPE: "dude", "opa": 123, "ta": 123}, False],
    ],
)
def test_validation_payload(payload: Dict[str, Any], is_valid: bool) -> None:
    assert auth_service.is_payload_valid(payload) == is_valid


@freeze_time(auth_service._now())
@pytest.mark.parametrize(
    ["delta", "is_alive"],
    [
        [-settings.ACCESS_TOKEN_TTL, False],
        [-settings.ACCESS_TOKEN_TTL - timedelta(seconds=1), False],
        [-settings.ACCESS_TOKEN_TTL - timedelta(milliseconds=1), False],
        [-2 * settings.ACCESS_TOKEN_TTL, False],
        [timedelta(milliseconds=0), True],
        [-settings.ACCESS_TOKEN_TTL + timedelta(seconds=1), True],
        [-settings.ACCESS_TOKEN_TTL + timedelta(milliseconds=1), True],
        [-timedelta(seconds=1), True],
        [-timedelta(milliseconds=1), True],
    ],
)
def test_is_token_alive(delta: timedelta, is_alive: bool) -> None:
    payload = {
        TELEGRAM_ID: 123,
        TOKEN_TYPE: TokenTypes.ACCESS.value,
        CREATED_AT: (auth_service._now() + delta).timestamp(),
    }

    assert auth_service.is_token_alive(payload, TokenTypes.ACCESS, settings.ACCESS_TOKEN_TTL) == is_alive
