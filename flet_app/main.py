"""
Time-Off Planning System — Flet Desktop / Mobile Client
========================================================
Uses page.controls (page.add / page.clean) instead of page.views + page.go()
because the Views-based routing does not render on Flet mobile (APK).
"""

from __future__ import annotations

import asyncio
import calendar as _calendar
from datetime import datetime, timedelta

import flet as ft
from httpx import HTTPStatusError

from api_client import ApiClient
from i18n import t, get_lang, set_lang, MONTH_NAMES_EN, WEEKDAYS_FULL_EN

api = ApiClient()

# Module-level state for leave form editing (None = add new, int = edit existing)
_editing_leave_id: list[int | None] = [None]

# Background polling state
_last_revision: list[int] = [0]
_current_route: list[str] = ["/login"]
_poll_running: list[bool] = [False]
_page_ref: list[ft.Page | None] = [None]
_page_refresh_fn: list = [None]  # callable registered by my-leaves / calendar pages

# ── Color palette matching the web version ────────────────────────────────
INDIGO = "#4f46e5"
INDIGO_LIGHT = "#e0e7ff"
GRAY_50 = "#f9fafb"
GRAY_100 = "#f3f4f6"
GRAY_200 = "#e5e7eb"
GRAY_500 = "#6b7280"
GRAY_700 = "#374151"
GRAY_900 = "#111827"
RED = "#dc2626"
GREEN = "#16a34a"

LEAVE_COLORS = ["indigo", "teal", "amber", "rose", "cyan", "purple", "emerald", "orange"]
FLET_COLOR_MAP = {
    "indigo": ft.Colors.INDIGO_100,
    "teal": ft.Colors.TEAL_100,
    "amber": ft.Colors.AMBER_100,
    "rose": ft.Colors.PINK_100,
    "cyan": ft.Colors.CYAN_100,
    "purple": ft.Colors.PURPLE_100,
    "emerald": ft.Colors.GREEN_100,
    "orange": ft.Colors.ORANGE_100,
}
FLET_TEXT_COLOR_MAP = {
    "indigo": ft.Colors.INDIGO_800,
    "teal": ft.Colors.TEAL_800,
    "amber": ft.Colors.AMBER_800,
    "rose": ft.Colors.PINK_800,
    "cyan": ft.Colors.CYAN_800,
    "purple": ft.Colors.PURPLE_800,
    "emerald": ft.Colors.GREEN_800,
    "orange": ft.Colors.ORANGE_800,
}


def _color_for(name: str) -> str:
    idx = sum(ord(c) for c in name) % len(LEAVE_COLORS)
    return LEAVE_COLORS[idx]


# ── Background revision polling ───────────────────────────────────────────

def _start_polling(page: ft.Page):
    """Start an async polling task via page.run_task.

    Using page.run_task (async coroutine) instead of page.run_thread
    because page.run_task runs on the main Flet event loop, which
    guarantees page.update() works correctly on all platforms including
    Android/serious_python.
    """
    _page_ref[0] = page
    _poll_running[0] = True
    try:
        _last_revision[0] = api.get_revision()
    except Exception:
        pass
    page.run_task(_poll_async)


async def _poll_async():
    """Async polling loop: sleep → check revision → refresh current page.

    Uses httpx.AsyncClient for revision checks (httpx is NOT thread-safe,
    so each coroutine needs its own client).  When a revision change is
    detected, the registered _page_refresh_fn is run via asyncio.to_thread
    (sync HTTP fetch + control rebuild), then page.update() is called back
    on the event loop.
    """
    import httpx as _httpx

    async with _httpx.AsyncClient(base_url=api.base, timeout=5) as poll_client:
        while _poll_running[0]:
            await asyncio.sleep(3)
            page = _page_ref[0]
            if not page or (not api.user_id and not api.is_admin):
                continue

            try:
                r = await poll_client.get("/api/revision")
                r.raise_for_status()
                rev = r.json()["revision"]
                if rev != _last_revision[0]:
                    _last_revision[0] = rev
                    fn = _page_refresh_fn[0]
                    route = _current_route[0]
                    if fn and route in ("/my-leaves", "/calendar", "/admin"):
                        await asyncio.to_thread(fn)
                        page.update()
            except Exception:
                pass


# ── Helper: navigate by clearing page controls ────────────────────────────
def _nav(page: ft.Page, route: str):
    """Thread-safe navigate — schedules _navigate on the UI event loop.

    On mobile (iOS / Android) event-handler callbacks run on a worker thread.
    Calling _navigate directly from those callbacks silently fails because
    page.update() does not flush native views from a worker thread.
    This wrapper uses page.run_task() so the rebuild always runs on the
    correct event loop.
    """
    async def _go():
        _navigate(page, route)
    page.run_task(_go)


