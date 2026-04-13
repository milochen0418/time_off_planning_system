"""
REST API endpoints for the Time-Off Planning System.
Mounted into the Reflex app's FastAPI instance so that both the web UI
and the Flet mobile/desktop client share the same data store.
"""

from __future__ import annotations

import calendar as _calendar
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from time_off_planning_system.store import store

# ---------------------------------------------------------------------------
# Router (will be mounted by the Reflex app)
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api")

# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    id: int
    username: str
    display_name: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str
    display_name: str


class LeaveCreate(BaseModel):
    leave_date: str
    start_time: str
    end_time: str
    note: str = ""


class LeaveUpdate(BaseModel):
    leave_date: str
    start_time: str
    end_time: str
    note: str = ""


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    display_name: str


class UserUpdate(BaseModel):
    username: str
    password: str
    display_name: str


class MessageCreate(BaseModel):
    employee_id: str
    name: str
    email: str
    contact_method: str
    contact_value: str
    message: str


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------


@router.get("/revision")
def get_revision():
    """Lightweight endpoint returning the current data-store revision number."""
    return {"revision": store.revision}


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    user = next(
        (
            u
            for u in store.users
            if u["username"] == req.username and u["password_hash"] == req.password
        ),
        None,
    )
    if not user:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    return LoginResponse(
        id=user["id"], username=user["username"], display_name=user["display_name"]
    )


@router.post("/register", response_model=LoginResponse)
def register(req: RegisterRequest):
    if not req.username or not req.password or not req.display_name:
        raise HTTPException(status_code=400, detail="請填寫所有欄位")
    if req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="密碼不一致")
    if store.find_user_by_name(req.username):
        raise HTTPException(status_code=400, detail="此帳號已被註冊")
    new_user = store.add_user(req.username, req.password, req.display_name)
    return LoginResponse(
        id=new_user["id"],
        username=new_user["username"],
        display_name=new_user["display_name"],
    )


# ---------------------------------------------------------------------------
# Leave endpoints
# ---------------------------------------------------------------------------


@router.get("/leaves")
def get_leaves(user_id: int | None = None):
    if user_id is not None:
        filtered = [L for L in store.leaves if L["user_id"] == user_id]
        return sorted(filtered, key=lambda x: (x["leave_date"], x["start_time"]))
    return store.leaves


@router.post("/leaves")
def create_leave(user_id: int, body: LeaveCreate):
    user = store.find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="使用者不存在")
    if not body.leave_date or not body.start_time or not body.end_time:
        raise HTTPException(status_code=400, detail="請填寫所有必要欄位")
    if body.start_time >= body.end_time:
        raise HTTPException(status_code=400, detail="開始時間必須早於結束時間")
    for L in store.leaves:
        if L["user_id"] == user_id and L["leave_date"] == body.leave_date:
            if body.start_time < L["end_time"] and body.end_time > L["start_time"]:
                raise HTTPException(
                    status_code=409,
                    detail=f"與現有預約衝突 ({L['start_time']} - {L['end_time']})",
                )
    new_leave = store.add_leave(
        user_id=user_id,
        leave_date=body.leave_date,
        start_time=body.start_time,
        end_time=body.end_time,
        note=body.note,
        display_name=user["display_name"],
    )
    return new_leave


@router.put("/leaves/{leave_id}")
def update_leave(leave_id: int, user_id: int, body: LeaveUpdate):
    leave = next((L for L in store.leaves if L["id"] == leave_id), None)
    if not leave:
        raise HTTPException(status_code=404, detail="休假紀錄不存在")
    if not body.leave_date or not body.start_time or not body.end_time:
        raise HTTPException(status_code=400, detail="請填寫所有必要欄位")
    if body.start_time >= body.end_time:
        raise HTTPException(status_code=400, detail="開始時間必須早於結束時間")
    for L in store.leaves:
        if L["id"] == leave_id:
            continue
        if L["user_id"] == user_id and L["leave_date"] == body.leave_date:
            if body.start_time < L["end_time"] and body.end_time > L["start_time"]:
                raise HTTPException(
                    status_code=409,
                    detail=f"與現有預約衝突 ({L['start_time']} - {L['end_time']})",
                )
    leave["leave_date"] = body.leave_date
    leave["start_time"] = body.start_time
    leave["end_time"] = body.end_time
    leave["note"] = body.note
    store._bump()
    return leave


@router.delete("/leaves/{leave_id}")
def delete_leave(leave_id: int):
    if not store.delete_leave(leave_id):
        raise HTTPException(status_code=404, detail="休假紀錄不存在")
    return {"message": "已刪除休假記錄"}


# ---------------------------------------------------------------------------
# Calendar endpoints
# ---------------------------------------------------------------------------


def _get_color_class(name: str) -> str:
    colors = ["indigo", "emerald", "amber", "rose", "cyan", "purple", "teal", "orange"]
    idx = sum(ord(c) for c in name) % len(colors)
    return colors[idx]


