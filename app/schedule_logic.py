from datetime import datetime, timedelta


def get_workdays(count: int = 14):
    """
    Возвращает список рабочих дней (Пн-Пт) на ближайшие count дней.
    Формат:
    [
      {"label": "Пн 10.06.2026", "date": "10.06.2026"},
      ...
    ]
    """
    weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт"]
    today = datetime.today()
    days = []
    current = today + timedelta(days=1)

    while len(days) < count:
        if current.weekday() < 5:  # 0-4 = Пн-Пт
            days.append(
                {
                    "label": f"{weekdays_ru[current.weekday()]} {current.strftime('%d.%m.%Y')}",
                    "date": current.strftime("%d.%m.%Y"),
                }
            )
        current += timedelta(days=1)

    return days


def get_times():
    """
    Возвращает список слотов времени.
    Можно подстроить под своё расписание.
    """
    return ["08:00", "09:20", "10:40", "12:50", "14:10", "15:30"]


def safe_datetime(date_s: str, time_s: str):
    """
    Безопасно парсит дату и время в datetime.
    Формат даты: dd.MM.yyyy
    Формат времени: HH:mm
    """
    try:
        return datetime.strptime(f"{date_s} {time_s}", "%d.%m.%Y %H:%M")
    except Exception:
        return None