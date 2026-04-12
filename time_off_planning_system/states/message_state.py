import reflex as rx
from typing import TypedDict
from datetime import datetime


class Message(TypedDict):
    id: int
    employee_id: str
    name: str
    email: str
    contact_method: str
    contact_value: str
    message: str
    submitted_at: str


class MessageState(rx.State):
    messages: list[Message] = []
    next_msg_id: int = 1
    form_employee_id: str = ""
    form_name: str = ""
    form_email: str = ""
    form_contact_method: str = "Line"
    form_contact_value: str = ""
    form_message: str = ""
    form_error: str = ""
    form_success: str = ""

    @rx.var
    def sorted_messages(self) -> list[Message]:
        return sorted(self.messages, key=lambda x: x["submitted_at"], reverse=True)

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
        new_msg: Message = {
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
        self.form_employee_id = ""
        self.form_name = ""
        self.form_email = ""
        self.form_contact_value = ""
        self.form_message = ""
        self.form_success = "留言已送出，管理者將盡快與您聯繫！"

    @rx.event
    def delete_message(self, msg_id: int):
        self.messages = [m for m in self.messages if m["id"] != msg_id]
        yield rx.toast("留言已刪除")