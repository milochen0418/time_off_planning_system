import reflex as rx
from typing import TypedDict
import logging

from time_off_planning_system.store import store, Leave
from time_off_planning_system.i18n import get_text


class LeaveState(rx.State):
    _rev: int = 0
    _last_store_rev: int = 0
    form_date: str = ""
    form_start_time: str = ""
    form_end_time: str = ""
    form_note: str = ""
    editing_id: int = -1
    show_form: bool = False
    form_error: str = ""

    @rx.var
    async def my_leaves(self) -> list[Leave]:
        _ = self._rev
        from time_off_planning_system.states.auth_state import AuthState

        auth = await self.get_state(AuthState)
        user_id = auth.current_user_id
        filtered = [L for L in store.leaves if L["user_id"] == user_id]
        return sorted(filtered, key=lambda x: (x["leave_date"], x["start_time"]))

    @rx.var
    def all_leaves(self) -> list[Leave]:
        _ = self._rev
        return store.leaves

    @rx.event
    def load_leaves(self):
        """Bump revision to force recompute from store (e.g. picks up API data)."""
        self._rev += 1

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
        leave = next((L for L in store.leaves if L["id"] == leave_id), None)
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
        from time_off_planning_system.states.lang_state import LangState

        auth = await self.get_state(AuthState)
        lang_state = await self.get_state(LangState)
        lang = lang_state.lang
        if not self.form_date or not self.form_start_time or (not self.form_end_time):
            self.form_error = get_text(lang, "fill_required_fields")
            return
        if self.form_start_time >= self.form_end_time:
            self.form_error = get_text(lang, "start_before_end")
            return
        user_id = auth.current_user_id
        for L in store.leaves:
            if self.editing_id != -1 and L["id"] == self.editing_id:
                continue
            if L["user_id"] == user_id and L["leave_date"] == self.form_date:
                if (
                    self.form_start_time < L["end_time"]
                    and self.form_end_time > L["start_time"]
                ):
                    self.form_error = (
                        f"{get_text(lang, 'conflict_prefix')} ({L['start_time']} - {L['end_time']})"
                    )
                    return
        if self.editing_id == -1:
            store.add_leave(
                user_id=user_id,
                leave_date=self.form_date,
                start_time=self.form_start_time,
                end_time=self.form_end_time,
                note=self.form_note,
                display_name=auth.current_display_name,
            )
            yield rx.toast(get_text(lang, "leave_added"), duration=3000)
        else:
            for i, L in enumerate(store.leaves):
                if L["id"] == self.editing_id:
                    store.leaves[i] = {
                        **L,
                        "leave_date": self.form_date,
                        "start_time": self.form_start_time,
                        "end_time": self.form_end_time,
                        "note": self.form_note,
                    }
                    store._bump()
                    break
            yield rx.toast(get_text(lang, "leave_updated"), duration=3000)
        self._rev += 1
        self.show_form = False

    @rx.event
    async def delete_leave(self, leave_id: int):
        from time_off_planning_system.states.lang_state import LangState
        lang_state = await self.get_state(LangState)
        lang = lang_state.lang
        store.delete_leave(leave_id)
        self._rev += 1
        yield rx.toast(get_text(lang, "leave_deleted"))

    @rx.event
    def check_store_update(self, _timestamp: str):
        """Called periodically by rx.moment to detect external store changes."""
        if store.revision != self._last_store_rev:
            self._last_store_rev = store.revision
            self._rev += 1