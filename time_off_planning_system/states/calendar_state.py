import reflex as rx
import calendar
from datetime import datetime, timedelta

from time_off_planning_system.store import store
from time_off_planning_system.i18n import MONTH_NAMES_EN, WEEKDAYS_FULL_EN, WEEKDAYS_FULL_ZH


def get_color_class(name: str) -> str:
    colors = [
        "bg-indigo-100 text-indigo-800 border-indigo-200",
        "bg-emerald-100 text-emerald-800 border-emerald-200",
        "bg-amber-100 text-amber-800 border-amber-200",
        "bg-rose-100 text-rose-800 border-rose-200",
        "bg-cyan-100 text-cyan-800 border-cyan-200",
        "bg-purple-100 text-purple-800 border-purple-200",
        "bg-teal-100 text-teal-800 border-teal-200",
        "bg-orange-100 text-orange-800 border-orange-200",
    ]
    idx = sum((ord(c) for c in name)) % len(colors)
    return colors[idx]


class CalendarState(rx.State):
    current_year: int = datetime.now().year
    current_month: int = datetime.now().month
    current_day: int = datetime.now().day
    view_mode: str = "month"

    @rx.var
    async def display_title(self) -> str:
        from time_off_planning_system.states.lang_state import LangState
        lang_state = await self.get_state(LangState)
        lang = lang_state.lang

        if self.view_mode == "month":
            if lang == "en":
                return f"{MONTH_NAMES_EN[self.current_month]} {self.current_year}"
            return f"{self.current_year}年 {self.current_month}月"
        elif self.view_mode == "week":
            date = datetime(self.current_year, self.current_month, self.current_day)
            start = date - timedelta(days=date.weekday())
            end = start + timedelta(days=6)
            if lang == "en":
                return f"{MONTH_NAMES_EN[self.current_month]} {self.current_year} ({start.month}/{start.day} - {end.month}/{end.day})"
            return f"{self.current_year}年 {self.current_month}月 ({start.month}/{start.day} - {end.month}/{end.day})"
        else:
            date = datetime(self.current_year, self.current_month, self.current_day)
            if lang == "en":
                return f"{MONTH_NAMES_EN[self.current_month]} {self.current_day}, {self.current_year} ({WEEKDAYS_FULL_EN[date.weekday()]})"
            weekdays = ["一", "二", "三", "四", "五", "六", "日"]
            return f"{self.current_year}年 {self.current_month}月 {self.current_day}日 (星期{weekdays[date.weekday()]})"

    @rx.var
    async def weekday_headers(self) -> list[str]:
        from time_off_planning_system.states.lang_state import LangState
        lang_state = await self.get_state(LangState)
        lang = lang_state.lang
        if lang == "en":
            return ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        return ["日", "一", "二", "三", "四", "五", "六"]

    def _compute_week_dates(self, lang: str) -> list[dict]:
        date = datetime(self.current_year, self.current_month, self.current_day)
        start = date - timedelta(days=date.weekday())
        today = datetime.now()
        weekdays_zh = ["一", "二", "三", "四", "五", "六", "日"]
        weekdays_en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        weekdays = weekdays_en if lang == "en" else weekdays_zh
        dates = []
        for i in range(7):
            curr = start + timedelta(days=i)
            is_today = (
                curr.year == today.year
                and curr.month == today.month
                and (curr.day == today.day)
            )
            dates.append(
                {
                    "date_str": f"{curr.year}-{curr.month:02d}-{curr.day:02d}",
                    "day_num": curr.day,
                    "weekday_label": weekdays[i],
                    "is_today": is_today,
                }
            )
        return dates

    @rx.var
    async def week_dates(self) -> list[dict]:
        from time_off_planning_system.states.lang_state import LangState
        lang_state = await self.get_state(LangState)
        return self._compute_week_dates(lang_state.lang)

    @rx.var
    def month_grid(self) -> list[list[dict[str, str | int | bool]]]:
        cal = calendar.Calendar(firstweekday=6)  # Sunday first
        today = datetime.now()
        weeks: list[list[dict[str, str | int | bool]]] = []
        for week in cal.monthdayscalendar(self.current_year, self.current_month):
            row: list[dict[str, str | int | bool]] = []
            for day in week:
                if day == 0:
                    row.append(
                        {
                            "day": 0,
                            "date_str": "",
                            "is_today": False,
                            "is_current_month": False,
                        }
                    )
                else:
                    is_today = (
                        self.current_year == today.year
                        and self.current_month == today.month
                        and day == today.day
                    )
                    row.append(
                        {
                            "day": day,
                            "date_str": f"{self.current_year}-{self.current_month:02d}-{day:02d}",
                            "is_today": is_today,
                            "is_current_month": True,
                        }
                    )
            weeks.append(row)
        return weeks

    @rx.var
    def current_date_str(self) -> str:
        return f"{self.current_year}-{self.current_month:02d}-{self.current_day:02d}"

    @rx.var
    def hours_list(self) -> list[str]:
        return [f"{h:02d}:00" for h in range(0, 24)]

    @rx.var
    async def week_columns(
        self,
    ) -> list[dict[str, str | int | bool | list[dict[str, str | int]]]]:
        from time_off_planning_system.states.leave_state import LeaveState
        from time_off_planning_system.states.lang_state import LangState

        leave_state = await self.get_state(LeaveState)
        lang_state = await self.get_state(LangState)
        _ = leave_state._rev
        all_leaves = store.leaves
        cols: list[dict[str, str | int | bool | list[dict[str, str | int]]]] = []
        week_dates = self._compute_week_dates(lang_state.lang)
        for d in week_dates:
            date_str = d["date_str"]
            day_leaves: list[dict[str, str | int]] = []
            for L in all_leaves:
                if L["leave_date"] == date_str:
                    cl: dict[str, str | int] = {
                        "id": L["id"],
                        "user_id": L["user_id"],
                        "leave_date": L["leave_date"],
                        "start_time": L["start_time"],
                        "end_time": L["end_time"],
                        "note": L["note"],
                        "display_name": L["display_name"],
                        "color_class": get_color_class(L["display_name"]),
                    }
                    day_leaves.append(cl)
            day_leaves.sort(key=lambda x: str(x["start_time"]))
            col: dict[str, str | int | bool | list[dict[str, str | int]]] = {
                "date_str": d["date_str"],
                "day_num": d["day_num"],
                "weekday_label": d["weekday_label"],
                "is_today": d["is_today"],
                "leaves": day_leaves,
            }
            cols.append(col)
        return cols

    @rx.var
    async def day_hours(self) -> list[dict[str, str | list[dict[str, str | int]]]]:
        from time_off_planning_system.states.leave_state import LeaveState

        leave_state = await self.get_state(LeaveState)
        _ = leave_state._rev
        all_leaves = store.leaves
        date_str = self.current_date_str
        day_leaves: list[dict[str, str | int]] = []
        for L in all_leaves:
            if L["leave_date"] == date_str:
                cl: dict[str, str | int] = {
                    "id": L["id"],
                    "user_id": L["user_id"],
                    "leave_date": L["leave_date"],
                    "start_time": L["start_time"],
                    "end_time": L["end_time"],
                    "note": L["note"],
                    "display_name": L["display_name"],
                    "color_class": get_color_class(L["display_name"]),
                }
                day_leaves.append(cl)
        hours_data: list[dict[str, str | list[dict[str, str | int]]]] = []
        for h in range(0, 24):
            hour_str = f"{h:02d}:00"
            hour_next = f"{h + 1:02d}:00" if h < 23 else "24:00"
            active_leaves: list[dict[str, str | int]] = []
            for cl in day_leaves:
                if str(cl["start_time"]) < hour_next and str(cl["end_time"]) > hour_str:
                    active_leaves.append(cl)
            hours_data.append({"hour_str": hour_str, "leaves": active_leaves})
        return hours_data

    @rx.event
    def set_view_mode(self, mode: str):
        self.view_mode = mode

    @rx.event
    def go_prev(self):
        if self.view_mode == "month":
            if self.current_month == 1:
                self.current_month = 12
                self.current_year -= 1
            else:
                self.current_month -= 1
        else:
            date = datetime(self.current_year, self.current_month, self.current_day)
            delta = timedelta(days=7) if self.view_mode == "week" else timedelta(days=1)
            new_date = date - delta
            self.current_year = new_date.year
            self.current_month = new_date.month
            self.current_day = new_date.day

    @rx.event
    def go_next(self):
        if self.view_mode == "month":
            if self.current_month == 12:
                self.current_month = 1
                self.current_year += 1
            else:
                self.current_month += 1
        else:
            date = datetime(self.current_year, self.current_month, self.current_day)
            delta = timedelta(days=7) if self.view_mode == "week" else timedelta(days=1)
            new_date = date + delta
            self.current_year = new_date.year
            self.current_month = new_date.month
            self.current_day = new_date.day

    @rx.event
    def go_today(self):
        today = datetime.now()
        self.current_year = today.year
        self.current_month = today.month
        self.current_day = today.day

    @rx.event
    def select_day(self, day: int):
        if day > 0:
            self.current_day = day
            self.view_mode = "day"