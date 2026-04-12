import reflex as rx
from time_off_planning_system.states.auth_state import AuthState
from time_off_planning_system.states.leave_state import LeaveState, Leave
from time_off_planning_system.components.layout import protected_layout


def index() -> rx.Component:
    return rx.el.div(
        on_mount=rx.cond(
            AuthState.logged_in, rx.redirect("/my-leaves"), rx.redirect("/login")
        )
    )


def login_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(
                    "calendar-days", class_name="mx-auto h-12 w-auto text-indigo-600"
                ),
                rx.el.h2(
                    "預約休假管理系統",
                    class_name="mt-6 text-center text-3xl font-extrabold tracking-tight text-gray-900",
                ),
                rx.el.p(
                    "登入您的帳號", class_name="mt-2 text-center text-sm text-gray-600"
                ),
                class_name="sm:mx-auto sm:w-full sm:max-w-md",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "帳號 (Username)",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            placeholder="請輸入帳號",
                            on_change=AuthState.set_login_username,
                            class_name="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "密碼 (Password)",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            type="password",
                            placeholder="請輸入密碼",
                            on_change=AuthState.set_login_password,
                            class_name="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
                        ),
                        class_name="mb-6",
                    ),
                    rx.cond(
                        AuthState.login_error != "",
                        rx.el.p(
                            AuthState.login_error,
                            class_name="mb-4 text-sm text-red-600 font-medium",
                        ),
                    ),
                    rx.el.button(
                        "登入系統",
                        on_click=AuthState.login,
                        class_name="flex w-full justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all",
                    ),
                    rx.el.div(
                        rx.el.span("尚未擁有帳號？", class_name="text-gray-500"),
                        rx.el.a(
                            "留言給超級管理者",
                            href="/contact",
                            class_name="ml-1 font-medium text-indigo-600 hover:text-indigo-500",
                        ),
                        class_name="mt-6 text-center text-sm",
                    ),
                    rx.el.div(
                        rx.el.a(
                            "超級管理者登入",
                            href="/admin-login",
                            class_name="text-xs text-gray-400 hover:text-indigo-500 transition-colors",
                        ),
                        class_name="mt-4 text-center",
                    ),
                    class_name="bg-white py-8 px-4 shadow-xl sm:rounded-lg sm:px-10 border border-gray-100",
                ),
                class_name="mt-8 sm:mx-auto sm:w-full sm:max-w-md",
            ),
            class_name="flex min-h-screen flex-col justify-center py-12 sm:px-6 lg:px-8 bg-gray-50",
        ),
        on_mount=AuthState.check_logged_in,
    )


def register_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("user-plus", class_name="mx-auto h-12 w-auto text-indigo-600"),
                rx.el.h2(
                    "建立新帳號",
                    class_name="mt-6 text-center text-3xl font-extrabold tracking-tight text-gray-900",
                ),
                class_name="sm:mx-auto sm:w-full sm:max-w-md",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "顯示名稱 (Display Name)",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            placeholder="例如：小明",
                            on_change=AuthState.set_reg_display_name,
                            class_name="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "登入帳號 (Username)",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            placeholder="例如：xiaoming123",
                            on_change=AuthState.set_reg_username,
                            class_name="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "密碼 (Password)",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            type="password",
                            on_change=AuthState.set_reg_password,
                            class_name="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "確認密碼 (Confirm Password)",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            type="password",
                            on_change=AuthState.set_reg_confirm_password,
                            class_name="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
                        ),
                        class_name="mb-6",
                    ),
                    rx.cond(
                        AuthState.register_error != "",
                        rx.el.p(
                            AuthState.register_error,
                            class_name="mb-4 text-sm text-red-600 font-medium",
                        ),
                    ),
                    rx.cond(
                        AuthState.register_success != "",
                        rx.el.p(
                            AuthState.register_success,
                            class_name="mb-4 text-sm text-green-600 font-medium",
                        ),
                    ),
                    rx.el.button(
                        "立即註冊",
                        on_click=AuthState.register,
                        class_name="flex w-full justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all",
                    ),
                    rx.el.div(
                        rx.el.span("系統問題或權限申請？", class_name="text-gray-500"),
                        rx.el.a(
                            "留言給超級管理者",
                            href="/contact",
                            class_name="ml-1 font-medium text-indigo-600 hover:text-indigo-500",
                        ),
                        class_name="mt-6 text-center text-sm",
                    ),
                    class_name="bg-white py-8 px-4 shadow-xl sm:rounded-lg sm:px-10 border border-gray-100",
                ),
                class_name="mt-8 sm:mx-auto sm:w-full sm:max-w-md",
            ),
            class_name="flex min-h-screen flex-col justify-center py-12 sm:px-6 lg:px-8 bg-gray-50",
        ),
        on_mount=AuthState.check_logged_in,
    )


