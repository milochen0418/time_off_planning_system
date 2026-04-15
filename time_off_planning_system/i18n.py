"""
Internationalization (i18n) module for the Time-Off Planning System.
Supports English (en) and Traditional Chinese (zh).
"""

from __future__ import annotations

import reflex as rx

TRANSLATIONS: dict[str, dict[str, str]] = {
    # ── Common ─────────────────────────────────────────────────────────────
    "app_title": {"zh": "預約休假管理系統", "en": "Time-Off Planning System"},
    "cancel": {"zh": "取消", "en": "Cancel"},
    "save": {"zh": "儲存", "en": "Save"},
    "logout": {"zh": "登出", "en": "Logout"},
    "language": {"zh": "語言", "en": "Language"},

    # ── Login page ─────────────────────────────────────────────────────────
    "login_subtitle": {"zh": "登入您的帳號", "en": "Sign in to your account"},
    "username_label": {"zh": "帳號 (Username)", "en": "Username"},
    "password_label": {"zh": "密碼 (Password)", "en": "Password"},
    "username_placeholder": {"zh": "請輸入帳號", "en": "Enter username"},
    "password_placeholder": {"zh": "請輸入密碼", "en": "Enter password"},
    "login_btn": {"zh": "登入系統", "en": "Sign In"},
    "no_account": {"zh": "尚未擁有帳號？", "en": "Don't have an account?"},
    "contact_admin_link": {"zh": "留言給超級管理者", "en": "Contact Admin"},
    "admin_login_link": {"zh": "超級管理者登入", "en": "Admin Login"},

    # ── Register page ──────────────────────────────────────────────────────
    "create_account": {"zh": "建立新帳號", "en": "Create Account"},
    "display_name_label": {"zh": "顯示名稱 (Display Name)", "en": "Display Name"},
    "display_name_placeholder": {"zh": "例如：小明", "en": "e.g. John"},
    "reg_username_label": {"zh": "登入帳號 (Username)", "en": "Login Username"},
    "reg_username_placeholder": {"zh": "例如：xiaoming123", "en": "e.g. john123"},
    "confirm_password_label": {"zh": "確認密碼 (Confirm Password)", "en": "Confirm Password"},
    "register_btn": {"zh": "立即註冊", "en": "Register Now"},
    "system_issue": {"zh": "系統問題或權限申請？", "en": "System issues or need access?"},

    # ── My Leaves page ─────────────────────────────────────────────────────
    "my_leaves_title": {"zh": "我的休假清單", "en": "My Leaves"},
    "my_leaves_subtitle": {"zh": "管理您的個人預約記錄。", "en": "Manage your personal leave records."},
    "add_leave": {"zh": "新增休假", "en": "Add Leave"},
    "edit_leave": {"zh": "編輯休假", "en": "Edit Leave"},
    "no_leaves": {"zh": "尚未有任何休假記錄", "en": "No leave records yet"},
    "no_leaves_hint": {"zh": "點擊上方按鈕來新增您的第一筆預約。", "en": "Click the button above to add your first booking."},
    "date_label": {"zh": "日期", "en": "Date"},
    "start_time_label": {"zh": "開始時間", "en": "Start Time"},
    "end_time_label": {"zh": "結束時間", "en": "End Time"},
    "note_label": {"zh": "備註 (選填)", "en": "Note (optional)"},
    "note_placeholder": {"zh": "例如：去醫院掛號", "en": "e.g. Doctor's appointment"},

    # ── Admin login page ───────────────────────────────────────────────────
    "admin_login_title": {"zh": "超級管理者登入", "en": "Admin Login"},
    "admin_panel_subtitle": {"zh": "後台管理系統", "en": "Admin Panel"},
    "admin_username_label": {"zh": "管理員帳號", "en": "Admin Username"},
    "admin_password_label": {"zh": "管理員密碼", "en": "Admin Password"},
    "admin_login_btn": {"zh": "登入後台", "en": "Sign In"},
    "back_to_user_login": {"zh": "返回一般使用者登入", "en": "Back to User Login"},

    # ── Admin dashboard ────────────────────────────────────────────────────
    "admin_dashboard_title": {"zh": "超級管理者後台", "en": "Admin Dashboard"},
    "admin_logout": {"zh": "登出後台", "en": "Logout"},
    "user_management": {"zh": "使用者管理", "en": "User Management"},
    "message_management": {"zh": "留言板管理", "en": "Message Board"},
    "add_user": {"zh": "新增使用者", "en": "Add User"},
    "edit_user": {"zh": "編輯使用者", "en": "Edit User"},
    "display_name": {"zh": "顯示名稱", "en": "Display Name"},
    "username": {"zh": "帳號", "en": "Username"},
    "password": {"zh": "密碼", "en": "Password"},
    "actions": {"zh": "操作", "en": "Actions"},
    "no_messages": {"zh": "尚無任何留言", "en": "No messages yet"},

    # ── Contact page ───────────────────────────────────────────────────────
    "contact_admin_title": {"zh": "留言給超級管理者", "en": "Contact Admin"},
    "contact_subtitle": {
        "zh": "若您忘記密碼或需要開通權限，請填寫下方表單。",
        "en": "If you forgot your password or need access, please fill out the form below.",
    },
    "employee_id_label": {"zh": "員工編號 (Employee ID)", "en": "Employee ID"},
    "name_label": {"zh": "姓名 (Name)", "en": "Name"},
    "email_label": {"zh": "信箱 (Email)", "en": "Email"},
    "contact_method_label": {"zh": "通訊方式", "en": "Contact Method"},
    "contact_value_label": {"zh": "帳號/號碼", "en": "Account / Number"},
    "message_content_label": {"zh": "留言內容", "en": "Message"},
    "submit_message": {"zh": "送出留言", "en": "Submit Message"},
    "back_to_login": {"zh": "返回登入頁面", "en": "Back to Login"},
    "enter_line_id": {"zh": "請輸入 Line ID", "en": "Enter Line ID"},
    "enter_phone": {"zh": "請輸入電話號碼", "en": "Enter phone number"},
    "enter_contact": {"zh": "請輸入聯絡方式", "en": "Enter contact info"},

    # ── Calendar page ──────────────────────────────────────────────────────
    "today": {"zh": "今天", "en": "Today"},
    "month_view": {"zh": "月", "en": "Month"},
    "week_view": {"zh": "週", "en": "Week"},
    "day_view": {"zh": "日", "en": "Day"},

    # ── Navbar ─────────────────────────────────────────────────────────────
    "my_leaves_nav": {"zh": "我的休假", "en": "My Leaves"},
    "calendar_nav": {"zh": "共用日曆", "en": "Shared Calendar"},
    "greeting_prefix": {"zh": "你好, ", "en": "Hello, "},

    # ── State error / success messages ─────────────────────────────────────
    "invalid_credentials": {"zh": "帳號或密碼錯誤", "en": "Invalid username or password"},
    "fill_all_fields": {"zh": "請填寫所有欄位", "en": "Please fill in all fields"},
    "password_mismatch": {"zh": "密碼不一致", "en": "Passwords do not match"},
    "username_taken": {"zh": "此帳號已被註冊", "en": "This username is already registered"},
    "register_success": {"zh": "註冊成功！請前往登入", "en": "Registration successful! Please log in"},
    "fill_required_fields": {"zh": "請填寫所有必要欄位", "en": "Please fill in all required fields"},
    "start_before_end": {"zh": "開始時間必須早於結束時間", "en": "Start time must be before end time"},
    "conflict_prefix": {"zh": "與現有預約衝突", "en": "Conflicts with existing booking"},
    "leave_added": {"zh": "成功新增休假", "en": "Leave added successfully"},
    "leave_updated": {"zh": "成功更新休假", "en": "Leave updated successfully"},
    "leave_deleted": {"zh": "已刪除休假記錄", "en": "Leave record deleted"},
    "message_sent": {"zh": "留言已送出，管理者將盡快與您聯繫！", "en": "Message sent! Admin will contact you soon."},
    "message_deleted": {"zh": "留言已刪除", "en": "Message deleted"},
    "invalid_admin_credentials": {"zh": "管理者帳號或密碼錯誤", "en": "Invalid admin credentials"},
    "username_in_use": {"zh": "此帳號已被使用", "en": "This username is already in use"},
    "user_added_prefix": {"zh": "成功新增使用者: ", "en": "User added: "},
    "user_updated": {"zh": "成功更新使用者資料", "en": "User information updated"},
    "cannot_delete_admin": {"zh": "不能刪除預設管理員帳號", "en": "Cannot delete the default admin account"},
    "user_deleted": {"zh": "使用者已刪除", "en": "User deleted"},

    # ── Calendar display ───────────────────────────────────────────────────
    "weekdays_short": {"zh": "日,一,二,三,四,五,六", "en": "Sun,Mon,Tue,Wed,Thu,Fri,Sat"},
    "weekdays_mon_first": {"zh": "一,二,三,四,五,六,日", "en": "Mon,Tue,Wed,Thu,Fri,Sat,Sun"},
    "weekday_prefix": {"zh": "星期", "en": ""},
}

# Month names for English calendar display
MONTH_NAMES_EN = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

WEEKDAYS_FULL_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAYS_FULL_ZH = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


def get_text(lang: str, key: str) -> str:
    """Return plain-text translation for the given language and key."""
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang, entry.get("zh", key))


def t(key: str) -> rx.Var:
    """Return an rx.cond Var that switches between English and Chinese text.

    Usage in Reflex UI:  rx.el.h2(t("app_title"))
    """
    from time_off_planning_system.states.lang_state import LangState

    entry = TRANSLATIONS.get(key)
    if not entry:
        return rx.Var.create(key)
    return rx.cond(LangState.lang == "en", entry.get("en", key), entry.get("zh", key))
