from tempfile import TemporaryFile
from datetime import datetime
from typing import Union

from django.conf import settings

_TRANSFER_FILE_NAME = "Выписка для {number} к {date}.txt"


def create_temp_file(text: str) -> TemporaryFile:
    temp = TemporaryFile("r+", encoding="utf-8")

    temp.write(text)
    temp.seek(0)

    return temp


def remove_temp_file(file: TemporaryFile) -> None:
    file.close()


def get_transfer_history_filename(number: Union[str, int]) -> str:
    date = datetime.now().date()

    return _TRANSFER_FILE_NAME.format(number=number, date=date)
