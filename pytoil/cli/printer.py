"""
Styles for pytoil's output using rich.


Author: Tom Fleet
Created: 05/02/2022
"""

from rich.console import Console
from rich.style import Style
from rich.theme import Theme

__all__ = ["Printer"]


class Printer:
    _title_style = Style(color="bright_cyan", bold=True)
    _info_style = Style(color="bright_cyan")
    _warning_style = Style(color="yellow")
    _good_style = Style(color="bright_green")
    _error_style = Style(color="bright_red", bold=True)
    _error_message_style = Style(color="white", bold=True)

    _pytoil_theme = Theme(
        styles={
            "title": _title_style,
            "info": _info_style,
            "warning": _warning_style,
            "error": _error_style,
            "error_message": _error_message_style,
            "good": _good_style,
        }
    )

    _pytoil_console = Console(theme=_pytoil_theme)

    def title(self, msg: str) -> None:
        self._pytoil_console.print(f"{msg}\n", style="title")

    def warn(self, msg: str) -> None:
        self._pytoil_console.print(f"⚠️  {msg}", style="warning")

    def info(self, msg: str) -> None:
        self._pytoil_console.print(f"💡 {msg}", style="info")

    def error(self, msg: str) -> None:
        self._pytoil_console.print(
            f"[error]✘  Error: [/error][error_message]{msg}[/error_message]"
        )

    def good(self, msg: str) -> None:
        self._pytoil_console.print(f"✔  {msg}", style="good")


if __name__ == "__main__":
    printer = Printer()
    printer.title("This is a title")
    printer.warn("This is a warning")
    printer.info("This is some info")
    printer.error("This is an error")
    printer.good("Cloned something")
