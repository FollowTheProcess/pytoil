"""
Interface that all starter classes must satisfy.

These templates are not supposed to be exhaustive, for that the user
is better off using pytoil's cookiecutter functionality.

The templates defined in the `starters` module are exactly that,
a starter. A good analogous reference would be the behaviour of
`cargo new` in rust, which simply sets up a few basic sub directories
and a "hello world" function main.rs.


Author: Tom Fleet
Created: 29/12/2021
"""

from __future__ import annotations

from typing import Protocol


class Starter(Protocol):
    async def generate(self, username: str | None = None) -> None:
        """
        Implements the generation of the project starter template.
        """
        ...
