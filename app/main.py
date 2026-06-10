import os
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Query

from .models import BookingRequest
from .schedule_logic import get_times, get_workdays, safe_datetime
from .db import (
    init_db,
    get_schedule,
    add_booking,
    is_slot_taken,
    week_limit,
    day_count,
    cancel_booking,
    block_slot,
)


app = FastAPI(title="Driving Lessons Booking API")

# Лимиты (можно поменять при желании)
MAX_PER_WEEK = 2   # максимум занятий в неделю
MAX_PER_DAY = 1    # максимум занятий в день

# Секрет для админ‑эндпоинтов (добавь ADMIN_SECRET в ENV на Render)
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "change-me")


def check_admin(token: str = Query(..., alias="admin_token")):
    if token != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")


@app.on_event("startup")
def on_startup():
    # Создаём таблицы при старте (если их ещё нет)
    init_db()


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/workdays")
async def workdays():
    return get_workdays()


@app.get("/times")
async def times():
    return get_times()


@app.get("/schedule")
async def schedule():
    records = get_schedule()
    return [
        {
            "date": r.date,
            "time": r.time,
            "status": r.status,
            "user_id": r.user_id,
            "fio": r.fio,
            "address": r.address,
            "created_at": r.created_at.isoformat(),
            "meta": r.meta,
        }
        for r in records
    ]


@app.post("/book")
async def book(req: BookingRequest):
    # 1. Проверка формата даты/времени
    dt = safe_datetime(req.date, req.time)
    if not dt:
        raise HTTPException(status_code=400, detail="Неверная дата/время")

    # 2. Нельзя записываться в прошлое
    if dt <= datetime.now():
        raise HTTPException(status_code=400, detail="Нельзя записаться в прошлое")

    # 3. Слот уже занят или заблокирован
    if is_slot_taken(req.date, req.time):
        raise HTTPException(status_code=400, detail="Слот уже занят или заблокирован")

    # 4. Лимит на день
    if day_count(req.user_id, req.date) >= MAX_PER_DAY:
        raise HTTPException(status_code=400, detail="У вас уже есть запись в этот день")

    # 5. Лимит на неделю
    if week_limit(req.user_id, req.date) >= MAX_PER_WEEK:
        raise HTTPException(status_code=400, detail="Превышен лимит занятий в неделю")

    # 6. Всё ок — создаём запись
    add_booking(
        date=req.date,
        time=req.time,
        user_id=req.user_id,
        fio=req.fio,
        address=req.address,
        status="забронировано",
        meta=req.meta or "",
    )

    return {"ok": True}


# ========= Админ‑эндпоинты =========

@app.post("/admin/cancel")
async def admin_cancel(
    date: str,
    time: str,
    _: None = Depends(check_admin),
):
    """
    Отменить занятие (status -> 'отменено') по дате и времени.
    """
    ok = cancel_booking(date, time)
    if not ok:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"ok": True}


@app.post("/admin/block")
async def admin_block(
    date: str,
    time: str,
    _: None = Depends(check_admin),
):
    """
    Заблокировать слот по дате и времени (никто не сможет записаться).
    """
    block_slot(date, time)
    return {"ok": True}