def _navigate(page: ft.Page, route: str):
    """Clear controls and rebuild the page for the given route."""
    _current_route[0] = route
    _page_refresh_fn[0] = None  # clear until a page re-registers
    page.controls.clear()
    page.overlay.clear()
    page.scroll = None
    page.padding = 0
    page.bgcolor = GRAY_50

    content: list[ft.Control] = []

    if route == "/my-leaves":
        if not api.user_id:
            _navigate(page, "/login")
            return
        content = [
            _navbar(page, "/my-leaves"),
            ft.Container(build_my_leaves_page(page), padding=20, expand=True),
        ]
    elif route == "/leave-form":
        if not api.user_id:
            _navigate(page, "/login")
            return
        content = [
            _navbar(page, "/my-leaves"),
            ft.Container(build_leave_form_page(page), padding=20, expand=True),
        ]
    elif route == "/calendar":
        if not api.user_id:
            _navigate(page, "/login")
            return
        content = [
            _navbar(page, "/calendar"),
            ft.Container(build_calendar_page(page), padding=20, expand=True),
        ]
    elif route == "/admin-login":
        content = [ft.Container(build_admin_login_page(page), padding=40, expand=True)]
    elif route == "/admin":
        content = [ft.Container(build_admin_page(page), padding=20, expand=True)]
    elif route == "/contact":
        content = [ft.Container(build_contact_page(page), padding=40, expand=True)]
    else:
        content = [ft.Container(build_login_page(page), padding=40, expand=True)]

    page.add(ft.SafeArea(ft.Column(content, expand=True), expand=True))
    page.update()


# ───────────────────────────────────────────────────────────────────────────
# LOGIN PAGE
# ───────────────────────────────────────────────────────────────────────────

