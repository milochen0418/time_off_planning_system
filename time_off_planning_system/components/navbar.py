import reflex as rx
from time_off_planning_system.states.auth_state import AuthState


def nav_link(label: str, href: str, active: bool) -> rx.Component:
    return rx.el.a(
        label,
        href=href,
        class_name=rx.cond(
            active,
            "text-indigo-600 border-b-2 border-indigo-600 px-1 pt-1 text-sm font-semibold",
            "text-gray-500 hover:text-gray-700 hover:border-gray-300 border-b-2 border-transparent px-1 pt-1 text-sm font-medium transition-colors",
        ),
    )


def navbar() -> rx.Component:
    return rx.el.nav(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("calendar-check", class_name="h-8 w-8 text-indigo-600"),
                        rx.el.span(
                            "預約休假管理系統",
                            class_name="ml-2 text-xl font-bold text-gray-900",
                        ),
                        class_name="flex shrink-0 items-center",
                    ),
                    rx.el.div(
                        nav_link(
                            "我的休假",
                            "/my-leaves",
                            AuthState.router.page.path == "/my-leaves",
                        ),
                        nav_link(
                            "共用日曆",
                            "/calendar",
                            AuthState.router.page.path == "/calendar",
                        ),
                        class_name="ml-10 flex space-x-8",
                    ),
                    class_name="flex h-16 justify-between",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.span(
                            f"你好, {AuthState.current_display_name}",
                            class_name="text-sm font-medium text-gray-700 mr-4",
                        ),
                        rx.el.button(
                            "登出",
                            on_click=AuthState.logout,
                            class_name="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50",
                        ),
                        class_name="flex items-center",
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex h-16 justify-between",
            ),
            class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
        ),
        class_name="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm",
    )