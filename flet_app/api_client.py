"""
API client for the Time-Off Planning System backend.
"""

from __future__ import annotations

import os

import httpx


def _default_base() -> str:
    """Pick the right default base URL for the current platform.

    - Android emulator: ``10.0.2.2`` to reach the host's localhost.
    - iOS simulator / desktop / web: ``127.0.0.1`` works directly.
    - Override with env var ``API_BASE_URL`` for any platform.
    """
    env = os.environ.get("API_BASE_URL")
    if env:
        return env
    # When packaged with serious_python for Android, sys.platform is 'linux'
    # and the ANDROID_BOOTLOGO env var (or others) are present.
    if os.environ.get("ANDROID_BOOTLOGO") or os.environ.get("ANDROID_ROOT"):
        return "http://10.0.2.2:8000"
    return "http://127.0.0.1:8000"


DEFAULT_BASE = _default_base()


class ApiClient:
    """Thin wrapper around the REST API."""

    def __init__(self, base_url: str = DEFAULT_BASE) -> None:
        self.base = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base, timeout=10)
        # current session
        self.user_id: int | None = None
        self.username: str = ""
        self.display_name: str = ""
        self.is_admin: bool = False

    def reconfigure(self, base_url: str) -> None:
        """Switch to a different backend URL (e.g. after platform detection)."""
        self.base = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base, timeout=10)

    # -- Revision ------------------------------------------------------------

    def get_revision(self) -> int:
        """Return the current data-store revision number (lightweight)."""
        r = self._client.get("/api/revision")
        r.raise_for_status()
        return r.json()["revision"]

    # -- Auth ----------------------------------------------------------------

    def login(self, username: str, password: str) -> dict:
        r = self._client.post("/api/login", json={"username": username, "password": password})
        r.raise_for_status()
        data = r.json()
        self.user_id = data["id"]
        self.username = data["username"]
        self.display_name = data["display_name"]
        return data

    def register(self, username: str, password: str, confirm: str, display_name: str) -> dict:
        r = self._client.post("/api/register", json={
            "username": username,
            "password": password,
            "confirm_password": confirm,
            "display_name": display_name,
        })
        r.raise_for_status()
        return r.json()

    def logout(self) -> None:
        self.user_id = None
        self.username = ""
        self.display_name = ""
        self.is_admin = False

    # -- Leaves --------------------------------------------------------------

    def get_my_leaves(self) -> list[dict]:
        r = self._client.get("/api/leaves", params={"user_id": self.user_id})
        r.raise_for_status()
        return r.json()

    def get_all_leaves(self) -> list[dict]:
        r = self._client.get("/api/leaves")
        r.raise_for_status()
        return r.json()

    def create_leave(self, leave_date: str, start_time: str, end_time: str, note: str = "") -> dict:
        r = self._client.post("/api/leaves", params={"user_id": self.user_id}, json={
            "leave_date": leave_date,
            "start_time": start_time,
            "end_time": end_time,
            "note": note,
        })
        r.raise_for_status()
        return r.json()

    def update_leave(self, leave_id: int, leave_date: str, start_time: str, end_time: str, note: str = "") -> dict:
        r = self._client.put(f"/api/leaves/{leave_id}", params={"user_id": self.user_id}, json={
            "leave_date": leave_date,
            "start_time": start_time,
            "end_time": end_time,
            "note": note,
        })
        r.raise_for_status()
        return r.json()

    def delete_leave(self, leave_id: int) -> dict:
        r = self._client.delete(f"/api/leaves/{leave_id}")
        r.raise_for_status()
        return r.json()

    # -- Calendar ------------------------------------------------------------

    def get_calendar_month(self, year: int, month: int) -> dict:
        r = self._client.get("/api/calendar/month", params={"year": year, "month": month})
        r.raise_for_status()
        return r.json()

    def get_calendar_week(self, year: int, month: int, day: int) -> dict:
        r = self._client.get("/api/calendar/week", params={"year": year, "month": month, "day": day})
        r.raise_for_status()
        return r.json()

    def get_calendar_day(self, year: int, month: int, day: int) -> dict:
        r = self._client.get("/api/calendar/day", params={"year": year, "month": month, "day": day})
        r.raise_for_status()
        return r.json()

    # -- Admin ---------------------------------------------------------------

    def admin_login(self, username: str, password: str) -> dict:
        r = self._client.post("/api/admin/login", json={"username": username, "password": password})
        r.raise_for_status()
        self.is_admin = True
        return r.json()

    def admin_list_users(self) -> list[dict]:
        r = self._client.get("/api/admin/users")
        r.raise_for_status()
        return r.json()

    def admin_create_user(self, username: str, password: str, display_name: str) -> dict:
        r = self._client.post("/api/admin/users", json={
            "username": username, "password": password, "display_name": display_name,
        })
        r.raise_for_status()
        return r.json()

    def admin_update_user(self, user_id: int, username: str, password: str, display_name: str) -> dict:
        r = self._client.put(f"/api/admin/users/{user_id}", json={
            "username": username, "password": password, "display_name": display_name,
        })
        r.raise_for_status()
        return r.json()

    def admin_delete_user(self, user_id: int) -> dict:
        r = self._client.delete(f"/api/admin/users/{user_id}")
        r.raise_for_status()
        return r.json()

    # -- Messages ------------------------------------------------------------

    def list_messages(self) -> list[dict]:
        r = self._client.get("/api/messages")
        r.raise_for_status()
        return r.json()

    def create_message(self, employee_id: str, name: str, email: str,
                       contact_method: str, contact_value: str, message: str) -> dict:
        r = self._client.post("/api/messages", json={
            "employee_id": employee_id,
            "name": name,
            "email": email,
            "contact_method": contact_method,
            "contact_value": contact_value,
            "message": message,
        })
        r.raise_for_status()
        return r.json()

    def delete_message(self, msg_id: int) -> dict:
        r = self._client.delete(f"/api/messages/{msg_id}")
        r.raise_for_status()
        return r.json()
