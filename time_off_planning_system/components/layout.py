import reflex as rx
from time_off_planning_system.components.navbar import navbar


def protected_layout(content: rx.Component) -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.main(
            rx.el.div(content, class_name="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8"),
            class_name="min-h-screen bg-gray-50",
        ),
        class_name="min-h-screen font-['Inter']",
    )