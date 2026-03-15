import reflex as rx


def index() -> rx.Component:
    return rx.container(
        rx.box(
            "What is Reflex?",
            text_align="right",
        ),
        rx.box(
            "ピュアPythonでwebアプリを書こう!",
            text_alighn="left",
        )
    )

app = rx.App()
app.add_page(index)