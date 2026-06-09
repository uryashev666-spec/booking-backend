from typing import Optional

from pydantic import BaseModel


class BookingRequest(BaseModel):
    date: str    # dd.MM.yyyy
    time: str    # HH:mm
    user_id: str
    fio: str
    address: str
    meta: Optional[str] = None