@router.get("/calendar/month")
def calendar_month(year: int, month: int):
    cal = _calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(year, month)
    today = datetime.now()
    grid = []
    for week in weeks:
        row = []
        for day in week:
            is_today = year == today.year and month == today.month and day == today.day
            date_str = f"{year}-{month:02d}-{day:02d}" if day > 0 else ""
            leaves_on_day = []
            if date_str:
                leaves_on_day = [
                    {**L, "color": _get_color_class(L["display_name"])}
                    for L in store.leaves
                    if L["leave_date"] == date_str
                ]
            row.append({
                "day": day,
                "is_current_month": day > 0,
                "is_today": is_today,
                "date_str": date_str,
                "leaves": leaves_on_day,
            })
        grid.append(row)
    return {"year": year, "month": month, "grid": grid}


@router.get("/calendar/week")
def calendar_week(year: int, month: int, day: int):
    date = datetime(year, month, day)
    start = date - timedelta(days=date.weekday())
    today = datetime.now()
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    columns = []
    for i in range(7):
        curr = start + timedelta(days=i)
        date_str = f"{curr.year}-{curr.month:02d}-{curr.day:02d}"
        is_today = curr.year == today.year and curr.month == today.month and curr.day == today.day
        day_leaves = [
            {**L, "color": _get_color_class(L["display_name"])}
            for L in store.leaves
            if L["leave_date"] == date_str
        ]
        day_leaves.sort(key=lambda x: x["start_time"])
        columns.append({
            "date_str": date_str,
            "day_num": curr.day,
            "weekday_label": weekdays[i],
            "is_today": is_today,
            "leaves": day_leaves,
        })
    return {"columns": columns}


@router.get("/calendar/day")
def calendar_day(year: int, month: int, day: int):
    date_str = f"{year}-{month:02d}-{day:02d}"
    day_leaves = [
        {**L, "color": _get_color_class(L["display_name"])}
        for L in store.leaves
        if L["leave_date"] == date_str
    ]
    hours_data = []
    for h in range(24):
        hour_str = f"{h:02d}:00"
        hour_next = f"{h + 1:02d}:00" if h < 23 else "24:00"
        active = [cl for cl in day_leaves if cl["start_time"] < hour_next and cl["end_time"] > hour_str]
        hours_data.append({"hour_str": hour_str, "leaves": active})
    return {"date_str": date_str, "hours": hours_data}


# ---------------------------------------------------------------------------
# Admin endpoints
# ---------------------------------------------------------------------------


@router.post("/admin/login")
def admin_login(req: AdminLoginRequest):
    if req.username == "admin" and req.password == "admin":
        return {"message": "管理者登入成功"}
    raise HTTPException(status_code=401, detail="管理者帳號或密碼錯誤")


@router.get("/admin/users")
def list_users():
    return [
        {"id": u["id"], "username": u["username"], "display_name": u["display_name"]}
        for u in store.users
    ]


@router.post("/admin/users")
def create_user(body: UserCreate):
    if not body.username or not body.password or not body.display_name:
        raise HTTPException(status_code=400, detail="請填寫所有欄位")
    if store.find_user_by_name(body.username):
        raise HTTPException(status_code=400, detail="此帳號已被使用")
    new_user = store.add_user(body.username, body.password, body.display_name)
    return {"id": new_user["id"], "username": new_user["username"], "display_name": new_user["display_name"]}


@router.put("/admin/users/{user_id}")
def update_user(user_id: int, body: UserUpdate):
    user = store.find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="使用者不存在")
    user["username"] = body.username
    user["password_hash"] = body.password
    user["display_name"] = body.display_name
    store._bump()
    return {"id": user["id"], "username": user["username"], "display_name": user["display_name"]}


@router.delete("/admin/users/{user_id}")
def delete_user(user_id: int):
    if user_id == 1:
        raise HTTPException(status_code=400, detail="不能刪除預設管理員帳號")
    if not store.delete_user(user_id):
        raise HTTPException(status_code=404, detail="使用者不存在")
    return {"message": "使用者已刪除"}


# ---------------------------------------------------------------------------
# Message endpoints
# ---------------------------------------------------------------------------


@router.get("/messages")
def list_messages():
    return sorted(store.messages, key=lambda x: x["submitted_at"], reverse=True)


@router.post("/messages")
def create_message(body: MessageCreate):
    if not all([body.employee_id, body.name, body.email, body.contact_value, body.message]):
        raise HTTPException(status_code=400, detail="請填寫所有欄位")
    new_msg = store.add_message(
        employee_id=body.employee_id,
        name=body.name,
        email=body.email,
        contact_method=body.contact_method,
        contact_value=body.contact_value,
        message=body.message,
        submitted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    return new_msg


@router.delete("/messages/{msg_id}")
def delete_message(msg_id: int):
    if not store.delete_message(msg_id):
        raise HTTPException(status_code=404, detail="留言不存在")
    return {"message": "留言已刪除"}
