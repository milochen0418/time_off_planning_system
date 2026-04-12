import reflex as rx
import asyncio
from typing import Optional, TypedDict


class User(TypedDict):
    id: int
    username: str
    password_hash: str
    display_name: str


class AuthState(rx.State):
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
    users: list[User] = [
        {
            "id": 1,
            "username": "admin",
            "password_hash": "admin123",
            "display_name": "管理員",
        }
    ]

    @rx.event
    def login(self):
        self.login_error = ""
        found_user = None
        for u in self.users:
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
        for u in self.users:
            if u["username"] == self.reg_username:
                self.register_error = "此帳號已被註冊"
                return
        new_user: User = {
            "id": len(self.users) + 1,
            "username": self.reg_username,
            "password_hash": self.reg_password,
            "display_name": self.reg_display_name,
        }
        self.users.append(new_user)
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