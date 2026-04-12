import reflex as rx
import calendar
from datetime import datetime, timedelta

from time_off_planning_system.store import store


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
    def display_title(self) -> str:
        if self.view_mode == "month":
            return f"{self.current_year}年 {self.current_month}月"
        elif self.view_mode == "week":
            date = datetime(self.current_year, self.current_month, self.current_day)
            start = date - timedelta(days=date.weekday())
            end = start + timedelta(days=6)
            return f"{self.current_year}年 {self.current_month}月 ({start.month}/{start.day} - {end.month}/{end.day})"
        else:
            date = datetime(self.current_year, self.current_month, self.current_day)
            weekdays = ["一", "二", "三", "四", "五", "六", "日"]
            return f"{self.current_year}年 {self.current_month}月 {self.current_day}日 (星期{weekdays[date.weekday()]})"

    @rx.var
    def month_grid(self) -> list[list[dict]]:
        cal = calendar.Calendar(firstweekday=6)
        weeks = cal.monthdayscalendar(self.current_year, self.current_month)
        today = datetime.now()
        grid = []
        for week in weeks:
            row = []
            for day in week:
                is_today = (
                    self.current_year == today.year
                    and self.current_month == today.month
                    and (day == today.day)
                )
                date_str = ""
                if day > 0:
                    date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
                row.append(
                    {
                        "day": day,
                        "is_current_month": day > 0,
                        "is_today": is_today,
                        "date_str": date_str,
                    }
                )
            grid.append(row)
        return grid

    @rx.var
    def week_dates(self) -> list[dict]:
        date = datetime(self.current_year, self.current_month, self.current_day)
        start = date - timedelta(days=date.weekday())
        today = datetime.now()
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
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

        leave_state = await self.get_state(LeaveState)
        _ = leave_state._rev
        all_leaves = store.leaves
        cols: list[dict[str, str | int | bool | list[dict[str, str | int]]]] = []
        for d in self.week_dates:
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