def leave_card(leave: Leave) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("calendar", class_name="h-5 w-5 text-indigo-500 mr-2"),
                    rx.el.span(
                        leave["leave_date"], class_name="font-semibold text-gray-900"
                    ),
                    class_name="flex items-center mb-1",
                ),
                rx.el.div(
                    rx.icon("clock", class_name="h-4 w-4 text-gray-400 mr-2"),
                    rx.el.span(
                        f"{leave['start_time']} - {leave['end_time']}",
                        class_name="text-sm text-gray-600",
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex-1",
            ),
            rx.el.div(
                rx.cond(
                    leave["note"] != "",
                    rx.el.p(
                        leave["note"], class_name="mt-2 text-sm text-gray-500 italic"
                    ),
                )
            ),
            class_name="flex-1",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("pencil", class_name="h-4 w-4"),
                on_click=lambda: LeaveState.open_edit_form(leave["id"]),
                class_name="p-2 text-gray-400 hover:text-indigo-600 transition-colors",
            ),
            rx.el.button(
                rx.icon("trash-2", class_name="h-4 w-4"),
                on_click=lambda: LeaveState.delete_leave(leave["id"]),
                class_name="p-2 text-gray-400 hover:text-red-600 transition-colors",
            ),
            class_name="flex gap-2",
        ),
        class_name="flex items-center justify-between p-4 bg-white border border-gray-100 rounded-xl hover:shadow-md transition-shadow mb-4",
    )


def leave_form_modal() -> rx.Component:
    return rx.cond(
        LeaveState.show_form,
        rx.el.div(
            rx.el.div(
                class_name="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity z-[60]",
                on_click=LeaveState.close_form,
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            rx.cond(
                                LeaveState.editing_id == -1, "新增休假", "編輯休假"
                            ),
                            class_name="text-xl font-bold text-gray-900 mb-4",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "日期",
                                class_name="block text-sm font-medium text-gray-700 mb-1",
                            ),
                            rx.el.input(
                                type="date",
                                on_change=LeaveState.set_form_date,
                                class_name="w-full p-2 border rounded-md mb-4",
                                default_value=LeaveState.form_date,
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.label(
                                        "開始時間",
                                        class_name="block text-sm font-medium text-gray-700 mb-1",
                                    ),
                                    rx.el.input(
                                        type="time",
                                        on_change=LeaveState.set_form_start_time,
                                        class_name="w-full p-2 border rounded-md",
                                        default_value=LeaveState.form_start_time,
                                    ),
                                    class_name="flex-1",
                                ),
                                rx.el.div(
                                    rx.el.label(
                                        "結束時間",
                                        class_name="block text-sm font-medium text-gray-700 mb-1",
                                    ),
                                    rx.el.input(
                                        type="time",
                                        on_change=LeaveState.set_form_end_time,
                                        class_name="w-full p-2 border rounded-md",
                                        default_value=LeaveState.form_end_time,
                                    ),
                                    class_name="flex-1",
                                ),
                                class_name="flex gap-4 mb-4",
                            ),
                            rx.el.label(
                                "備註 (選填)",
                                class_name="block text-sm font-medium text-gray-700 mb-1",
                            ),
                            rx.el.input(
                                placeholder="例如：去醫院掛號",
                                on_change=LeaveState.set_form_note,
                                class_name="w-full p-2 border rounded-md mb-4",
                                default_value=LeaveState.form_note,
                            ),
                            rx.cond(
                                LeaveState.form_error != "",
                                rx.el.p(
                                    LeaveState.form_error,
                                    class_name="text-red-500 text-sm mb-4",
                                ),
                            ),
                            rx.el.div(
                                rx.el.button(
                                    "取消",
                                    on_click=LeaveState.close_form,
                                    class_name="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200",
                                ),
                                rx.el.button(
                                    "儲存",
                                    on_click=LeaveState.save_leave,
                                    class_name="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700",
                                ),
                                class_name="flex justify-end gap-3",
                            ),
                        ),
                        class_name="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md",
                    ),
                    class_name="flex items-center justify-center min-h-screen p-4",
                ),
                class_name="fixed inset-0 z-[70] overflow-y-auto",
            ),
            class_name="relative z-[60]",
        ),
        rx.fragment(),
    )


