from fastapi import FastAPI, HTTPException

from .models import BookingRequest
from .schedule_logic import get_times, get_workdays, safe_datetime
from .db import init_db, get_schedule, add_booking


app = FastAPI(title="Driving Lessons Booking API")


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
    records = get_schedule()

    # Проверка: не занят ли слот
    for item in records:
        if (
            item.date == req.date
            and item.time == req.time
            and item.status != "отменено"
        ):
            raise HTTPException(status_code=400, detail="Слот уже занят")

    dt = safe_datetime(req.date, req.time)
    if not dt:
        raise HTTPException(status_code=400, detail="Неверная дата/время")

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
