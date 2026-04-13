"""
Time-Off Planning System — Flet Desktop / Mobile Client
========================================================
Uses page.controls (page.add / page.clean) instead of page.views + page.go()
because the Views-based routing does not render on Flet mobile (APK).
"""

from __future__ import annotations

import calendar as _calendar
import traceback
from datetime import datetime, timedelta

import flet as ft
from httpx import HTTPStatusError

from api_client import ApiClient

api = ApiClient()

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


# ── Helper: navigate by clearing page controls ────────────────────────────
def _navigate(page: ft.Page, route: str):
    """Clear controls and rebuild the page for the given route."""
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
    username_field = ft.TextField(label="帳號 (Username)", width=320)
    password_field = ft.TextField(label="密碼 (Password)", password=True, can_reveal_password=True, width=320)

    def do_login(_e):
        error_text.value = ""
        try:
            api.login(username_field.value.strip(), password_field.value)
            _navigate(page, "/my-leaves")
        except HTTPStatusError as exc:
            detail = exc.response.json().get("detail", "登入失敗")
            error_text.value = detail
            page.update()

    def go_contact(_e):
        _navigate(page, "/contact")

    def go_admin_login(_e):
        _navigate(page, "/admin-login")

    return ft.Column(
        [
            ft.Icon(ft.Icons.CALENDAR_MONTH, size=48, color=INDIGO),
            ft.Text("預約休假管理系統", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("登入您的帳號", size=14, color=GRAY_500),
            ft.Container(height=10),
            username_field,
            password_field,
            error_text,
            ft.ElevatedButton("登入系統", bgcolor=INDIGO, color="white", width=320, on_click=do_login),
            ft.Container(height=8),
            ft.Row([
                ft.Text("尚未擁有帳號？", color=GRAY_500, size=13),
                ft.TextButton("留言給超級管理者", on_click=go_contact),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.TextButton("超級管理者登入", on_click=go_admin_login,
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
    emp_id = ft.TextField(label="員工編號", width=400)
    name_f = ft.TextField(label="姓名", width=400)
    email_f = ft.TextField(label="Email", width=400)
    contact_method = ft.Dropdown(
        label="聯絡方式", width=400,
        options=[ft.dropdown.Option(m) for m in ["Line", "WhatsApp", "Phone", "Other"]],
        value="Line",
    )
    contact_value = ft.TextField(label="聯絡資訊", width=400)
    message_f = ft.TextField(label="留言內容", width=400, multiline=True, min_lines=3, max_lines=6)

    def submit(_e):
        error_text.value = ""
        success_text.value = ""
        try:
            api.create_message(
                emp_id.value.strip(), name_f.value.strip(), email_f.value.strip(),
                contact_method.value, contact_value.value.strip(), message_f.value.strip(),
            )
            success_text.value = "留言已送出，管理者將盡快與您聯繫！"
            emp_id.value = name_f.value = email_f.value = contact_value.value = message_f.value = ""
        except HTTPStatusError as exc:
            error_text.value = exc.response.json().get("detail", "送出失敗")
        page.update()

    def go_back(_e):
        _navigate(page, "/login")

    return ft.Column(
        [
            ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_back),
                     ft.Text("聯絡超級管理者", size=22, weight=ft.FontWeight.BOLD)]),
            emp_id, name_f, email_f, contact_method, contact_value, message_f,
            error_text, success_text,
            ft.ElevatedButton("送出留言", bgcolor=INDIGO, color="white", width=400, on_click=submit),
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
    form_error = ft.Text("", color=RED, size=13)

    date_f = ft.TextField(label="日期 (YYYY-MM-DD)", width=300)
    start_f = ft.TextField(label="開始時間 (HH:MM)", width=140)
    end_f = ft.TextField(label="結束時間 (HH:MM)", width=140)
    note_f = ft.TextField(label="備註 (選填)", width=300)
    form_title = ft.Text("新增休假", size=18, weight=ft.FontWeight.BOLD)
    editing_id: list[int | None] = [None]

    dlg = ft.AlertDialog(modal=True, title=form_title)

    def _refresh():
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
                        ft.Text("尚未有任何休假記錄", size=16, weight=ft.FontWeight.W_500),
                        ft.Text("點擊上方按鈕來新增您的第一筆預約。", size=13, color=GRAY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40, alignment=ft.alignment.center,
                    border=ft.border.all(2, GRAY_200),
                    border_radius=12,
                ),
            )
        else:
            for lv in leaves:
                leaves_list.controls.append(_leave_card(lv))
        page.update()

    def _leave_card(lv: dict) -> ft.Container:
        def edit(_e, lid=lv["id"]):
            _open_edit(lid)

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
        editing_id[0] = None
        form_title.value = "新增休假"
        date_f.value = start_f.value = end_f.value = note_f.value = ""
        form_error.value = ""
        dlg.open = True
        page.update()

    def _open_edit(lid: int):
        try:
            leaves = api.get_my_leaves()
            lv = next((l for l in leaves if l["id"] == lid), None)
        except Exception:
            return
        if not lv:
            return
        editing_id[0] = lid
        form_title.value = "編輯休假"
        date_f.value = lv["leave_date"]
        start_f.value = lv["start_time"]
        end_f.value = lv["end_time"]
        note_f.value = lv.get("note", "")
        form_error.value = ""
        dlg.open = True
        page.update()

    def _save(_e):
        form_error.value = ""
        try:
            if editing_id[0] is None:
                api.create_leave(date_f.value.strip(), start_f.value.strip(), end_f.value.strip(), note_f.value.strip())
            else:
                api.update_leave(editing_id[0], date_f.value.strip(), start_f.value.strip(), end_f.value.strip(), note_f.value.strip())
            dlg.open = False
            _refresh()
        except HTTPStatusError as exc:
            form_error.value = exc.response.json().get("detail", "儲存失敗")
            page.update()

    def _cancel(_e):
        dlg.open = False
        page.update()

    dlg.content = ft.Column([
        date_f,
        ft.Row([start_f, end_f]),
        note_f,
        form_error,
    ], tight=True, width=340)
    dlg.actions = [
        ft.TextButton("取消", on_click=_cancel),
        ft.ElevatedButton("儲存", bgcolor=INDIGO, color="white", on_click=_save),
    ]
    page.overlay.append(dlg)

    _refresh()

    return ft.Column([
        ft.Row([
            ft.Column([
                ft.Text("我的休假清單", size=22, weight=ft.FontWeight.BOLD),
                ft.Text("管理您的個人預約記錄。", size=13, color=GRAY_500),
            ], expand=True),
            ft.ElevatedButton("新增休假", icon=ft.Icons.ADD, bgcolor=INDIGO, color="white", on_click=_open_add),
        ]),
        ft.Divider(height=1),
        leaves_list,
    ], expand=True)


# ───────────────────────────────────────────────────────────────────────────
# CALENDAR PAGE
# ───────────────────────────────────────────────────────────────────────────

def build_calendar_page(page: ft.Page):
    now = datetime.now()
    state = {"year": now.year, "month": now.month, "day": now.day, "mode": "month"}
    title_text = ft.Text("", size=20, weight=ft.FontWeight.BOLD)
    calendar_content = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def _title():
        y, m, d, mode = state["year"], state["month"], state["day"], state["mode"]
        if mode == "month":
            return f"{y}年 {m}月"
        elif mode == "week":
            dt = datetime(y, m, d)
            start = dt - timedelta(days=dt.weekday())
            end = start + timedelta(days=6)
            return f"{y}年 {m}月 ({start.month}/{start.day} - {end.month}/{end.day})"
        else:
            weekdays = ["一", "二", "三", "四", "五", "六", "日"]
            dt = datetime(y, m, d)
            return f"{y}年 {m}月 {d}日 (星期{weekdays[dt.weekday()]})"

    def _refresh():
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
            calendar_content.controls.append(ft.Text(f"載入失敗: {e}", color=RED))
        page.update()

    def _build_month_view():
        data = api.get_calendar_month(state["year"], state["month"])
        weekday_headers = ["日", "一", "二", "三", "四", "五", "六"]
        header_row = ft.Row(
            [ft.Container(ft.Text(w, size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=GRAY_500),
                          width=80, alignment=ft.alignment.center)
             for w in weekday_headers],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        calendar_content.controls.append(header_row)
        for week in data["grid"]:
            row_controls = []
            for cell in week:
                day_num = cell["day"]
                if day_num == 0:
                    row_controls.append(ft.Container(width=80, height=70))
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
                    width=80, height=70, padding=4,
                    border=ft.border.all(1, GRAY_200),
                    bgcolor="white" if not cell.get("is_today") else INDIGO_LIGHT,
                    on_click=_click_day,
                ))
            calendar_content.controls.append(ft.Row(row_controls, alignment=ft.MainAxisAlignment.CENTER))

    def _build_week_view():
        data = api.get_calendar_week(state["year"], state["month"], state["day"])
        for col in data["columns"]:
            header_bg = INDIGO_LIGHT if col.get("is_today") else GRAY_100
            items: list[ft.Control] = [
                ft.Container(
                    ft.Row([
                        ft.Text(f"{col['weekday_label']}  {col['day_num']}", size=14, weight=ft.FontWeight.BOLD),
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
                items.append(ft.Text("無預約", size=12, color=GRAY_500, italic=True))
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

    mode_selector = ft.Row([
        ft.TextButton("月", on_click=_set_mode("month")),
        ft.TextButton("週", on_click=_set_mode("week")),
        ft.TextButton("日", on_click=_set_mode("day")),
    ])

    nav_row = ft.Row([
        ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=_prev),
        title_text,
        ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=_next),
        ft.Container(width=16),
        ft.OutlinedButton("今天", on_click=_today),
        ft.Container(expand=True),
        mode_selector,
    ])

    _refresh()

    return ft.Column([nav_row, ft.Divider(height=1), calendar_content], expand=True)


# ───────────────────────────────────────────────────────────────────────────
# ADMIN LOGIN PAGE
# ───────────────────────────────────────────────────────────────────────────

def build_admin_login_page(page: ft.Page):
    error_text = ft.Text("", color=RED, size=13)
    usr = ft.TextField(label="管理者帳號", width=320)
    pwd = ft.TextField(label="管理者密碼", width=320, password=True, can_reveal_password=True)

    def do_login(_e):
        error_text.value = ""
        try:
            api.admin_login(usr.value.strip(), pwd.value)
            _navigate(page, "/admin")
        except HTTPStatusError as exc:
            error_text.value = exc.response.json().get("detail", "登入失敗")
            page.update()

    def go_back(_e):
        _navigate(page, "/login")

    return ft.Column(
        [
            ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=48, color=INDIGO),
            ft.Text("超級管理者登入", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            usr, pwd, error_text,
            ft.ElevatedButton("管理者登入", bgcolor=INDIGO, color="white", width=320, on_click=do_login),
            ft.Container(height=8),
            ft.TextButton("返回使用者登入", on_click=go_back),
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
    usr_f = ft.TextField(label="帳號", width=300)
    pwd_f = ft.TextField(label="密碼", width=300)
    dn_f = ft.TextField(label="顯示名稱", width=300)
    form_title = ft.Text("新增使用者", size=18, weight=ft.FontWeight.BOLD)
    editing_uid: list[int | None] = [None]

    dlg = ft.AlertDialog(modal=True, title=form_title)

    def _refresh_users():
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
                    page.snack_bar = ft.SnackBar(ft.Text(exc.response.json().get("detail", "刪除失敗")))
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
        page.update()

    def _refresh_messages():
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
        page.update()

    def _open_add_user(_e):
        editing_uid[0] = None
        form_title.value = "新增使用者"
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
        form_title.value = "編輯使用者"
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
            form_error.value = exc.response.json().get("detail", "儲存失敗")
            page.update()

    def _cancel_user(_e):
        dlg.open = False
        page.update()

    dlg.content = ft.Column([usr_f, pwd_f, dn_f, form_error], tight=True, width=340)
    dlg.actions = [
        ft.TextButton("取消", on_click=_cancel_user),
        ft.ElevatedButton("儲存", bgcolor=INDIGO, color="white", on_click=_save_user),
    ]
    page.overlay.append(dlg)

    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="使用者管理", content=ft.Column([
                ft.Row([
                    ft.Text("使用者列表", size=18, weight=ft.FontWeight.BOLD, expand=True),
                    ft.ElevatedButton("新增使用者", icon=ft.Icons.ADD, bgcolor=INDIGO, color="white", on_click=_open_add_user),
                ]),
                users_list,
            ], expand=True)),
            ft.Tab(text="留言管理", content=ft.Column([
                ft.Text("留言列表", size=18, weight=ft.FontWeight.BOLD),
                messages_list,
            ], expand=True)),
        ],
        expand=True,
    )

    def on_tab_change(_e):
        if tabs.selected_index == 0:
            _refresh_users()
        else:
            _refresh_messages()

    tabs.on_change = on_tab_change

    def admin_logout(_e):
        api.is_admin = False
        _navigate(page, "/login")

    _refresh_users()
    _refresh_messages()

    return ft.Column([
        ft.Row([
            ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, color=INDIGO),
            ft.Text("超級管理者後台", size=22, weight=ft.FontWeight.BOLD, expand=True),
            ft.OutlinedButton("登出管理", on_click=admin_logout),
        ]),
        ft.Divider(height=1),
        tabs,
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
            on_click=lambda _e: _navigate(page, route),
        )

    def logout(_e):
        api.logout()
        _navigate(page, "/login")

    return ft.Container(
        ft.Column([
            # Row 1: logo + greeting + logout
            ft.Row([
                ft.Icon(ft.Icons.CALENDAR_MONTH, color=INDIGO, size=20),
                ft.Text("預約休假管理系統", weight=ft.FontWeight.BOLD, size=14),
                ft.Container(expand=True),
                ft.Text(f"{api.display_name}", size=12, color=GRAY_700),
                ft.TextButton("登出", on_click=logout,
                              style=ft.ButtonStyle(color=GRAY_500, padding=0)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            # Row 2: nav tabs
            ft.Row([
                nav_btn("我的休假", "/my-leaves"),
                nav_btn("共用日曆", "/calendar"),
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
    page.title = "預約休假管理系統"
    page.bgcolor = GRAY_50
    page.padding = 0
    _navigate(page, "/login")


ft.app(target=main)