def build_login_page(page: ft.Page):
    error_text = ft.Text("", color=RED, size=13)
    username_field = ft.TextField(label=t("username_label"), width=320)
    password_field = ft.TextField(label=t("password_label"), password=True, can_reveal_password=True, width=320)

    def _do_switch_lang(lang: str):
        """Switch language via page.run_task to ensure it runs on the UI event loop."""
        set_lang(lang)

        async def _rebuild():
            _navigate(page, "/login")

        page.run_task(_rebuild)

    zh_btn = ft.OutlinedButton(
        "中文",
        style=ft.ButtonStyle(
            bgcolor=INDIGO if get_lang() == "zh" else "white",
            color="white" if get_lang() == "zh" else GRAY_700,
            side=ft.BorderSide(1, INDIGO),
        ),
        on_click=lambda _e: _do_switch_lang("zh"),
    )
    en_btn = ft.OutlinedButton(
        "EN",
        style=ft.ButtonStyle(
            bgcolor=INDIGO if get_lang() == "en" else "white",
            color="white" if get_lang() == "en" else GRAY_700,
            side=ft.BorderSide(1, INDIGO),
        ),
        on_click=lambda _e: _do_switch_lang("en"),
    )

    def do_login(_e):
        error_text.value = ""
        try:
            api.login(username_field.value.strip(), password_field.value)
            _nav(page, "/my-leaves")
        except HTTPStatusError as exc:
            detail = exc.response.json().get("detail", t("login_failed"))
            error_text.value = detail
            page.update()
        except Exception:
            error_text.value = t("login_failed")
            page.update()

    def go_contact(_e):
        _nav(page, "/contact")

    def go_admin_login(_e):
        _nav(page, "/admin-login")

    return ft.Column(
        [
            ft.Row([ft.Container(expand=True), zh_btn, en_btn], alignment=ft.MainAxisAlignment.END),
            ft.Icon(ft.Icons.CALENDAR_MONTH, size=48, color=INDIGO),
            ft.Text(t("app_title"), size=28, weight=ft.FontWeight.BOLD),
            ft.Text(t("login_subtitle"), size=14, color=GRAY_500),
            ft.Container(height=10),
            username_field,
            password_field,
            error_text,
            ft.ElevatedButton(t("login_btn"), bgcolor=INDIGO, color="white", width=320, on_click=do_login),
            ft.Container(height=8),
            ft.Row([
                ft.Text(t("no_account"), color=GRAY_500, size=13),
                ft.TextButton(t("contact_admin_link"), on_click=go_contact),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.TextButton(t("admin_login_link"), on_click=go_admin_login,
                          style=ft.ButtonStyle(color=GRAY_500)),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
    )


# ───────────────────────────────────────────────────────────────────────────
# CONTACT / MESSAGE PAGE
# ───────────────────────────────────────────────────────────────────────────

def build_contact_page(page: ft.Page):
    error_text = ft.Text("", color=RED, size=13)
    success_text = ft.Text("", color=GREEN, size=13)
    emp_id = ft.TextField(label=t("employee_id_label"), width=400)
    name_f = ft.TextField(label=t("name_label"), width=400)
    email_f = ft.TextField(label=t("email_label"), width=400)
    contact_method = ft.Dropdown(
        label=t("contact_method_label"), width=400,
        options=[ft.dropdown.Option(m) for m in ["Line", "WhatsApp", "Phone", "Other"]],
        value="Line",
    )
    contact_value = ft.TextField(label=t("contact_value_label"), width=400)
    message_f = ft.TextField(label=t("message_content_label"), width=400, multiline=True, min_lines=3, max_lines=6)

    def submit(_e):
        error_text.value = ""
        success_text.value = ""
        try:
            api.create_message(
                emp_id.value.strip(), name_f.value.strip(), email_f.value.strip(),
                contact_method.value, contact_value.value.strip(), message_f.value.strip(),
            )
            success_text.value = t("message_sent")
            emp_id.value = name_f.value = email_f.value = contact_value.value = message_f.value = ""
        except HTTPStatusError as exc:
            error_text.value = exc.response.json().get("detail", t("submit_failed"))
        page.update()

    def go_back(_e):
        _nav(page, "/login")

    return ft.Column(
        [
            ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_back),
                     ft.Text(t("contact_admin_title"), size=22, weight=ft.FontWeight.BOLD)]),
            emp_id, name_f, email_f, contact_method, contact_value, message_f,
            error_text, success_text,
            ft.ElevatedButton(t("submit_message"), bgcolor=INDIGO, color="white", width=400, on_click=submit),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


# ───────────────────────────────────────────────────────────────────────────
# MY LEAVES PAGE
# ───────────────────────────────────────────────────────────────────────────

def build_my_leaves_page(page: ft.Page):
    leaves_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def _fetch_and_build():
        """Sync HTTP fetch + rebuild controls. NO page.update().

        Safe to call from a worker thread via asyncio.to_thread().
        """
        leaves_list.controls.clear()
        try:
            leaves = api.get_my_leaves()
        except Exception:
            leaves = []
        if not leaves:
            leaves_list.controls.append(
                ft.Container(
                    ft.Column([
                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=48, color=GRAY_200),
                        ft.Text(t("no_leaves"), size=16, weight=ft.FontWeight.W_500),
                        ft.Text(t("no_leaves_hint"), size=13, color=GRAY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40, alignment=ft.Alignment(0, 0),
                    border=ft.border.all(2, GRAY_200),
                    border_radius=12,
                ),
            )
        else:
            for lv in leaves:
                leaves_list.controls.append(_leave_card(lv))

    def _refresh():
        _fetch_and_build()
        page.update()

    def _leave_card(lv: dict) -> ft.Container:
        def edit(_e, lid=lv["id"]):
            _editing_leave_id[0] = lid
            _nav(page, "/leave-form")

        def delete(_e, lid=lv["id"]):
            try:
                api.delete_leave(lid)
            except Exception:
                pass
            _refresh()

        return ft.Container(
            ft.Row([
                ft.Column([
                    ft.Row([ft.Icon(ft.Icons.CALENDAR_MONTH, color=INDIGO, size=18),
                            ft.Text(lv["leave_date"], weight=ft.FontWeight.BOLD)]),
                    ft.Row([ft.Icon(ft.Icons.ACCESS_TIME, color=GRAY_500, size=16),
                            ft.Text(f"{lv['start_time']} - {lv['end_time']}", size=13, color=GRAY_500)]),
                    ft.Text(lv.get("note", ""), size=12, italic=True, color=GRAY_500) if lv.get("note") else ft.Container(),
                ], expand=True),
                ft.Row([
                    ft.IconButton(ft.Icons.EDIT, icon_color=GRAY_500, on_click=edit),
                    ft.IconButton(ft.Icons.DELETE, icon_color=RED, on_click=delete),
                ]),
            ]),
            padding=12, border=ft.border.all(1, GRAY_100), border_radius=10,
            bgcolor="white", margin=ft.margin.only(bottom=8),
        )

    def _open_add(_e):
        _editing_leave_id[0] = None
        _nav(page, "/leave-form")

    def _manual_refresh(_e):
        _refresh()

    _page_refresh_fn[0] = _fetch_and_build  # poll calls this in worker thread
    _refresh()

    return ft.Column([
        ft.Row([
            ft.Column([
                ft.Text(t("my_leaves_title"), size=22, weight=ft.FontWeight.BOLD),
                ft.Text(t("my_leaves_subtitle"), size=13, color=GRAY_500),
            ], expand=True),
            ft.IconButton(ft.Icons.REFRESH, icon_color=INDIGO, tooltip=t("refresh"), on_click=_manual_refresh),
            ft.ElevatedButton(t("add_leave"), icon=ft.Icons.ADD, bgcolor=INDIGO, color="white", on_click=_open_add),
        ]),
        ft.Divider(height=1),
        leaves_list,
    ], expand=True)


# ───────────────────────────────────────────────────────────────────────────
# LEAVE FORM PAGE (full page, no dialog — so DatePicker / TimePicker work)
# ───────────────────────────────────────────────────────────────────────────

def build_leave_form_page(page: ft.Page):
    editing_id = _editing_leave_id[0]
    is_edit = editing_id is not None
    form_error = ft.Text("", color=RED, size=13)
    debug_log = ft.Text("", color=GRAY_500, size=11)  # debug log visible on screen

    def _log(msg: str):
        """Append debug message visible on screen (serious_python has no logcat)."""
        debug_log.value = msg
        try:
            page.update()
        except Exception:
            pass

    # -- Resolve defaults --
    now = datetime.now()
    init_date = now.strftime("%Y-%m-%d")
    init_start = "09:00"
    init_end = "18:00"
    init_note = ""

    if is_edit:
        try:
            leaves = api.get_my_leaves()
            lv = next((l for l in leaves if l["id"] == editing_id), None)
            if lv:
                init_date = lv["leave_date"]
                init_start = lv["start_time"]
                init_end = lv["end_time"]
                init_note = lv.get("note", "")
        except Exception:
            pass

    # -- Display fields: use Text in styled Containers (TextField steals tap) --
    date_text = ft.Text(init_date, size=16)
    start_text = ft.Text(init_start, size=16)
    end_text = ft.Text(init_end, size=16)
    note_f = ft.TextField(label=t("note_label"), value=init_note)

    def _make_picker_field(icon: str, label: str, value_text: ft.Text, on_tap) -> ft.Container:
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=INDIGO, size=20),
                ft.Column([
                    ft.Text(label, size=11, color=GRAY_500),
                    value_text,
                ], spacing=2, expand=True),
                ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=GRAY_500),
            ]),
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            border=ft.border.all(1, GRAY_200),
            border_radius=8,
            bgcolor="white",
            on_click=on_tap,
            ink=True,
        )

    # -- Native pickers --
    def _parse_date(s: str) -> datetime:
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except ValueError:
            return now

    date_picker = ft.DatePicker(
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2030, 12, 31),
        value=_parse_date(init_date),
    )
    start_time_picker = ft.TimePicker()
    end_time_picker = ft.TimePicker()

    def _on_date_change(e):
        _log(f"DatePicker on_change fired, value={date_picker.value}")
        if date_picker.value:
            # DatePicker returns UTC datetime; convert to local date to avoid
            # the "off-by-one-day" bug in UTC+ timezones.
            local_dt = date_picker.value.astimezone()
            date_text.value = local_dt.strftime("%Y-%m-%d")
            page.update()

    def _on_start_change(e):
        _log(f"StartTimePicker on_change fired, value={start_time_picker.value}")
        if start_time_picker.value:
            t = start_time_picker.value
            start_text.value = f"{t.hour:02d}:{t.minute:02d}"
            page.update()

    def _on_end_change(e):
        _log(f"EndTimePicker on_change fired, value={end_time_picker.value}")
        if end_time_picker.value:
            t = end_time_picker.value
            end_text.value = f"{t.hour:02d}:{t.minute:02d}"
            page.update()

    date_picker.on_change = _on_date_change
    start_time_picker.on_change = _on_start_change
    end_time_picker.on_change = _on_end_change

    # Add pickers to overlay so they can be opened
    page.overlay.extend([date_picker, start_time_picker, end_time_picker])

    def _open_picker(picker, label):
        _log(f"Opening {label}")
        try:
            picker.open = True
            page.update()
            _log(f"{label} opened OK")
        except Exception as ex:
            _log(f"{label} ERROR: {ex}")

    def _tap_date(_e):
        if date_text.value:
            try:
                date_picker.value = datetime.strptime(date_text.value, "%Y-%m-%d")
            except ValueError:
                pass
        _open_picker(date_picker, "date_picker")

    def _tap_start(_e):
        _open_picker(start_time_picker, "start_time_picker")

    def _tap_end(_e):
        _open_picker(end_time_picker, "end_time_picker")

    # -- Save / Cancel --
    def _save(_e):
        form_error.value = ""
        d = (date_text.value or "").strip()
        s = (start_text.value or "").strip()
        en = (end_text.value or "").strip()
        n = note_f.value.strip()
        try:
            if is_edit:
                api.update_leave(editing_id, d, s, en, n)
            else:
                api.create_leave(d, s, en, n)
            _nav(page, "/my-leaves")
        except HTTPStatusError as exc:
            form_error.value = exc.response.json().get("detail", "儲存失敗")
            page.update()
        except Exception:
            form_error.value = t("submit_failed")
            page.update()

    def _cancel(_e):
        _nav(page, "/my-leaves")

    title = t("edit_leave") if is_edit else t("add_leave")

    # Build tappable picker fields
    date_row = _make_picker_field(ft.Icons.CALENDAR_MONTH, t("date_label"), date_text, _tap_date)
    start_row = _make_picker_field(ft.Icons.ACCESS_TIME, t("start_time_label"), start_text, _tap_start)
    end_row = _make_picker_field(ft.Icons.ACCESS_TIME, t("end_time_label"), end_text, _tap_end)

    return ft.Column([
        ft.Row([
            ft.IconButton(ft.Icons.ARROW_BACK, on_click=_cancel),
            ft.Text(title, size=22, weight=ft.FontWeight.BOLD),
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Divider(height=1),
        ft.Container(height=8),
        date_row,
        ft.Container(height=8),
        start_row,
        ft.Container(height=8),
        end_row,
        ft.Container(height=12),
        note_f,
        form_error,
        ft.Container(height=16),
        ft.Row([
            ft.OutlinedButton(t("cancel"), on_click=_cancel),
            ft.ElevatedButton(t("save"), bgcolor=INDIGO, color="white", on_click=_save),
        ], alignment=ft.MainAxisAlignment.END),
        ft.Container(height=8),
        debug_log,
    ], scroll=ft.ScrollMode.AUTO, expand=True)


# ───────────────────────────────────────────────────────────────────────────
# CALENDAR PAGE
# ───────────────────────────────────────────────────────────────────────────

def build_calendar_page(page: ft.Page):
    now = datetime.now()
    state = {"year": now.year, "month": now.month, "day": now.day, "mode": "month"}
    title_text = ft.Text("", size=20, weight=ft.FontWeight.BOLD)
    calendar_content = ft.Column(spacing=0)

    def _title():
        y, m, d, mode = state["year"], state["month"], state["day"], state["mode"]
        lang = get_lang()
        if mode == "month":
            if lang == "en":
                return f"{MONTH_NAMES_EN[m]} {y}"
            return f"{y}年 {m}月"
        elif mode == "week":
            dt = datetime(y, m, d)
            start = dt - timedelta(days=dt.weekday())
            end = start + timedelta(days=6)
            if lang == "en":
                return f"{MONTH_NAMES_EN[m]} {y} ({start.month}/{start.day} - {end.month}/{end.day})"
            return f"{y}年 {m}月 ({start.month}/{start.day} - {end.month}/{end.day})"
        else:
            dt = datetime(y, m, d)
            if lang == "en":
                return f"{MONTH_NAMES_EN[m]} {d}, {y} ({WEEKDAYS_FULL_EN[dt.weekday()]})"
            weekdays = ["一", "二", "三", "四", "五", "六", "日"]
            return f"{y}年 {m}月 {d}日 (星期{weekdays[dt.weekday()]})"

    def _fetch_and_build():
        """Sync HTTP fetch + rebuild controls. NO page.update()."""
        title_text.value = _title()
        calendar_content.controls.clear()
        mode = state["mode"]
        try:
            if mode == "month":
                _build_month_view()
            elif mode == "week":
                _build_week_view()
            else:
                _build_day_view()
        except Exception as e:
            calendar_content.controls.append(ft.Text(f"{t('load_failed')}: {e}", color=RED))

    def _refresh():
        _fetch_and_build()
        page.update()

    def _build_month_view():
        data = api.get_calendar_month(state["year"], state["month"])
        weekday_headers = t("weekdays_sun_first").split(",")
        header_row = ft.Row(
            [ft.Container(ft.Text(w, size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=GRAY_500),
                          height=24, alignment=ft.Alignment(0, 0), expand=True)
             for w in weekday_headers],
            spacing=0,
        )
        calendar_content.controls.append(header_row)
        for week in data["grid"]:
            row_controls = []
            for cell in week:
                day_num = cell["day"]
                if day_num == 0:
                    row_controls.append(ft.Container(height=70, expand=True))
                    continue
                items: list[ft.Control] = []
                day_color = INDIGO if cell.get("is_today") else GRAY_900
                day_weight = ft.FontWeight.BOLD if cell.get("is_today") else ft.FontWeight.NORMAL
                items.append(ft.Text(str(day_num), size=13, color=day_color, weight=day_weight))
                for lv in cell.get("leaves", [])[:2]:
                    c = lv.get("color", "indigo")
                    items.append(ft.Container(
                        ft.Text(lv["display_name"], size=9, color=FLET_TEXT_COLOR_MAP.get(c, ft.Colors.BLACK)),
                        bgcolor=FLET_COLOR_MAP.get(c, ft.Colors.GREY_100),
                        border_radius=4, padding=2,
                    ))
                if len(cell.get("leaves", [])) > 2:
                    items.append(ft.Text(f"+{len(cell['leaves']) - 2}", size=9, color=GRAY_500))

                def _click_day(_e, d=day_num):
                    state["day"] = d
                    state["mode"] = "day"
                    _refresh()

                row_controls.append(ft.Container(
                    ft.Column(items, spacing=1, tight=True),
                    height=70, padding=4, expand=True,
                    border=ft.border.all(1, GRAY_200),
                    bgcolor="white" if not cell.get("is_today") else INDIGO_LIGHT,
                    on_click=_click_day,
                ))
            calendar_content.controls.append(ft.Row(row_controls, spacing=0))

    def _build_week_view():
        data = api.get_calendar_week(state["year"], state["month"], state["day"])
        weekdays_local = t("weekdays_mon_first").split(",")
        for idx, col in enumerate(data["columns"]):
            label = weekdays_local[idx] if idx < len(weekdays_local) else col["weekday_label"]
            header_bg = INDIGO_LIGHT if col.get("is_today") else GRAY_100
            items: list[ft.Control] = [
                ft.Container(
                    ft.Row([
                        ft.Text(f"{label}  {col['day_num']}", size=14, weight=ft.FontWeight.BOLD),
                    ]),
                    bgcolor=header_bg, padding=8, border_radius=6,
                ),
            ]
            if col["leaves"]:
                for lv in col["leaves"]:
                    c = lv.get("color", "indigo")
                    items.append(ft.Container(
                        ft.Column([
                            ft.Text(lv["display_name"], size=13, weight=ft.FontWeight.W_500,
                                    color=FLET_TEXT_COLOR_MAP.get(c, ft.Colors.BLACK)),
                            ft.Text(f"{lv['start_time']} - {lv['end_time']}", size=11, color=GRAY_500),
                        ], spacing=2),
                        bgcolor=FLET_COLOR_MAP.get(c, ft.Colors.GREY_100),
                        padding=8, border_radius=6, margin=ft.margin.only(bottom=4),
                    ))
            else:
                items.append(ft.Text(t("no_bookings"), size=12, color=GRAY_500, italic=True))
            calendar_content.controls.append(ft.Container(
                ft.Column(items, spacing=4), padding=8,
                border=ft.border.all(1, GRAY_200), border_radius=8,
                margin=ft.margin.only(bottom=6),
            ))

    def _build_day_view():
        data = api.get_calendar_day(state["year"], state["month"], state["day"])
        for hr in data["hours"]:
            leaves_controls: list[ft.Control] = []
            for lv in hr.get("leaves", []):
                c = lv.get("color", "indigo")
                leaves_controls.append(ft.Container(
                    ft.Column([
                        ft.Text(lv["display_name"], weight=ft.FontWeight.W_500, size=12,
                                color=FLET_TEXT_COLOR_MAP.get(c, ft.Colors.BLACK)),
                        ft.Text(f"{lv['start_time']}-{lv['end_time']}", size=10, color=GRAY_500),
                    ], spacing=1),
                    bgcolor=FLET_COLOR_MAP.get(c, ft.Colors.GREY_100),
                    padding=6, border_radius=4, margin=ft.margin.only(left=8),
                ))
            calendar_content.controls.append(ft.Container(
                ft.Row([
                    ft.Text(hr["hour_str"], size=12, color=GRAY_500, width=50),
                    ft.VerticalDivider(width=1),
                    *leaves_controls,
                ], vertical_alignment=ft.CrossAxisAlignment.START),
                height=50, border=ft.border.only(bottom=ft.BorderSide(1, GRAY_200)),
            ))

    def _prev(_e):
        y, m, d, mode = state["year"], state["month"], state["day"], state["mode"]
        if mode == "month":
            if m == 1:
                state["month"], state["year"] = 12, y - 1
            else:
                state["month"] = m - 1
        else:
            dt = datetime(y, m, d)
            delta = timedelta(days=7) if mode == "week" else timedelta(days=1)
            ndt = dt - delta
            state["year"], state["month"], state["day"] = ndt.year, ndt.month, ndt.day
        _refresh()

    def _next(_e):
        y, m, d, mode = state["year"], state["month"], state["day"], state["mode"]
        if mode == "month":
            if m == 12:
                state["month"], state["year"] = 1, y + 1
            else:
                state["month"] = m + 1
        else:
            dt = datetime(y, m, d)
            delta = timedelta(days=7) if mode == "week" else timedelta(days=1)
            ndt = dt + delta
            state["year"], state["month"], state["day"] = ndt.year, ndt.month, ndt.day
        _refresh()

    def _today(_e):
        now2 = datetime.now()
        state["year"], state["month"], state["day"] = now2.year, now2.month, now2.day
        _refresh()

    def _set_mode(mode: str):
        def handler(_e):
            state["mode"] = mode
            _refresh()
        return handler

    def _manual_refresh(_e):
        _refresh()

    nav_row1 = ft.Row([
        ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=_prev),
        title_text,
        ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=_next),
        ft.Container(expand=True),
        ft.IconButton(ft.Icons.REFRESH, icon_color=INDIGO, tooltip=t("refresh"), on_click=_manual_refresh),
        ft.OutlinedButton(t("today"), on_click=_today),
    ])
    nav_row2 = ft.Row([
        ft.TextButton(t("month_btn"), on_click=_set_mode("month")),
        ft.TextButton(t("week_btn"), on_click=_set_mode("week")),
        ft.TextButton(t("day_btn"), on_click=_set_mode("day")),
    ])

    _page_refresh_fn[0] = _fetch_and_build  # poll calls this in worker thread
    _refresh()

    return ft.Column([nav_row1, nav_row2, ft.Divider(height=1), calendar_content],
                     scroll=ft.ScrollMode.AUTO, expand=True)


