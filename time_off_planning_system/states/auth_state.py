import reflex as rx
import asyncio
from typing import Optional, TypedDict

from time_off_planning_system.store import store, User


class AuthState(rx.State):
    _rev: int = 0
    _last_store_rev: int = 0
    logged_in: bool = False
    current_user_id: int = -1
    current_username: str = ""
    current_display_name: str = ""
    login_username: str = ""
    login_password: str = ""
    login_error: str = ""
    reg_username: str = ""
    reg_password: str = ""
    reg_confirm_password: str = ""
    reg_display_name: str = ""
    register_error: str = ""
    register_success: str = ""

    @rx.var
    def users(self) -> list[User]:
        # Reference _rev so Reflex recomputes when data changes
        _ = self._rev
        return store.users

    @rx.event
    def login(self):
        self.login_error = ""
        found_user = None
        for u in store.users:
            if (
                u["username"] == self.login_username
                and u["password_hash"] == self.login_password
            ):
                found_user = u
                break
        if found_user:
            self.logged_in = True
            self.current_user_id = found_user["id"]
            self.current_username = found_user["username"]
            self.current_display_name = found_user["display_name"]
            self.login_username = ""
            self.login_password = ""
            return rx.redirect("/my-leaves")
        else:
            self.login_error = "帳號或密碼錯誤"

    @rx.event
    def register(self):
        self.register_error = ""
        self.register_success = ""
        if (
            not self.reg_username
            or not self.reg_password
            or (not self.reg_display_name)
        ):
            self.register_error = "請填寫所有欄位"
            return
        if self.reg_password != self.reg_confirm_password:
            self.register_error = "密碼不一致"
            return
        if store.find_user_by_name(self.reg_username):
            self.register_error = "此帳號已被註冊"
            return
        store.add_user(self.reg_username, self.reg_password, self.reg_display_name)
        self._rev += 1
        self.register_success = "註冊成功！請前往登入"
        self.reg_username = ""
        self.reg_password = ""
        self.reg_confirm_password = ""
        self.reg_display_name = ""

    @rx.event
    def logout(self):
        self.logged_in = False
        self.current_user_id = -1
        self.current_username = ""
        self.current_display_name = ""
        return rx.redirect("/login")

    @rx.event
    def check_auth(self):
        if not self.logged_in:
            return rx.redirect("/login")

    @rx.event
    def check_logged_in(self):
        if self.logged_in:
            return rx.redirect("/my-leaves")

    @rx.event
    def check_store_update(self, _timestamp: str):
        """Called periodically by rx.moment to detect external store changes."""
        if store.revision != self._last_store_rev:
            self._last_store_rev = store.revision
            self._rev += 1