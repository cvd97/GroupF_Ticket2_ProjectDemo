# GroupF_Ticket2_ProjectDemo

Working prototype for Group F Ticket 2 design pattern demo. This project implements the notification system from the design proposal. The main design problem is that a notification system should not be built around one large switch statement. This version separates what gets sent from how it gets delivered.

## Patterns implemented

- **Adapter:** `EmailAdapter`, `SMSAdapter`, `PushAdapter`, and `InAppAdapter` all implement the same `send(message)` interface.
- **Observer:** `NotificationService` notifies subscribers when an event fires.
- **Decorator:** `LoggingDecorator` and `RetryDecorator` add behavior without editing the channel classes.
- **Chain of Responsibility:** selected channels are tried in order until one succeeds.
- **GRASP:** the design uses polymorphism, low coupling, and protected variations.

## Why SQLite is used

The proposal listed MySQL, but SQLite is used for the actual class demo because it runs immediately on every group member's machine. This keeps the demo reliable. The design patterns are independent of the database choice.

## Backend setup

From the project root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py test
python manage.py runserver 8000
```

Important: use the `.venv` folder, not `venv`. If you already made an old broken virtual environment, delete it first:

```bash
rm -rf venv .venv
```

The backend should now be running at:

```text
http://localhost:8000/api/logs/
```

## Frontend setup

Open a second terminal from the project root:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, usually:

```text
http://localhost:5173
```

## Class demo flow

1. Open the React dashboard.
2. Type a notification message.
3. Enter an email and/or phone number.
4. Choose the fallback order: push, SMS, email, or in-app.
5. Click **Run Pattern Demo**.
6. Show the trace list. This proves the Observer, Decorator, Adapter, and Chain of Responsibility are running.
7. If email is selected, the backend terminal prints the demo email because Django uses the console email backend by default.

## Real email later

The demo uses console email by default. For real email, set SMTP values in `backend/.env.example` and change the email backend to SMTP. Do not commit real passwords or API keys.

## Recommended GitHub commands

From the project root:

```bash
git init
git add .
git commit -m "Implement notification design pattern demo"
git branch -M main
git remote add origin https://github.com/cvd97/GroupF_Ticket2_ProjectDemo.git
git push -u origin main
```