def my_leaves_page() -> rx.Component:
    return protected_layout(
        rx.el.div(
            leave_form_modal(),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            "我的休假清單",
                            class_name="text-2xl font-bold text-gray-900",
                        ),
                        rx.el.p(
                            "管理您的個人預約記錄。", class_name="text-gray-500 text-sm"
                        ),
                        class_name="flex-1",
                    ),
                    rx.el.button(
                        rx.icon("plus", class_name="h-4 w-4 mr-2"),
                        "新增休假",
                        on_click=LeaveState.open_add_form,
                        class_name="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors",
                    ),
                    class_name="flex items-center justify-between mb-8",
                ),
                rx.cond(
                    LeaveState.my_leaves.length() == 0,
                    rx.el.div(
                        rx.icon(
                            "calendar-x",
                            class_name="mx-auto h-12 w-12 text-gray-300 mb-4",
                        ),
                        rx.el.h3(
                            "尚未有任何休假記錄",
                            class_name="text-lg font-medium text-gray-900",
                        ),
                        rx.el.p(
                            "點擊上方按鈕來新增您的第一筆預約。",
                            class_name="mt-1 text-sm text-gray-500",
                        ),
                        class_name="text-center py-12 bg-white rounded-2xl border-2 border-dashed border-gray-200",
                    ),
                    rx.el.div(rx.foreach(LeaveState.my_leaves, leave_card)),
                ),
            ),
        )
    )


from time_off_planning_system.states.calendar_state import CalendarState
from time_off_planning_system.states.admin_state import AdminState


def admin_login_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(
                    "shield-check", class_name="mx-auto h-12 w-auto text-slate-700"
                ),
                rx.el.h2(
                    "超級管理者登入",
                    class_name="mt-6 text-center text-3xl font-extrabold tracking-tight text-slate-900",
                ),
                rx.el.p(
                    "後台管理系統", class_name="mt-2 text-center text-sm text-slate-600"
                ),
                class_name="sm:mx-auto sm:w-full sm:max-w-md",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "管理員帳號",
                            class_name="block text-sm font-medium text-slate-700",
                        ),
                        rx.el.input(
                            placeholder="Admin Username",
                            on_change=AdminState.set_admin_login_username,
                            class_name="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-slate-500 focus:ring-slate-500 sm:text-sm p-2 border",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "管理員密碼",
                            class_name="block text-sm font-medium text-slate-700",
                        ),
                        rx.el.input(
                            type="password",
                            placeholder="Admin Password",
                            on_change=AdminState.set_admin_login_password,
                            class_name="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-slate-500 focus:ring-slate-500 sm:text-sm p-2 border",
                        ),
                        class_name="mb-6",
                    ),
                    rx.cond(
                        AdminState.admin_login_error != "",
                        rx.el.p(
                            AdminState.admin_login_error,
                            class_name="mb-4 text-sm text-red-600 font-medium",
                        ),
                    ),
                    rx.el.button(
                        "登入後台",
                        on_click=AdminState.admin_login,
                        class_name="flex w-full justify-center rounded-md border border-transparent bg-slate-800 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-slate-900 transition-all",
                    ),
                    rx.el.div(
                        rx.el.a(
                            "返回一般使用者登入",
                            href="/login",
                            class_name="font-medium text-slate-600 hover:text-slate-500",
                        ),
                        class_name="mt-6 text-center text-sm",
                    ),
                    class_name="bg-white py-8 px-4 shadow-xl sm:rounded-lg sm:px-10 border border-slate-100",
                ),
                class_name="mt-8 sm:mx-auto sm:w-full sm:max-w-md",
            ),
            class_name="flex min-h-screen flex-col justify-center py-12 sm:px-6 lg:px-8 bg-slate-50",
        ),
        on_mount=AdminState.check_admin_logged_in,
    )


