import reflex as rx


class LangState(rx.State):
    """Global language state. Supported values: 'zh' (Traditional Chinese), 'en' (English)."""

    lang: str = "zh"

    @rx.event
    def set_lang(self, value: str):
        self.lang = value
