import reflex as rx
from typing import TypedDict
import logging


class Leave(TypedDict):
    id: int
    user_id: int
    leave_date: str
    start_time: str
    end_time: str
    note: str
    display_name: str


class LeaveState(rx.State):
    leaves: list[Leave] = []
    form_date: str = ""
    form_start_time: str = ""
    form_end_time: str = ""
    form_note: str = ""
    editing_id: int = -1
    show_form: bool = False
    form_error: str = ""
    next_id: int = 1

    @rx.var
    async def my_leaves(self) -> list[Leave]:
        from time_off_planning_system.states.auth_state import AuthState

        auth = await self.get_state(AuthState)
        user_id = auth.current_user_id
        filtered = [L for L in self.leaves if L["user_id"] == user_id]
        return sorted(filtered, key=lambda x: (x["leave_date"], x["start_time"]))

    @rx.var
    def all_leaves(self) -> list[Leave]:
        return self.leaves

    @rx.event
    def load_leaves(self):
        pass

    @rx.event
    def open_add_form(self):
        self.form_date = ""
        self.form_start_time = ""
        self.form_end_time = ""
        self.form_note = ""
        self.editing_id = -1
        self.form_error = ""
        self.show_form = True

    @rx.event
    def open_edit_form(self, leave_id: int):
        leave = next((L for L in self.leaves if L["id"] == leave_id), None)
        if leave:
            self.form_date = leave["leave_date"]
            self.form_start_time = leave["start_time"]
            self.form_end_time = leave["end_time"]
            self.form_note = leave["note"]
            self.editing_id = leave_id
            self.form_error = ""
            self.show_form = True

    @rx.event
    def close_form(self):
        self.show_form = False
        self.form_error = ""

    @rx.event
    async def save_leave(self):
        from time_off_planning_system.states.auth_state import AuthState

        auth = await self.get_state(AuthState)
        if not self.form_date or not self.form_start_time or (not self.form_end_time):
            self.form_error = "請填寫所有必要欄位"
            return
        if self.form_start_time >= self.form_end_time:
            self.form_error = "開始時間必須早於結束時間"
            return
        user_id = auth.current_user_id
        for L in self.leaves:
            if self.editing_id != -1 and L["id"] == self.editing_id:
                continue
            if L["user_id"] == user_id and L["leave_date"] == self.form_date:
                if (
                    self.form_start_time < L["end_time"]
                    and self.form_end_time > L["start_time"]
                ):
                    self.form_error = (
                        f"與現有預約衝突 ({L['start_time']} - {L['end_time']})"
                    )
                    return
        if self.editing_id == -1:
            new_leave: Leave = {
                "id": self.next_id,
                "user_id": user_id,
                "leave_date": self.form_date,
                "start_time": self.form_start_time,
                "end_time": self.form_end_time,
                "note": self.form_note,
                "display_name": auth.current_display_name,
            }
            self.leaves.append(new_leave)
            self.next_id += 1
            yield rx.toast("成功新增休假", duration=3000)
        else:
            for i, L in enumerate(self.leaves):
                if L["id"] == self.editing_id:
                    self.leaves[i]["leave_date"] = self.form_date
                    self.leaves[i]["start_time"] = self.form_start_time
                    self.leaves[i]["end_time"] = self.form_end_time
                    self.leaves[i]["note"] = self.form_note
                    break
            yield rx.toast("成功更新休假", duration=3000)
        self.show_form = False

    @rx.event
    def delete_leave(self, leave_id: int):
        self.leaves = [L for L in self.leaves if L["id"] != leave_id]
        yield rx.toast("已刪除休假記錄")