# ───────────────────────────────────────────────────────────────────────────
# ADMIN LOGIN PAGE
# ───────────────────────────────────────────────────────────────────────────

def build_admin_login_page(page: ft.Page):
    error_text = ft.Text("", color=RED, size=13)
    usr = ft.TextField(label=t("admin_username_label"), width=320)
    pwd = ft.TextField(label=t("admin_password_label"), width=320, password=True, can_reveal_password=True)

    def do_login(_e):
        error_text.value = ""
        try:
            api.admin_login(usr.value.strip(), pwd.value)
            _nav(page, "/admin")
        except HTTPStatusError as exc:
            error_text.value = exc.response.json().get("detail", t("login_failed"))
            page.update()
        except Exception:
            error_text.value = t("login_failed")
            page.update()

    def go_back(_e):
        _nav(page, "/login")

    return ft.Column(
        [
            ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=48, color=INDIGO),
            ft.Text(t("admin_login_title"), size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            usr, pwd, error_text,
            ft.ElevatedButton(t("admin_login_btn"), bgcolor=INDIGO, color="white", width=320, on_click=do_login),
            ft.Container(height=8),
            ft.TextButton(t("back_to_user_login"), on_click=go_back),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
    )


# ───────────────────────────────────────────────────────────────────────────
# ADMIN DASHBOARD
# ───────────────────────────────────────────────────────────────────────────

def build_admin_page(page: ft.Page):
    if not api.is_admin:
        _navigate(page, "/admin-login")
        return ft.Container()

    users_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    messages_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    form_error = ft.Text("", color=RED, size=13)
    usr_f = ft.TextField(label=t("username"), width=300)
    pwd_f = ft.TextField(label=t("password"), width=300)
    dn_f = ft.TextField(label=t("display_name"), width=300)
    form_title = ft.Text(t("add_user"), size=18, weight=ft.FontWeight.BOLD)
    editing_uid: list[int | None] = [None]

    dlg = ft.AlertDialog(modal=True, title=form_title)

    def _fetch_and_build_users():
        """Sync HTTP fetch + rebuild user controls. NO page.update().

        Safe to call from a worker thread via asyncio.to_thread().
        """
        users_list.controls.clear()
        try:
            users = api.admin_list_users()
        except Exception:
            users = []
        for u in users:
            def edit(_e, uid=u["id"]):
                _open_edit_user(uid)

            def delete(_e, uid=u["id"]):
                try:
                    api.admin_delete_user(uid)
                except HTTPStatusError as exc:
                    page.snack_bar = ft.SnackBar(ft.Text(exc.response.json().get("detail", t("delete_failed"))))
                    page.snack_bar.open = True
                _refresh_users()

            users_list.controls.append(ft.Container(
                ft.Row([
                    ft.Column([
                        ft.Text(u["display_name"], weight=ft.FontWeight.BOLD),
                        ft.Text(f"@{u['username']}", size=12, color=GRAY_500),
                    ], expand=True),
                    ft.IconButton(ft.Icons.EDIT, icon_color=GRAY_500, on_click=edit),
                    ft.IconButton(ft.Icons.DELETE, icon_color=RED, on_click=delete),
                ]),
                padding=10, border=ft.border.all(1, GRAY_100), border_radius=8,
                bgcolor="white", margin=ft.margin.only(bottom=6),
            ))

    def _refresh_users():
        _fetch_and_build_users()
        page.update()

    def _fetch_and_build_messages():
        """Sync HTTP fetch + rebuild message controls. NO page.update().

        Safe to call from a worker thread via asyncio.to_thread().
        """
        messages_list.controls.clear()
        try:
            msgs = api.list_messages()
        except Exception:
            msgs = []
        for m in msgs:
            def delete_msg(_e, mid=m["id"]):
                try:
                    api.delete_message(mid)
                except Exception:
                    pass
                _refresh_messages()

            messages_list.controls.append(ft.Container(
                ft.Column([
                    ft.Row([
                        ft.Text(m["name"], weight=ft.FontWeight.BOLD),
                        ft.Text(f"({m['employee_id']})", size=12, color=GRAY_500),
                        ft.Container(expand=True),
                        ft.Text(m["submitted_at"], size=11, color=GRAY_500),
                        ft.IconButton(ft.Icons.DELETE, icon_color=RED, icon_size=16, on_click=delete_msg),
                    ]),
                    ft.Text(f"Email: {m['email']}  |  {m['contact_method']}: {m['contact_value']}", size=12, color=GRAY_500),
                    ft.Text(m["message"], size=13),
                ]),
                padding=10, border=ft.border.all(1, GRAY_100), border_radius=8,
                bgcolor="white", margin=ft.margin.only(bottom=6),
            ))

    def _refresh_messages():
        _fetch_and_build_messages()
        page.update()

    def _open_add_user(_e):
        editing_uid[0] = None
        form_title.value = t("add_user")
        usr_f.value = pwd_f.value = dn_f.value = ""
        form_error.value = ""
        dlg.open = True
        page.update()

    def _open_edit_user(uid: int):
        try:
            users = api.admin_list_users()
            u = next((x for x in users if x["id"] == uid), None)
        except Exception:
            return
        if not u:
            return
        editing_uid[0] = uid
        form_title.value = t("edit_user")
        usr_f.value = u["username"]
        pwd_f.value = ""
        dn_f.value = u["display_name"]
        form_error.value = ""
        dlg.open = True
        page.update()

    def _save_user(_e):
        form_error.value = ""
        try:
            if editing_uid[0] is None:
                api.admin_create_user(usr_f.value.strip(), pwd_f.value, dn_f.value.strip())
            else:
                api.admin_update_user(editing_uid[0], usr_f.value.strip(), pwd_f.value, dn_f.value.strip())
            dlg.open = False
            _refresh_users()
        except HTTPStatusError as exc:
            form_error.value = exc.response.json().get("detail", t("save_failed"))
            page.update()

    def _cancel_user(_e):
        dlg.open = False
        page.update()

    dlg.content = ft.Column([usr_f, pwd_f, dn_f, form_error], tight=True, width=340)
    dlg.actions = [
        ft.TextButton(t("cancel"), on_click=_cancel_user),
        ft.ElevatedButton(t("save"), bgcolor=INDIGO, color="white", on_click=_save_user),
    ]
    page.overlay.append(dlg)

    # -- Tab content panels --
    users_panel = ft.Column([
        ft.Row([
            ft.Text(t("user_list"), size=18, weight=ft.FontWeight.BOLD, expand=True),
            ft.ElevatedButton(t("add_user"), icon=ft.Icons.ADD, bgcolor=INDIGO, color="white", on_click=_open_add_user),
        ]),
        users_list,
    ], expand=True)

    messages_panel = ft.Column([
        ft.Text(t("message_list"), size=18, weight=ft.FontWeight.BOLD),
        messages_list,
    ], expand=True)

    tab_content = ft.Container(content=users_panel, expand=True)
    _active_tab: list[int] = [0]

    def _tab_btn(label: str, idx: int):
        is_active = _active_tab[0] == idx
        return ft.TextButton(
            label,
            style=ft.ButtonStyle(
                color=INDIGO if is_active else GRAY_500,
                bgcolor=INDIGO_LIGHT if is_active else None,
            ),
            on_click=lambda _e: _switch_tab(idx),
        )

    def _switch_tab(idx: int):
        _active_tab[0] = idx
        if idx == 0:
            tab_content.content = users_panel
            _refresh_users()
        else:
            tab_content.content = messages_panel
            _refresh_messages()
        _rebuild_tab_bar()
        page.update()

    tab_bar = ft.Row(spacing=0)

    def _rebuild_tab_bar():
        tab_bar.controls = [
            _tab_btn(t("user_management"), 0),
            _tab_btn(t("message_management"), 1),
        ]

    _rebuild_tab_bar()

    def admin_logout(_e):
        api.is_admin = False
        _nav(page, "/login")

    def _admin_refresh():
        """Sync data fetch + rebuild controls. NO page.update().

        Called by the polling loop via asyncio.to_thread() on a worker
        thread. The polling loop handles page.update() on the UI thread
        after this returns.
        """
        if _active_tab[0] == 0:
            _fetch_and_build_users()
        else:
            _fetch_and_build_messages()

    _page_refresh_fn[0] = _admin_refresh
    _refresh_users()
    _refresh_messages()

    return ft.Column([
        ft.Row([
            ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, color=INDIGO),
            ft.Text(t("admin_dashboard_title"), size=22, weight=ft.FontWeight.BOLD, expand=True),
            ft.OutlinedButton(t("admin_logout"), on_click=admin_logout),
        ]),
        ft.Divider(height=1),
        tab_bar,
        tab_content,
    ], expand=True)


