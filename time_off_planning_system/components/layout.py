import reflex as rx
from time_off_planning_system.components.navbar import navbar
from time_off_planning_system.states.auth_state import AuthState
from time_off_planning_system.states.leave_state import LeaveState
from time_off_planning_system.states.message_state import MessageState

_POLL_INTERVAL_MS = 3000


def protected_layout(content: rx.Component) -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.main(
            rx.el.div(content, class_name="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8"),
            class_name="min-h-screen bg-gray-50",
        ),
        # Hidden polling timers — detect external store changes every 3 s
        rx.moment(interval=_POLL_INTERVAL_MS, on_change=AuthState.check_store_update, display="none"),
        rx.moment(interval=_POLL_INTERVAL_MS, on_change=LeaveState.check_store_update, display="none"),
        rx.moment(interval=_POLL_INTERVAL_MS, on_change=MessageState.check_store_update, display="none"),
        class_name="min-h-screen font-['Inter']",
    )