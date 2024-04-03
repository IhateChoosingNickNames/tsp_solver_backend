import codecs
import csv
from enum import Enum

from fastapi import UploadFile, HTTPException

from core.dto import TaskDetailDTO, SinglePoint, Points
from core.exceptions import IncorrectFileFormatError


class FileFormat(Enum):
    CSV = "text/csv"


def get_data_from_file(file: UploadFile) -> Points:
    if file.content_type == FileFormat.CSV.value:
        return _open_csv_file(file)

    raise IncorrectFileFormatError("Неверный тип файла")


def _open_csv_file(file: UploadFile) -> Points:
    try:
        csv_reader = csv.DictReader(
            codecs.iterdecode(file.file, encoding="utf-8")
        )
        return Points(
            points=[
                SinglePoint(lat=elem.get("lat"), lng=elem.get("lng"))
                for elem in csv_reader
            ]
        )
    except HTTPException as err:
        raise err
    except Exception:
        raise IncorrectFileFormatError(
            "Непредвиденная ошибка при чтении файла.",
        )
    finally:
        file.file.close()
