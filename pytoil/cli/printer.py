"""
Styles for pytoil's output using rich.


Author: Tom Fleet
Created: 05/02/2022
"""

import sys

from rich.console import Console
from rich.style import Style
from rich.theme import Theme

__all__ = ["Printer", "printer"]


class Printer:
    """
    Pytoil's default CLI output printer, designed for user
    friendly, colourful output, not for logging.
    """

    _title_style = Style(color="bright_cyan", bold=True)
    _info_style = Style(color="bright_cyan")
    _warning_style = Style(color="yellow", bold=True)
    _good_style = Style(color="bright_green")
    _error_style = Style(color="bright_red", bold=True)
    _error_message_style = Style(color="white", bold=True)
    _note_style = Style(color="white", bold=True)

    _pytoil_theme = Theme(
        styles={
            "title": _title_style,
            "info": _info_style,
            "warning": _warning_style,
            "error": _error_style,
            "error_message": _error_message_style,
            "good": _good_style,
            "note": _note_style,
        }
    )

    _pytoil_console = Console(theme=_pytoil_theme)

    __slots__ = ()

    def title(self, msg: str) -> None:
        """
        Print a bold title message or section header.
        """
        self._pytoil_console.print(f"{msg}\n", style="title")

    def warn(self, msg: str, exits: int | None = None) -> None:
        """
        Print a warning message.

        If `exits` is not None, will call `sys.exit` with given code.
        """
        self._pytoil_console.print(f"⚠️  {msg}", style="warning")
        if exits is not None:
            sys.exit(exits)

    def info(self, msg: str, exits: int | None = None, spaced: bool = False) -> None:
        """
        Print an info message.

        If `exits` is not None, will call `sys.exit` with given code.

        If spaced is True, a new line will be printed before and after the message.
        """
        to_print = f"💡 {msg}"
        if spaced:
            to_print = f"\n💡 {msg}\n"

        self._pytoil_console.print(to_print, style="info")
        if exits is not None:
            sys.exit(exits)

    def error(self, msg: str, exits: int | None = None) -> None:
        """
        Print an error message.

        If `exits` is not None, will call `sys.exit` with given code.
        """
        self._pytoil_console.print(
            f"[error]✘  Error: [/error][error_message]{msg}[/error_message]"
        )
        if exits is not None:
            sys.exit(exits)

    def good(self, msg: str, exits: int | None = None) -> None:
        """
        Print a success message.

        If `exits` is not None, will call `sys.exit` with given code.
        """
        self._pytoil_console.print(f"✔  {msg}", style="good")
        if exits is not None:
            sys.exit(exits)

    def note(self, msg: str, exits: int | None = None) -> None:
        """
        Print an note, designed for supplementary info on another
        printer method.

        If `exits` is not None, will call `sys.exit` with given code.
        """
        self._pytoil_console.print(f"[note]Note:[/note] {msg}")
        if exits is not None:
            sys.exit(exits)

    def text(self, msg: str, exits: int | None = None) -> None:
        """
        Print default text.

        If `exits` is not None, will call `sys.exit` with given code.
        """
        self._pytoil_console.print(msg, style="default")
        if exits is not None:
            sys.exit(exits)


# Export a default printer
printer = Printer()


if __name__ == "__main__":
    printer.note("This is a note")
