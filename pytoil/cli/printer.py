"""
Styles for pytoil's output using rich.


Author: Tom Fleet
Created: 05/02/2022
"""

from __future__ import annotations

import sys

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.style import Style
from rich.theme import Theme

__all__ = ("Printer", "printer")


class Printer:
    """
    Pytoil's default CLI output printer, designed for user
    friendly, colourful output, not for logging.
    """

    _pytoil_theme = Theme(
        styles={
            "title": Style(color="bright_cyan", bold=True),
            "info": Style(color="bright_cyan"),
            "warning": Style(color="yellow", bold=True),
            "error": Style(color="bright_red", bold=True),
            "error_message": Style(color="white", bold=True),
            "good": Style(color="bright_green"),
            "note": Style(color="white", bold=True),
            "subtle": Style(color="bright_black", italic=True),
        }
    )

    _pytoil_console = Console(theme=_pytoil_theme)

    __slots__ = ()

    def title(self, msg: str, spaced: bool = True) -> None:
        """
        Print a bold title message or section header.
        """
        to_print = f"{msg}"
        if spaced:
            to_print = f"{msg}\n"
        self._pytoil_console.print(to_print, style="title")

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
        Print a note, designed for supplementary info on another
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

    def progress(self) -> Progress:
        """
        Return a pre-configured rich spinner.
        """
        text_column = TextColumn("{task.description}")
        spinner_column = SpinnerColumn("simpleDotsScrolling", style="bold white")
        return Progress(text_column, spinner_column, transient=True)

    def subtle(self, msg: str) -> None:
        """
        Print subtle greyed out text.
        """
        self._pytoil_console.print(msg, style="subtle", markup=None)


# Export a default printer
printer = Printer()
