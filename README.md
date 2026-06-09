\# Driving Lessons Booking Backend (FastAPI + Google Sheets)



Минимальный бекенд для записи на занятия вождения.  

Использует FastAPI и Google Sheets в качестве хранилища.



\## Локальный запуск



```bash

python -m venv venv

source venv/bin/activate  # Windows: venv\\Scripts\\activate

pip install -r requirements.txt



export SPREADSHEET\_ID="ВАШ\_ID\_ТАБЛИЦЫ"

export GOOGLE\_SERVICE\_ACCOUNT\_JSON='{"type": "service\_account", ...}'



uvicorn app.main:app --host 0.0.0.0 --port 8000

```



После этого API будет доступен по адресу `http://localhost:8000`.



Основные эндпоинты:



\- `GET /health` – проверка, что API жив.

\- `GET /workdays` – список рабочих дней (Пн–Пт).

\- `GET /times` – список слотов времени.

\- `GET /schedule` – текущее расписание из Google Sheets.

\- `POST /book` – создание записи.



Тело `POST /book`:



```json

{

&nbsp; "date": "10.06.2026",

&nbsp; "time": "09:20",

&nbsp; "user\_id": "12345",

&nbsp; "fio": "Иванов Иван",

&nbsp; "address": "Челябинск, ул. ...",

&nbsp; "meta": "любой комментарий"

}

```