def user_form_modal() -> rx.Component:
    return rx.cond(
        AdminState.show_user_form,
        rx.el.div(
            rx.el.div(
                class_name="fixed inset-0 bg-slate-900 bg-opacity-50 transition-opacity z-[60]",
                on_click=AdminState.close_user_form,
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            rx.cond(
                                AdminState.editing_user_id == -1,
                                "新增使用者",
                                "編輯使用者",
                            ),
                            class_name="text-xl font-bold text-slate-900 mb-4",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "顯示名稱",
                                class_name="block text-sm font-medium text-slate-700 mb-1",
                            ),
                            rx.el.input(
                                on_change=AdminState.set_form_display_name,
                                class_name="w-full p-2 border rounded-md mb-4",
                                default_value=AdminState.form_display_name,
                            ),
                            rx.el.label(
                                "帳號 (Username)",
                                class_name="block text-sm font-medium text-slate-700 mb-1",
                            ),
                            rx.el.input(
                                on_change=AdminState.set_form_username,
                                class_name="w-full p-2 border rounded-md mb-4",
                                default_value=AdminState.form_username,
                            ),
                            rx.el.label(
                                "密碼",
                                class_name="block text-sm font-medium text-slate-700 mb-1",
                            ),
                            rx.el.input(
                                type="password",
                                on_change=AdminState.set_form_password,
                                class_name="w-full p-2 border rounded-md mb-4",
                                default_value=AdminState.form_password,
                            ),
                            rx.cond(
                                AdminState.form_error != "",
                                rx.el.p(
                                    AdminState.form_error,
                                    class_name="text-red-500 text-sm mb-4",
                                ),
                            ),
                            rx.el.div(
                                rx.el.button(
                                    "取消",
                                    on_click=AdminState.close_user_form,
                                    class_name="px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 rounded-md hover:bg-slate-200",
                                ),
                                rx.el.button(
                                    "儲存",
                                    on_click=AdminState.save_user,
                                    class_name="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700",
                                ),
                                class_name="flex justify-end gap-3",
                            ),
                        ),
                        class_name="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md",
                    ),
                    class_name="flex items-center justify-center min-h-screen p-4",
                ),
                class_name="fixed inset-0 z-[70] overflow-y-auto",
            ),
            class_name="relative z-[60]",
        ),
        rx.fragment(),
    )


from time_off_planning_system.states.message_state import MessageState, Message


def message_card(msg: Message) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        msg["name"], class_name="text-lg font-bold text-slate-900"
                    ),
                    rx.el.span(
                        f"({msg['employee_id']})",
                        class_name="ml-2 text-sm text-slate-500",
                    ),
                    class_name="flex items-baseline",
                ),
                rx.el.div(
                    msg["submitted_at"],
                    class_name="text-xs font-medium bg-slate-100 text-slate-600 px-2 py-1 rounded-full",
                ),
                class_name="flex justify-between items-start mb-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("mail", class_name="h-4 w-4 text-slate-400 mr-2"),
                    rx.el.span(msg["email"], class_name="text-sm text-slate-600"),
                    class_name="flex items-center mb-1",
                ),
                rx.el.div(
                    rx.match(
                        msg["contact_method"],
                        (
                            "Line",
                            rx.icon(
                                "message-circle",
                                class_name="h-4 w-4 text-green-500 mr-2",
                            ),
                        ),
                        (
                            "WhatsApp",
                            rx.icon(
                                "phone", class_name="h-4 w-4 text-emerald-500 mr-2"
                            ),
                        ),
                        (
                            "Phone",
                            rx.icon(
                                "phone-call", class_name="h-4 w-4 text-blue-500 mr-2"
                            ),
                        ),
                        rx.icon("at-sign", class_name="h-4 w-4 text-slate-400 mr-2"),
                    ),
                    rx.el.span(
                        f"{msg['contact_method']}: {msg['contact_value']}",
                        class_name="text-sm text-slate-600",
                    ),
                    class_name="flex items-center",
                ),
                class_name="mb-4 p-3 bg-slate-50 rounded-lg",
            ),
            rx.el.p(
                msg["message"],
                class_name="text-slate-700 whitespace-pre-wrap text-sm leading-relaxed",
            ),
            class_name="p-6",
        ),
        rx.el.button(
            rx.icon("trash-2", class_name="h-4 w-4"),
            on_click=lambda: MessageState.delete_message(msg["id"]),
            class_name="absolute top-4 right-4 p-2 text-slate-300 hover:text-red-600 hover:bg-red-50 rounded-md transition-all",
        ),
        class_name="bg-white border border-slate-200 rounded-xl relative shadow-sm hover:shadow-md transition-shadow",
    )


