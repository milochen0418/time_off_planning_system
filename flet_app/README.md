# Time-Off Planning System — Flet Desktop Client

桌面版預約休假管理系統，使用 [Flet](https://flet.dev/) 構建，功能與 Web 版完全一致。

## 架構

```
┌─────────────────┐                         ┌──────────────────────┐
│  Browser (Web)  │ ◄──── Reflex SSR ────►  │                      │
└─────────────────┘                         │  Reflex + FastAPI    │
                                            │  (port 8000)         │
┌─────────────────┐        HTTP/JSON        │                      │
│  Flet Desktop / │ ◄────────────────────►  │  共用 store.py       │
│  Mobile App     │   /api/* endpoints      │  (in-memory data)    │
└─────────────────┘                         └──────────────────────┘
```

- **同一個伺服器** (port 8000) 同時服務 Web 和 Flet 客戶端
- **store.py** 是唯一的資料來源，Reflex states 和 API 都讀寫同一份資料
- Web 版新增的休假，Flet 手機版立即可見，反之亦然

## 功能

| 功能 | 說明 |
|------|------|
| 登入 | 使用帳號密碼登入 |
| 我的休假 | 新增、編輯、刪除個人休假記錄 |
| 共用日曆 | 月/週/日 三種檢視模式，顯示所有人的休假 |
| 超級管理者 | 使用者 CRUD、留言管理 |
| 聯絡管理者 | 送出留言給超級管理者 |

## 快速啟動

### 1. 安裝依賴

```bash
poetry install
```

### 2. 啟動 Reflex 伺服器 (同時提供 Web + API)

```bash
poetry run ./reflex_rerun.sh
```

### 3. 啟動 Flet 桌面/手機程式 (另一個終端)

```bash
cd flet_app
poetry run python main.py
```

## 預設帳號

| 角色 | 帳號 | 密碼 |
|------|------|------|
| 一般使用者 | admin | admin123 |
| 超級管理者 | admin | admin |

## API 端點一覽

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/login` | 使用者登入 |
| POST | `/api/register` | 使用者註冊 |
| GET | `/api/leaves?user_id=` | 取得休假列表 |
| POST | `/api/leaves?user_id=` | 新增休假 |
| PUT | `/api/leaves/{id}?user_id=` | 更新休假 |
| DELETE | `/api/leaves/{id}` | 刪除休假 |
| GET | `/api/calendar/month?year=&month=` | 月曆資料 |
| GET | `/api/calendar/week?year=&month=&day=` | 週曆資料 |
| GET | `/api/calendar/day?year=&month=&day=` | 日曆資料 |
| POST | `/api/admin/login` | 管理者登入 |
| GET | `/api/admin/users` | 使用者列表 |
| POST | `/api/admin/users` | 新增使用者 |
| PUT | `/api/admin/users/{id}` | 更新使用者 |
| DELETE | `/api/admin/users/{id}` | 刪除使用者 |
| GET | `/api/messages` | 留言列表 |
| POST | `/api/messages` | 送出留言 |
| DELETE | `/api/messages/{id}` | 刪除留言 |
