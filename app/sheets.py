import json
import os
from pathlib import Path

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")


def get_sheets_service():
    """
    Создаёт клиент к Google Sheets.
    Ключ берём либо из переменной окружения GOOGLE_SERVICE_ACCOUNT_JSON,
    либо из локального файла service-account.json (для разработки).
    """
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if creds_json:
        info = json.loads(creds_json)
        creds = Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
    else:
        info = json.loads(Path("service-account.json").read_text(encoding="utf-8"))
        creds = Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )

    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets()


def load_schedule():
    """
    Загружает все записи из листа Schedule.
    Ожидаемый формат колонок:
    A: date, B: time, C: status, D: user_id,
    E: fio, F: address, G: created_at, H: meta
    """
    sheets = get_sheets_service()
    result = sheets.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="Schedule!A2:H",
    ).execute()
    rows = result.get("values", []) or []

    schedule = []
    for row in rows:
        schedule.append(
            {
                "date": row[0],
                "time": row[1],
                "status": row[2],
                "user_id": row[3] if len(row) > 3 else "",
                "fio": row[4] if len(row) > 4 else "",
                "address": row[5] if len(row) > 5 else "",
                "created_at": row[6] if len(row) > 6 else "",
                "meta": row[7] if len(row) > 7 else "",
            }
        )
    return schedule


def append_booking(booking: dict):
    """
    Добавляет одну запись в конец листа Schedule.
    booking:
      date, time, status, user_id, fio, address, created_at, meta
    """
    sheets = get_sheets_service()
    values = [
        [
            booking["date"],
            booking["time"],
            booking["status"],
            booking["user_id"],
            booking["fio"],
            booking["address"],
            booking["created_at"],
            booking.get("meta", ""),
        ]
    ]
    sheets.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Schedule!A:H",
        valueInputOption="RAW",
        body={"values": values},
    ).execute()