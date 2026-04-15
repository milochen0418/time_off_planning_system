"""
Internationalization (i18n) module for the Flet app.
Supports English (en) and Traditional Chinese (zh).
"""

from __future__ import annotations

# Module-level language state (shared across the single Flet app process)
_current_lang: list[str] = ["zh"]

TRANSLATIONS: dict[str, dict[str, str]] = {
    # ── Common ─────────────────────────────────────────────────────────────
    "app_title": {"zh": "預約休假管理系統", "en": "Time-Off Planning System"},
    "cancel": {"zh": "取消", "en": "Cancel"},
    "save": {"zh": "儲存", "en": "Save"},
    "logout": {"zh": "登出", "en": "Logout"},
    "language": {"zh": "語言", "en": "Language"},
    "refresh": {"zh": "重新整理", "en": "Refresh"},

    # ── Login page ─────────────────────────────────────────────────────────
    "login_subtitle": {"zh": "登入您的帳號", "en": "Sign in to your account"},
    "username_label": {"zh": "帳號 (Username)", "en": "Username"},
    "password_label": {"zh": "密碼 (Password)", "en": "Password"},
    "login_btn": {"zh": "登入系統", "en": "Sign In"},
    "no_account": {"zh": "尚未擁有帳號？", "en": "Don't have an account?"},
    "contact_admin_link": {"zh": "留言給超級管理者", "en": "Contact Admin"},
    "admin_login_link": {"zh": "超級管理者登入", "en": "Admin Login"},
    "login_failed": {"zh": "登入失敗", "en": "Login failed"},

    # ── Contact page ───────────────────────────────────────────────────────
    "contact_admin_title": {"zh": "聯絡超級管理者", "en": "Contact Admin"},
    "employee_id_label": {"zh": "員工編號", "en": "Employee ID"},
    "name_label": {"zh": "姓名", "en": "Name"},
    "email_label": {"zh": "Email", "en": "Email"},
    "contact_method_label": {"zh": "聯絡方式", "en": "Contact Method"},
    "contact_value_label": {"zh": "聯絡資訊", "en": "Contact Info"},
    "message_content_label": {"zh": "留言內容", "en": "Message"},
    "submit_message": {"zh": "送出留言", "en": "Submit Message"},
    "message_sent": {"zh": "留言已送出，管理者將盡快與您聯繫！", "en": "Message sent! Admin will contact you soon."},
    "submit_failed": {"zh": "送出失敗", "en": "Submission failed"},

    # ── My Leaves page ─────────────────────────────────────────────────────
    "my_leaves_title": {"zh": "我的休假清單", "en": "My Leaves"},
    "my_leaves_subtitle": {"zh": "管理您的個人預約記錄。", "en": "Manage your personal leave records."},
    "add_leave": {"zh": "新增休假", "en": "Add Leave"},
    "edit_leave": {"zh": "編輯休假", "en": "Edit Leave"},
    "no_leaves": {"zh": "尚未有任何休假記錄", "en": "No leave records yet"},
    "no_leaves_hint": {"zh": "點擊上方按鈕來新增您的第一筆預約。", "en": "Click the button above to add your first booking."},
    "note_label": {"zh": "備註 (選填)", "en": "Note (optional)"},
    "date_label": {"zh": "日期", "en": "Date"},
    "start_time_label": {"zh": "開始時間", "en": "Start Time"},
    "end_time_label": {"zh": "結束時間", "en": "End Time"},
    "save_failed": {"zh": "儲存失敗", "en": "Save failed"},

    # ── Calendar ───────────────────────────────────────────────────────────
    "today": {"zh": "今天", "en": "Today"},
    "month_btn": {"zh": "月", "en": "Month"},
    "week_btn": {"zh": "週", "en": "Week"},
    "day_btn": {"zh": "日", "en": "Day"},
    "load_failed": {"zh": "載入失敗", "en": "Load failed"},
    "no_bookings": {"zh": "無預約", "en": "No bookings"},

    # ── Navbar ─────────────────────────────────────────────────────────────
    "my_leaves_nav": {"zh": "我的休假", "en": "My Leaves"},
    "calendar_nav": {"zh": "共用日曆", "en": "Shared Calendar"},

    # ── Admin ──────────────────────────────────────────────────────────────
    "admin_login_title": {"zh": "超級管理者登入", "en": "Admin Login"},
    "admin_username_label": {"zh": "管理者帳號", "en": "Admin Username"},
    "admin_password_label": {"zh": "管理者密碼", "en": "Admin Password"},
    "admin_login_btn": {"zh": "管理者登入", "en": "Admin Login"},
    "back_to_user_login": {"zh": "返回使用者登入", "en": "Back to User Login"},
    "admin_dashboard_title": {"zh": "超級管理者後台", "en": "Admin Dashboard"},
    "admin_logout": {"zh": "登出管理", "en": "Logout Admin"},
    "user_management": {"zh": "使用者管理", "en": "User Management"},
    "message_management": {"zh": "留言管理", "en": "Message Board"},
    "user_list": {"zh": "使用者列表", "en": "User List"},
    "message_list": {"zh": "留言列表", "en": "Message List"},
    "add_user": {"zh": "新增使用者", "en": "Add User"},
    "edit_user": {"zh": "編輯使用者", "en": "Edit User"},
    "username": {"zh": "帳號", "en": "Username"},
    "password": {"zh": "密碼", "en": "Password"},
    "display_name": {"zh": "顯示名稱", "en": "Display Name"},
    "delete_failed": {"zh": "刪除失敗", "en": "Delete failed"},

    # ── Calendar display ───────────────────────────────────────────────────
    "weekdays_sun_first": {"zh": "日,一,二,三,四,五,六", "en": "Sun,Mon,Tue,Wed,Thu,Fri,Sat"},
    "weekdays_mon_first": {"zh": "一,二,三,四,五,六,日", "en": "Mon,Tue,Wed,Thu,Fri,Sat,Sun"},
}

MONTH_NAMES_EN = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

WEEKDAYS_FULL_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_lang() -> str:
    return _current_lang[0]


def set_lang(lang: str) -> None:
    _current_lang[0] = lang


def t(key: str) -> str:
    """Return the translated text for the current language."""
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(_current_lang[0], entry.get("zh", key))
