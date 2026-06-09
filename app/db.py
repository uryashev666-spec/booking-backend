import os
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    TIMESTAMP,
    create_engine,
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
    status = Column(String(20), nullable=False)
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