def admin_dashboard_page() -> rx.Component:
    return rx.el.div(
        user_form_modal(),
        rx.el.nav(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("shield-check", class_name="h-8 w-8 text-white"),
                        rx.el.span(
                            "超級管理者後台",
                            class_name="ml-2 text-xl font-bold text-white",
                        ),
                        class_name="flex items-center",
                    ),
                    rx.el.button(
                        "登出後台",
                        on_click=AdminState.admin_logout,
                        class_name="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors",
                    ),
                    class_name="flex h-16 items-center justify-between",
                ),
                class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
            ),
            class_name="bg-slate-900 border-b border-slate-800 sticky top-0 z-50",
        ),
        rx.el.main(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.nav(
                            rx.el.button(
                                "使用者管理",
                                on_click=lambda: AdminState.set_active_tab("users"),
                                class_name=rx.cond(
                                    AdminState.active_tab == "users",
                                    "px-4 py-2 text-sm font-semibold text-indigo-600 border-b-2 border-indigo-600",
                                    "px-4 py-2 text-sm font-medium text-slate-500 hover:text-slate-700 border-b-2 border-transparent transition-colors",
                                ),
                            ),
                            rx.el.button(
                                "留言板管理",
                                on_click=lambda: AdminState.set_active_tab("messages"),
                                class_name=rx.cond(
                                    AdminState.active_tab == "messages",
                                    "px-4 py-2 text-sm font-semibold text-indigo-600 border-b-2 border-indigo-600",
                                    "px-4 py-2 text-sm font-medium text-slate-500 hover:text-slate-700 border-b-2 border-transparent transition-colors",
                                ),
                            ),
                            class_name="flex space-x-8 border-b border-slate-200",
                        ),
                        class_name="mb-8",
                    ),
                    rx.match(
                        AdminState.active_tab,
                        (
                            "users",
                            rx.el.div(
                                rx.el.div(
                                    rx.el.h2(
                                        "使用者管理",
                                        class_name="text-2xl font-bold text-slate-900",
                                    ),
                                    rx.el.button(
                                        rx.icon("plus", class_name="h-4 w-4 mr-2"),
                                        "新增使用者",
                                        on_click=AdminState.open_add_user_form,
                                        class_name="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors shadow-sm",
                                    ),
                                    class_name="flex justify-between items-center mb-6",
                                ),
                                rx.el.div(
                                    rx.el.table(
                                        rx.el.thead(
                                            rx.el.tr(
                                                rx.el.th(
                                                    "ID",
                                                    class_name="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider",
                                                ),
                                                rx.el.th(
                                                    "顯示名稱",
                                                    class_name="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider",
                                                ),
                                                rx.el.th(
                                                    "帳號",
                                                    class_name="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider",
                                                ),
                                                rx.el.th(
                                                    "操作",
                                                    class_name="px-6 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider",
                                                ),
                                            ),
                                            class_name="bg-slate-50 border-b border-slate-200",
                                        ),
                                        rx.el.tbody(
                                            rx.foreach(
                                                AuthState.users,
                                                lambda user: rx.el.tr(
                                                    rx.el.td(
                                                        user["id"].to(str),
                                                        class_name="px-6 py-4 whitespace-nowrap text-sm text-slate-500",
                                                    ),
                                                    rx.el.td(
                                                        user["display_name"],
                                                        class_name="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900",
                                                    ),
                                                    rx.el.td(
                                                        user["username"],
                                                        class_name="px-6 py-4 whitespace-nowrap text-sm text-slate-500",
                                                    ),
                                                    rx.el.td(
                                                        rx.el.div(
                                                            rx.el.button(
                                                                rx.icon(
                                                                    "pencil",
                                                                    class_name="h-4 w-4",
                                                                ),
                                                                on_click=lambda: AdminState.open_edit_user_form(
                                                                    user["id"]
                                                                ),
                                                                class_name="text-indigo-600 hover:text-indigo-900",
                                                            ),
                                                            rx.cond(
                                                                user["id"] != 1,
                                                                rx.el.button(
                                                                    rx.icon(
                                                                        "trash-2",
                                                                        class_name="h-4 w-4",
                                                                    ),
                                                                    on_click=lambda: AdminState.delete_user(
                                                                        user["id"]
                                                                    ),
                                                                    class_name="text-red-600 hover:text-red-900",
                                                                ),
                                                                rx.fragment(),
                                                            ),
                                                            class_name="flex justify-end gap-3",
                                                        ),
                                                        class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium",
                                                    ),
                                                    class_name="hover:bg-slate-50 transition-colors border-b border-slate-100",
                                                ),
                                            )
                                        ),
                                        class_name="min-w-full divide-y divide-slate-200 table-auto",
                                    ),
                                    class_name="overflow-hidden border border-slate-200 rounded-xl bg-white",
                                ),
                            ),
                        ),
                        (
                            "messages",
                            rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.h2(
                                            "留言板管理",
                                            class_name="text-2xl font-bold text-slate-900",
                                        ),
                                        rx.el.p(
                                            f"目前共有 {MessageState.messages.length()} 則留言",
                                            class_name="text-slate-500 text-sm",
                                        ),
                                    ),
                                    class_name="mb-6",
                                ),
                                rx.cond(
                                    MessageState.messages.length() == 0,
                                    rx.el.div(
                                        rx.icon(
                                            "message-square-dashed",
                                            class_name="h-12 w-12 text-slate-300 mx-auto mb-4",
                                        ),
                                        rx.el.p(
                                            "尚無任何留言",
                                            class_name="text-slate-400 font-medium",
                                        ),
                                        class_name="text-center py-20 bg-white border-2 border-dashed border-slate-200 rounded-xl",
                                    ),
                                    rx.el.div(
                                        rx.foreach(
                                            MessageState.sorted_messages, message_card
                                        ),
                                        class_name="grid grid-cols-1 md:grid-cols-2 gap-6",
                                    ),
                                ),
                            ),
                        ),
                        rx.fragment(),
                    ),
                ),
                class_name="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8",
            ),
            class_name="min-h-screen bg-slate-50 font-['Inter']",
        ),
        on_mount=AdminState.check_admin_auth,
    )


