from datetime import datetime

from fastapi import FastAPI, HTTPException

from .models import BookingRequest
from .schedule_logic import get_times, get_workdays, safe_datetime
from .sheets import append_booking, load_schedule


app = FastAPI(title="Driving Lessons Booking API")


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
    return load_schedule()


@app.post("/book")
async def book(req: BookingRequest):
    schedule = load_schedule()

    # Проверка: не занят ли слот
    for item in schedule:
        if (
            item["date"] == req.date
            and item["time"] == req.time
            and item["status"] != "отменено"
        ):
            raise HTTPException(status_code=400, detail="Слот уже занят")

    dt = safe_datetime(req.date, req.time)
    if not dt:
        raise HTTPException(status_code=400, detail="Неверная дата/время")

    booking = {
        "date": req.date,
        "time": req.time,
        "status": "забронировано",
        "user_id": req.user_id,
        "fio": req.fio,
        "address": req.address,
        "created_at": datetime.utcnow().isoformat(),
        "meta": req.meta or "",
    }
    append_booking(booking)
    return {"ok": True}