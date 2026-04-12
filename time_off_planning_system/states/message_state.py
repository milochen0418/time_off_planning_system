import reflex as rx
from typing import TypedDict
from datetime import datetime

from time_off_planning_system.store import store, Message


class MessageState(rx.State):
    messages: list[dict] = []
    next_msg_id: int = 1
    form_employee_id: str = ""
    form_name: str = ""
    form_email: str = ""
    form_contact_method: str = "Line"
    form_contact_value: str = ""
    form_message: str = ""
    form_error: str = ""
    form_success: str = ""

    def _sync_to_store(self):
        """Write current state messages into the shared store for the REST API."""
        store.messages = list(self.messages)
        store._next_msg_id = self.next_msg_id

    @rx.var
    def sorted_messages(self) -> list[Message]:
        return sorted(self.messages, key=lambda x: x["submitted_at"], reverse=True)

    @rx.event
    def load_messages(self):
        """Sync from store on page load (picks up any API-created data)."""
        self.messages = list(store.messages)
        self.next_msg_id = store._next_msg_id

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
        new_msg: dict = {
            "id": self.next_msg_id,
            "employee_id": self.form_employee_id,
            "name": self.form_name,
            "email": self.form_email,
            "contact_method": self.form_contact_method,
            "contact_value": self.form_contact_value,
            "message": self.form_message,
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.messages.append(new_msg)
        self.next_msg_id += 1
        self._sync_to_store()
        self.form_employee_id = ""
        self.form_name = ""
        self.form_email = ""
        self.form_contact_value = ""
        self.form_message = ""
        self.form_success = "留言已送出，管理者將盡快與您聯繫！"

    @rx.event
    def delete_message(self, msg_id: int):
        self.messages = [m for m in self.messages if m["id"] != msg_id]
        self._sync_to_store()
        yield rx.toast("留言已刪除")