def month_cell(cell_data: dict) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.cond(
                cell_data["day"].to(int) > 0,
                rx.el.span(
                    cell_data["day"].to(str),
                    class_name=rx.cond(
                        cell_data["is_today"].to(bool),
                        "flex items-center justify-center w-8 h-8 rounded-full bg-indigo-600 text-white font-bold",
                        "flex items-center justify-center w-8 h-8 text-gray-900",
                    ),
                ),
                rx.fragment(),
            ),
            class_name="flex justify-center mb-1",
        ),
        rx.cond(
            cell_data["day"].to(int) > 0,
            rx.el.div(
                rx.foreach(
                    LeaveState.all_leaves,
                    lambda leave: rx.cond(
                        leave["leave_date"] == cell_data["date_str"].to(str),
                        rx.el.div(
                            rx.el.span(
                                leave["display_name"],
                                class_name="text-xs font-medium truncate",
                            ),
                            class_name="bg-indigo-100 text-indigo-700 rounded px-1 mb-1 truncate text-xs",
                        ),
                        rx.fragment(),
                    ),
                ),
                class_name="flex flex-col gap-1 overflow-y-auto max-h-20",
            ),
            rx.fragment(),
        ),
        on_click=lambda: rx.cond(
            cell_data["day"].to(int) > 0,
            CalendarState.select_day(cell_data["day"].to(int)),
            rx.console_log("invalid"),
        ),
        class_name=rx.cond(
            cell_data["is_current_month"].to(bool),
            "min-h-[100px] border border-gray-200 p-1 cursor-pointer hover:bg-gray-50 transition-colors bg-white",
            "min-h-[100px] border border-gray-200 p-1 bg-gray-50 opacity-50",
        ),
    )


def month_view() -> rx.Component:
    weekdays = ["日", "一", "二", "三", "四", "五", "六"]
    return rx.el.div(
        rx.el.div(
            rx.foreach(
                weekdays,
                lambda d: rx.el.div(
                    d,
                    class_name="py-2 text-center text-sm font-semibold text-gray-700 border border-gray-200 bg-gray-50",
                ),
            ),
            class_name="grid grid-cols-7",
        ),
        rx.el.div(
            rx.foreach(
                CalendarState.month_grid,
                lambda week: rx.fragment(rx.foreach(week, month_cell)),
            ),
            class_name="grid grid-cols-7",
        ),
        class_name="border-l border-t border-gray-200 rounded-lg overflow-hidden",
    )


