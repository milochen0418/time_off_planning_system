import reflex as rx
from typing import TypedDict
from datetime import datetime

from time_off_planning_system.store import store, Message


class MessageState(rx.State):
    _rev: int = 0
    _last_store_rev: int = 0
    form_employee_id: str = ""
    form_name: str = ""
    form_email: str = ""
    form_contact_method: str = "Line"
    form_contact_value: str = ""
    form_message: str = ""
    form_error: str = ""
    form_success: str = ""

    @rx.var
    def messages(self) -> list[Message]:
        _ = self._rev
        return store.messages

    @rx.var
    def sorted_messages(self) -> list[Message]:
        _ = self._rev
        return sorted(store.messages, key=lambda x: x["submitted_at"], reverse=True)

    @rx.event
    def load_messages(self):
        """Bump revision to force recompute from store."""
        self._rev += 1

    @rx.event
    def set_contact_method(self, value: str):
        self.form_contact_method = value
        self.form_contact_value = ""

    @rx.event
    def submit_message(self):
        self.form_error = ""
        self.form_success = ""
        if not all(
            [
                self.form_employee_id,
                self.form_name,
                self.form_email,
                self.form_contact_value,
                self.form_message,
            ]
        ):
            self.form_error = "請填寫所有欄位"
            return
        store.add_message(
            employee_id=self.form_employee_id,
            name=self.form_name,
            email=self.form_email,
            contact_method=self.form_contact_method,
            contact_value=self.form_contact_value,
            message=self.form_message,
            submitted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self._rev += 1
        self.form_employee_id = ""
        self.form_name = ""
        self.form_email = ""
        self.form_contact_value = ""
        self.form_message = ""
        self.form_success = "留言已送出，管理者將盡快與您聯繫！"

    @rx.event
    def delete_message(self, msg_id: int):
        store.delete_message(msg_id)
        self._rev += 1
        yield rx.toast("留言已刪除")

    @rx.event
    def check_store_update(self, _timestamp: str):
        """Called periodically by rx.moment to detect external store changes."""
        if store.revision != self._last_store_rev:
            self._last_store_rev = store.revision
            self._rev += 1