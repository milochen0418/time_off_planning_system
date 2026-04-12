"""
Shared in-memory data store — the single source of truth.

Both the Reflex web app (states) and the REST API read/write this store,
ensuring that data stays in sync between the browser and the Flet mobile app.
"""

from __future__ import annotations

from typing import TypedDict


class User(TypedDict):
    id: int
    username: str
    password_hash: str
    display_name: str


class Leave(TypedDict):
    id: int
    user_id: int
    leave_date: str
    start_time: str
    end_time: str
    note: str
    display_name: str


class Message(TypedDict):
    id: int
    employee_id: str
    name: str
    email: str
    contact_method: str
    contact_value: str
    message: str
    submitted_at: str


class DataStore:
    """Process-level singleton that holds all application data."""

    def __init__(self) -> None:
        self.users: list[User] = [
            {
                "id": 1,
                "username": "admin",
                "password_hash": "admin123",
                "display_name": "管理員",
            }
        ]
        self.leaves: list[Leave] = []
        self.messages: list[Message] = []
        self._next_user_id: int = 2
        self._next_leave_id: int = 1
        self._next_msg_id: int = 1

    # ── User helpers ──────────────────────────────────────────────────────

    def find_user(self, user_id: int) -> User | None:
        return next((u for u in self.users if u["id"] == user_id), None)

    def find_user_by_name(self, username: str) -> User | None:
        return next((u for u in self.users if u["username"] == username), None)

    def add_user(self, username: str, password: str, display_name: str) -> User:
        new_user: User = {
            "id": self._next_user_id,
            "username": username,
            "password_hash": password,
            "display_name": display_name,
        }
        self.users.append(new_user)
        self._next_user_id += 1
        return new_user

    # ── Leave helpers ─────────────────────────────────────────────────────

    def add_leave(
        self,
        user_id: int,
        leave_date: str,
        start_time: str,
        end_time: str,
        note: str,
        display_name: str,
    ) -> Leave:
        new_leave: Leave = {
            "id": self._next_leave_id,
            "user_id": user_id,
            "leave_date": leave_date,
            "start_time": start_time,
            "end_time": end_time,
            "note": note,
            "display_name": display_name,
        }
        self.leaves.append(new_leave)
        self._next_leave_id += 1
        return new_leave

    # ── Message helpers ───────────────────────────────────────────────────

    def add_message(
        self,
        employee_id: str,
        name: str,
        email: str,
        contact_method: str,
        contact_value: str,
        message: str,
        submitted_at: str,
    ) -> Message:
        new_msg: Message = {
            "id": self._next_msg_id,
            "employee_id": employee_id,
            "name": name,
            "email": email,
            "contact_method": contact_method,
            "contact_value": contact_value,
            "message": message,
            "submitted_at": submitted_at,
        }
        self.messages.append(new_msg)
        self._next_msg_id += 1
        return new_msg


# Module-level singleton — imported by both states and api
store = DataStore()