def week_column_component(
    col: dict[str, str | int | bool | list[dict[str, str | int]]],
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                col["weekday_label"].to(str), class_name="text-xs text-gray-500 mb-1"
            ),
            rx.el.div(
                col["day_num"].to(str),
                class_name=rx.cond(
                    col["is_today"].to(bool),
                    "flex items-center justify-center w-8 h-8 rounded-full bg-indigo-600 text-white font-bold mx-auto",
                    "flex items-center justify-center w-8 h-8 text-gray-900 font-medium mx-auto",
                ),
            ),
            class_name="text-center py-2 border-b border-gray-200 bg-gray-50",
        ),
        rx.el.div(
            rx.foreach(
                col["leaves"].to(list[dict[str, str | int]]),
                lambda leave: rx.el.div(
                    rx.el.div(
                        leave["display_name"].to(str),
                        class_name="font-semibold text-xs truncate",
                    ),
                    rx.el.div(
                        f"{leave['start_time']} - {leave['end_time']}",
                        class_name="text-[10px] opacity-90",
                    ),
                    class_name=leave["color_class"].to(str)
                    + " p-2 rounded-md border mb-2 shadow-sm",
                ),
            ),
            class_name="p-2 min-h-[400px]",
        ),
        class_name="border-r border-gray-200 last:border-r-0 flex-1 min-w-[120px]",
    )


def week_view() -> rx.Component:
    return rx.el.div(
        rx.foreach(CalendarState.week_columns, week_column_component),
        class_name="flex flex-row bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm overflow-x-auto",
    )


def day_hour_row(
    hour_data: dict[str, str | list[dict[str, str | int]]],
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            hour_data["hour_str"].to(str),
            class_name="w-20 py-4 text-right pr-4 text-sm font-medium text-gray-500 border-r border-gray-200 flex-shrink-0",
        ),
        rx.el.div(
            rx.foreach(
                hour_data["leaves"].to(list[dict[str, str | int]]),
                lambda leave: rx.el.div(
                    rx.el.div(
                        rx.el.span(
                            leave["display_name"].to(str),
                            class_name="font-semibold text-sm",
                        ),
                        rx.el.span(
                            f"{leave['start_time']} - {leave['end_time']}",
                            class_name="text-xs ml-2 opacity-90",
                        ),
                        class_name="flex items-center",
                    ),
                    rx.cond(
                        leave["note"].to(str) != "",
                        rx.el.div(
                            leave["note"].to(str), class_name="text-xs mt-1 opacity-80"
                        ),
                        rx.fragment(),
                    ),
                    class_name=leave["color_class"].to(str)
                    + " p-2 rounded-md border mr-2 mb-2 flex-1 shadow-sm min-w-[150px]",
                ),
            ),
            class_name="flex-1 p-2 flex flex-wrap gap-2",
        ),
        class_name="flex border-b border-gray-100 last:border-b-0 min-h-[80px]",
    )


def day_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    CalendarState.display_title,
                    class_name="text-lg font-bold text-gray-900",
                ),
                class_name="p-4 border-b border-gray-200 bg-gray-50",
            ),
            rx.foreach(CalendarState.day_hours, day_hour_row),
            class_name="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden",
        )
    )


def contact_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(
                    "message-square", class_name="mx-auto h-12 w-auto text-indigo-600"
                ),
                rx.el.h2(
                    "留言給超級管理者",
                    class_name="mt-6 text-center text-3xl font-extrabold text-gray-900",
                ),
                rx.el.p(
                    "若您忘記密碼或需要開通權限，請填寫下方表單。",
                    class_name="mt-2 text-center text-sm text-gray-600",
                ),
                class_name="sm:mx-auto sm:w-full sm:max-w-md",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "員工編號 (Employee ID)",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            on_change=MessageState.set_form_employee_id,
                            class_name="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border sm:text-sm",
                            default_value=MessageState.form_employee_id,
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "姓名 (Name)",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            on_change=MessageState.set_form_name,
                            class_name="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border sm:text-sm",
                            default_value=MessageState.form_name,
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "信箱 (Email)",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            type="email",
                            on_change=MessageState.set_form_email,
                            class_name="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border sm:text-sm",
                            default_value=MessageState.form_email,
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "通訊方式",
                                class_name="block text-sm font-medium text-gray-700",
                            ),
                            rx.el.select(
                                rx.el.option("Line", value="Line"),
                                rx.el.option("WhatsApp", value="WhatsApp"),
                                rx.el.option("Phone", value="Phone"),
                                rx.el.option("Other", value="Other"),
                                on_change=MessageState.set_contact_method,
                                value=MessageState.form_contact_method,
                                class_name="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border sm:text-sm bg-white appearance-none",
                            ),
                            class_name="w-1/3",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "帳號/號碼",
                                class_name="block text-sm font-medium text-gray-700",
                            ),
                            rx.el.input(
                                on_change=MessageState.set_form_contact_value,
                                placeholder=rx.match(
                                    MessageState.form_contact_method,
                                    ("Line", "請輸入 Line ID"),
                                    ("WhatsApp", "請輸入電話號碼"),
                                    ("Phone", "請輸入電話號碼"),
                                    "請輸入聯絡方式",
                                ),
                                class_name="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border sm:text-sm",
                                default_value=MessageState.form_contact_value,
                            ),
                            class_name="flex-1",
                        ),
                        class_name="flex gap-4 mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "留言內容",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.textarea(
                            on_change=MessageState.set_form_message,
                            rows="4",
                            class_name="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border sm:text-sm",
                            default_value=MessageState.form_message,
                        ),
                        class_name="mb-6",
                    ),
                    rx.cond(
                        MessageState.form_error != "",
                        rx.el.p(
                            MessageState.form_error,
                            class_name="mb-4 text-sm text-red-600 font-medium",
                        ),
                    ),
                    rx.cond(
                        MessageState.form_success != "",
                        rx.el.p(
                            MessageState.form_success,
                            class_name="mb-4 text-sm text-green-600 font-medium",
                        ),
                    ),
                    rx.el.button(
                        "送出留言",
                        on_click=MessageState.submit_message,
                        class_name="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 transition-colors mb-4",
                    ),
                    rx.el.div(
                        rx.el.a(
                            "返回登入頁面",
                            href="/login",
                            class_name="text-sm font-medium text-indigo-600 hover:text-indigo-500",
                        ),
                        class_name="text-center",
                    ),
                    class_name="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10 border border-gray-100",
                ),
                class_name="mt-8 sm:mx-auto sm:w-full sm:max-w-lg",
            ),
            class_name="flex min-h-screen flex-col justify-center py-12 sm:px-6 lg:px-8 bg-gray-50",
        )
    )


