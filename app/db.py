import os
from datetime import datetime, timedelta

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    TIMESTAMP,
    create_engine,
    select,
    and_,
)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), nullable=False)       # "dd.MM.yyyy"
    time = Column(String(5), nullable=False)        # "HH:mm"
    status = Column(String(20), nullable=False)     # "забронировано"/"отменено"/"заблокировано"
    user_id = Column(String(64), nullable=False, index=True)
    fio = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    meta = Column(Text)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_schedule():
    db = SessionLocal()
    try:
        return db.query(Schedule).all()
    finally:
        db.close()


def add_booking(date, time, user_id, fio, address, status="забронировано", meta=""):
    db = SessionLocal()
    try:
        booking = Schedule(
            date=date,
            time=time,
            status=status,
            user_id=user_id,
            fio=fio,
            address=address,
            created_at=datetime.utcnow(),
            meta=meta or "",
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking
    finally:
        db.close()


# ========= Дополнительные функции для ограничений =========

def get_user_records(user_id: str):
    """Все НЕ отменённые записи пользователя."""
    db = SessionLocal()
    try:
        q = (
            select(Schedule)
            .where(
                and_(
                    Schedule.user_id == user_id,
                    Schedule.status != "отменено",
                )
            )
        )
        return db.execute(q).scalars().all()
    finally:
        db.close()


def week_limit(user_id: str, target_date: str) -> int:
    """
    Сколько у пользователя занятий за 7 дней, включая target_date.
    target_date в формате "dd.MM.yyyy".
    """
    new_dt = datetime.strptime(target_date, "%d.%m.%Y")
    week_dates = {
        (new_dt + timedelta(days=i)).strftime("%d.%m.%Y")
        for i in range(-6, 1)
    }

    records = get_user_records(user_id)
    return sum(1 for r in records if r.date in week_dates)


def day_count(user_id: str, date: str) -> int:
    """Сколько записей у пользователя в конкретный день."""
    records = get_user_records(user_id)
    return sum(1 for r in records if r.date == date)


def is_slot_taken(date: str, time: str) -> bool:
    """Есть ли запись/блокировка в слоте (кроме отменённых)."""
    db = SessionLocal()
    try:
        q = select(Schedule).where(
            and_(
                Schedule.date == date,
                Schedule.time == time,
                Schedule.status != "отменено",
            )
        )
        return db.execute(q).scalars().first() is not None
    finally:
        db.close()


# ========= Админ‑операции =========

def cancel_booking(date: str, time: str) -> bool:
    """Отменить занятие по дате и времени (status -> 'отменено')."""
    db = SessionLocal()
    try:
        q = (
            select(Schedule)
            .where(
                and_(
                    Schedule.date == date,
                    Schedule.time == time,
                    Schedule.status != "отменено",
                )
            )
        )
        record = db.execute(q).scalars().first()
        if not record:
            return False
        record.status = "отменено"
        db.commit()
        return True
    finally:
        db.close()


def block_slot(date: str, time: str, admin_id: str = "admin") -> None:
    """Заблокировать слот (чтобы никто не смог записаться)."""
    db = SessionLocal()
    try:
        block = Schedule(
            date=date,
            time=time,
            status="заблокировано",
            user_id=admin_id,
            fio="",
            address="",
            created_at=datetime.utcnow(),
            meta="admin block",
        )
        db.add(block)
        db.commit()
    finally:
        db.close()
