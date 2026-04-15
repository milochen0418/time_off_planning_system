import reflex as rx
from typing import TypedDict, Optional
from time_off_planning_system.store import store, User
from time_off_planning_system.i18n import get_text


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
    async def admin_login(self):
        from time_off_planning_system.states.lang_state import LangState
        lang_state = await self.get_state(LangState)
        lang = lang_state.lang
        if (
            self.admin_login_username == "admin"
            and self.admin_login_password == "admin"
        ):
            self.admin_logged_in = True
            self.admin_login_error = ""
            return rx.redirect("/admin")
        else:
            self.admin_login_error = get_text(lang, "invalid_admin_credentials")

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
    def open_edit_user_form(self, user_id: int):
        user = store.find_user(user_id)
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
        from time_off_planning_system.states.auth_state import AuthState
        from time_off_planning_system.states.lang_state import LangState

        lang_state = await self.get_state(LangState)
        lang = lang_state.lang
        if (
            not self.form_username
            or not self.form_password
            or (not self.form_display_name)
        ):
            self.form_error = get_text(lang, "fill_all_fields")
            return
        if self.editing_user_id == -1:
            if store.find_user_by_name(self.form_username):
                self.form_error = get_text(lang, "username_in_use")
                return
            store.add_user(
                self.form_username, self.form_password, self.form_display_name
            )
            yield rx.toast(f"{get_text(lang, 'user_added_prefix')}{self.form_display_name}")
        else:
            store.update_user(
                self.editing_user_id,
                username=self.form_username,
                password_hash=self.form_password,
                display_name=self.form_display_name,
            )
            yield rx.toast(get_text(lang, "user_updated"))
        # Bump AuthState._rev so its `users` computed var recomputes
        auth = await self.get_state(AuthState)
        auth._rev += 1
        self.show_user_form = False

    @rx.event
    async def delete_user(self, user_id: int):
        from time_off_planning_system.states.auth_state import AuthState
        from time_off_planning_system.states.lang_state import LangState

        lang_state = await self.get_state(LangState)
        lang = lang_state.lang
        if user_id == 1:
            yield rx.toast(get_text(lang, "cannot_delete_admin"))
            return
        store.delete_user(user_id)
        auth = await self.get_state(AuthState)
        auth._rev += 1
        yield rx.toast(get_text(lang, "user_deleted"))