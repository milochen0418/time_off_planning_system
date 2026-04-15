# Time-Off Planning System — Flet Desktop Client

A desktop/mobile time-off planning app built with [Flet](https://flet.dev/), fully feature-equivalent to the Web version.

## Architecture

```
┌─────────────────┐                         ┌──────────────────────┐
│  Browser (Web)  │ ◄──── Reflex SSR ────►  │                      │
└─────────────────┘                         │  Reflex + FastAPI    │
                                            │  (port 8000)         │
┌─────────────────┐        HTTP/JSON        │                      │
│  Flet Desktop / │ ◄────────────────────►  │  Shared store.py     │
│  Mobile App     │   /api/* endpoints      │  (in-memory data)    │
└─────────────────┘                         └──────────────────────┘
```

- **A single server** (port 8000) serves both the Web and Flet clients.
- **store.py** is the single source of truth — both Reflex states and the API read/write the same data.
- Leaves created from the Web version are instantly visible in the Flet mobile app, and vice versa.

## Features

| Feature | Description |
|---------|-------------|
| Login | Sign in with username and password |
| My Leaves | Create, edit, and delete personal leave records |
| Shared Calendar | Month / Week / Day views showing everyone's leaves |
| Admin Panel | User CRUD and message management |
| Contact Admin | Submit a message to the super admin |

## Quick Start

### 1. Install Dependencies

```bash
poetry install
```

### 2. Start the Reflex Server (serves both Web + API)

```bash
poetry run ./reflex_rerun.sh
```

### 3. Start the Flet Desktop/Mobile App (in another terminal)

**Desktop mode:**

```bash
cd flet_app
poetry run python main.py
```

**Android emulator:**

```bash
poetry run flet run flet_app/main.py --android
```

**iOS simulator:**

```bash
open -a Simulator
poetry run flet run flet_app/main.py --ios
```

> iOS simulator requires Xcode 16+ and CocoaPods. See [HOW_TO_RUN_EN.md](HOW_TO_RUN_EN.md) for details.

## Default Accounts

| Role | Username | Password |
|------|----------|----------|
| Regular user | admin | admin123 |
| Super admin | admin | admin |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/login` | User login |
| POST | `/api/register` | User registration |
| GET | `/api/leaves?user_id=` | Get leave list |
| POST | `/api/leaves?user_id=` | Create a leave |
| PUT | `/api/leaves/{id}?user_id=` | Update a leave |
| DELETE | `/api/leaves/{id}` | Delete a leave |
| GET | `/api/calendar/month?year=&month=` | Monthly calendar data |
| GET | `/api/calendar/week?year=&month=&day=` | Weekly calendar data |
| GET | `/api/calendar/day?year=&month=&day=` | Daily calendar data |
| POST | `/api/admin/login` | Admin login |
| GET | `/api/admin/users` | User list |
| POST | `/api/admin/users` | Create a user |
| PUT | `/api/admin/users/{id}` | Update a user |
| DELETE | `/api/admin/users/{id}` | Delete a user |
| GET | `/api/messages` | Message list |
| POST | `/api/messages` | Submit a message |
| DELETE | `/api/messages/{id}` | Delete a message |