def calendar_page() -> rx.Component:
    return protected_layout(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.button(
                        rx.icon("chevron-left", class_name="h-5 w-5"),
                        on_click=CalendarState.go_prev,
                        class_name="p-2 rounded-md border hover:bg-gray-50",
                    ),
                    rx.el.button(
                        "今天",
                        on_click=CalendarState.go_today,
                        class_name="px-4 py-2 border rounded-md hover:bg-gray-50 font-medium",
                    ),
                    rx.el.button(
                        rx.icon("chevron-right", class_name="h-5 w-5"),
                        on_click=CalendarState.go_next,
                        class_name="p-2 rounded-md border hover:bg-gray-50",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.h2(
                    CalendarState.display_title,
                    class_name="text-xl font-bold text-gray-900",
                ),
                rx.el.div(
                    rx.el.button(
                        "月",
                        on_click=lambda: CalendarState.set_view_mode("month"),
                        class_name=rx.cond(
                            CalendarState.view_mode == "month",
                            "px-4 py-2 border border-indigo-600 bg-indigo-50 text-indigo-700 font-medium rounded-l-md",
                            "px-4 py-2 border border-r-0 rounded-l-md hover:bg-gray-50",
                        ),
                    ),
                    rx.el.button(
                        "週",
                        on_click=lambda: CalendarState.set_view_mode("week"),
                        class_name=rx.cond(
                            CalendarState.view_mode == "week",
                            "px-4 py-2 border border-indigo-600 bg-indigo-50 text-indigo-700 font-medium",
                            "px-4 py-2 border border-r-0 hover:bg-gray-50",
                        ),
                    ),
                    rx.el.button(
                        "日",
                        on_click=lambda: CalendarState.set_view_mode("day"),
                        class_name=rx.cond(
                            CalendarState.view_mode == "day",
                            "px-4 py-2 border border-indigo-600 bg-indigo-50 text-indigo-700 font-medium rounded-r-md",
                            "px-4 py-2 border rounded-r-md hover:bg-gray-50",
                        ),
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex items-center justify-between mb-6 bg-white p-4 rounded-xl border border-gray-200 shadow-sm",
            ),
            rx.match(
                CalendarState.view_mode,
                ("month", month_view()),
                ("week", week_view()),
                ("day", day_view()),
                month_view(),
            ),
        )
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, route="/")
app.add_page(login_page, route="/login")
app.add_page(register_page, route="/register")
app.add_page(my_leaves_page, route="/my-leaves", on_load=AuthState.check_auth)
app.add_page(calendar_page, route="/calendar", on_load=AuthState.check_auth)
app.add_page(admin_login_page, route="/admin-login")
app.add_page(admin_dashboard_page, route="/admin", on_load=AdminState.check_admin_auth)
app.add_page(contact_page, route="/contact")