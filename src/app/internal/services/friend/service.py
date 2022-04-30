from typing import Dict, Optional, Union

from django.db.models import QuerySet

from app.internal.models.user import TelegramUser
from app.internal.services.user.TelegramUserFields import TelegramUserFields


def add_friend(user: TelegramUser, friend: TelegramUser) -> None:
    user.friends.add(friend)


def get_friend(user: TelegramUser, identifier: Union[int, str]) -> Optional[TelegramUser]:
    param = (
        {TelegramUserFields.ID: int(identifier)}
        if str(identifier).isdigit()
        else {TelegramUserFields.USERNAME: str(identifier)}
    )

    return user.friends.filter(**param).first()


def get_friends(user: TelegramUser) -> QuerySet[TelegramUser]:
    return user.friends.all()


def get_friends_with_enums(user: TelegramUser) -> Dict[int, TelegramUser]:
    return dict((num, friend) for num, friend in enumerate(get_friends(user), 1))


def is_friend_exist(user: TelegramUser, friend: TelegramUser) -> bool:
    return user.friends.filter(pk=friend.pk).exists()