# ───────────────────────────────────────────────────────────────────────────
# NAVBAR (for logged-in pages)
# ───────────────────────────────────────────────────────────────────────────

def _navbar(page: ft.Page, active: str) -> ft.Container:
    def nav_btn(label: str, route: str):
        is_active = active == route
        return ft.TextButton(
            label,
            style=ft.ButtonStyle(
                color=INDIGO if is_active else GRAY_500,
            ),
            on_click=lambda _e: _nav(page, route),
        )

    def logout(_e):
        api.logout()
        _nav(page, "/login")

    return ft.Container(
        ft.Column([
            # Row 1: logo + greeting + logout
            ft.Row([
                ft.Icon(ft.Icons.CALENDAR_MONTH, color=INDIGO, size=20),
                ft.Text(t("app_title"), weight=ft.FontWeight.BOLD, size=14),
                ft.Container(expand=True),
                ft.Text(f"{api.display_name}", size=12, color=GRAY_700),
                ft.TextButton(t("logout"), on_click=logout,
                              style=ft.ButtonStyle(color=GRAY_500, padding=0)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            # Row 2: nav tabs
            ft.Row([
                nav_btn(t("my_leaves_nav"), "/my-leaves"),
                nav_btn(t("calendar_nav"), "/calendar"),
            ]),
        ], spacing=0),
        padding=ft.padding.symmetric(horizontal=12, vertical=4),
        bgcolor="white",
        border=ft.border.only(bottom=ft.BorderSide(1, GRAY_200)),
    )


# ───────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ───────────────────────────────────────────────────────────────────────────

def main(page: ft.Page):
    page.title = t("app_title")
    page.bgcolor = GRAY_50
    page.padding = 0
    # On Android emulator the default 10.0.2.2 is correct.
    # On iOS simulator or desktop, use 127.0.0.1.
    if page.platform in (ft.PagePlatform.IOS, ft.PagePlatform.MACOS):
        if "10.0.2.2" in api.base:
            api.reconfigure("http://127.0.0.1:8000")
    _start_polling(page)
    _navigate(page, "/login")


ft.app(target=main)
