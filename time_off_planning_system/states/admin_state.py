import reflex as rx
from typing import TypedDict, Optional
from time_off_planning_system.states.auth_state import AuthState, User


class AdminState(rx.State):
    admin_logged_in: bool = False
    admin_login_username: str = ""
    admin_login_password: str = ""
    admin_login_error: str = ""
    active_tab: str = "users"
    show_user_form: bool = False
    editing_user_id: int = -1
    form_username: str = ""
    form_password: str = ""
    form_display_name: str = ""
    form_error: str = ""

    @rx.event
    def admin_login(self):
        if (
            self.admin_login_username == "admin"
            and self.admin_login_password == "admin"
        ):
            self.admin_logged_in = True
            self.admin_login_error = ""
            return rx.redirect("/admin")
        else:
            self.admin_login_error = "管理者帳號或密碼錯誤"

    @rx.event
    def admin_logout(self):
        self.admin_logged_in = False
        return rx.redirect("/admin-login")

    @rx.event
    def check_admin_auth(self):
        if not self.admin_logged_in:
            return rx.redirect("/admin-login")

    @rx.event
    def check_admin_logged_in(self):
        if self.admin_logged_in:
            return rx.redirect("/admin")

    @rx.event
    def set_active_tab(self, tab: str):
        self.active_tab = tab

    @rx.event
    def open_add_user_form(self):
        self.form_username = ""
        self.form_password = ""
        self.form_display_name = ""
        self.editing_user_id = -1
        self.form_error = ""
        self.show_user_form = True

    @rx.event
    async def open_edit_user_form(self, user_id: int):
        auth = await self.get_state(AuthState)
        user = next((u for u in auth.users if u["id"] == user_id), None)
        if user:
            self.form_username = user["username"]
            self.form_password = user["password_hash"]
            self.form_display_name = user["display_name"]
            self.editing_user_id = user_id
            self.form_error = ""
            self.show_user_form = True

    @rx.event
    def close_user_form(self):
        self.show_user_form = False
        self.form_error = ""

    @rx.event
    async def save_user(self):
        if (
            not self.form_username
            or not self.form_password
            or (not self.form_display_name)
        ):
            self.form_error = "請填寫所有欄位"
            return
        auth = await self.get_state(AuthState)
        if self.editing_user_id == -1:
            if any((u["username"] == self.form_username for u in auth.users)):
                self.form_error = "此帳號已被使用"
                return
            max_id = max([u["id"] for u in auth.users], default=0)
            new_user: User = {
                "id": max_id + 1,
                "username": self.form_username,
                "password_hash": self.form_password,
                "display_name": self.form_display_name,
            }
            auth.users.append(new_user)
            yield rx.toast(f"成功新增使用者: {self.form_display_name}")
        else:
            for i, u in enumerate(auth.users):
                if u["id"] == self.editing_user_id:
                    auth.users[i]["username"] = self.form_username
                    auth.users[i]["password_hash"] = self.form_password
                    auth.users[i]["display_name"] = self.form_display_name
                    break
            yield rx.toast(f"成功更新使用者資料")
        self.show_user_form = False

    @rx.event
    async def delete_user(self, user_id: int):
        auth = await self.get_state(AuthState)
        if user_id == 1:
            yield rx.toast("不能刪除預設管理員帳號")
            return
        auth.users = [u for u in auth.users if u["id"] != user_id]
        yield rx.toast("使用者已刪除")