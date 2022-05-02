"""
Module responsible for interacting with git via subprocesses.


Author: Tom Fleet
Created: 22/12/2021
"""

from __future__ import annotations

import asyncio
import shutil
import sys
from pathlib import Path

from pytoil.exceptions import GitNotInstalledError

GIT = shutil.which("git")


class Git:
    def __init__(self, git: str | None = GIT) -> None:
        self.git = git

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + f"(git={self.git!r})"

    __slots__ = ("git",)

    async def clone(self, url: str, cwd: Path, silent: bool = True) -> None:
        """
        Clone a repo.

        Args:
            url (str): The clone url of the repo
            cwd (Path): The cwd under which to clone
            silent (bool, optional): Whether to hook the output
                up to stdout and stderr (False) or to discard and keep silent (True).
                Defaults to True.
        """
        if not self.git:
            raise GitNotInstalledError

        proc = await asyncio.create_subprocess_exec(
            self.git,
            "clone",
            url,
            cwd=cwd,
            stdout=asyncio.subprocess.DEVNULL if silent else sys.stdout,
            stderr=asyncio.subprocess.DEVNULL if silent else sys.stderr,
        )

        await proc.wait()

    async def init(self, cwd: Path, silent: bool = True) -> None:
        """
        Initialise a new git repo.

        Args:
            cwd (Path): The cwd to initialise the repo in.
            silent (bool, optional): Whether to hook the output
                up to stdout and stderr (False) or to discard and keep silent (True).
                Defaults to True.
        """
        if not self.git:
            raise GitNotInstalledError

        proc = await asyncio.create_subprocess_exec(
            self.git,
            "init",
            cwd=cwd,
            stdout=asyncio.subprocess.DEVNULL if silent else sys.stdout,
            stderr=asyncio.subprocess.DEVNULL if silent else sys.stderr,
        )

        await proc.wait()

    async def add(self, cwd: Path, silent: bool = True) -> None:
        """
        Stages all files in cwd.

        Args:
            cwd (Path): The cwd to stage all child files in.
            silent (bool, optional): Whether to hook the output up
                to stdout and stderr (False) or to discard and keep silent (True).
                Defaults to True.
        """
        if not self.git:
            raise GitNotInstalledError

        proc = await asyncio.create_subprocess_exec(
            self.git,
            "add",
            "-A",
            cwd=cwd,
            stdout=asyncio.subprocess.DEVNULL if silent else sys.stdout,
            stderr=asyncio.subprocess.DEVNULL if silent else sys.stderr,
        )

        await proc.wait()

    async def commit(
        self,
        cwd: Path,
        message: str = "Initial Commit (Automated at Project Creation)",
        silent: bool = True,
    ) -> None:
        """
        Commits the current state.

        Args:
            cwd (Path): cwd of the repo to commit.
            message (str, optional): Optional commit message.
                Defaults to "Initial Commit (Automated at Project Creation)"
            silent (bool, optional): Whether to hook the output up
                to stdout and stderr (False) or to discard and keep silent (True).
                Defaults to True.
        """
        if not self.git:
            raise GitNotInstalledError

        proc = await asyncio.create_subprocess_exec(
            self.git,
            "commit",
            "-m",
            message,
            cwd=cwd,
            stdout=asyncio.subprocess.DEVNULL if silent else sys.stdout,
            stderr=asyncio.subprocess.DEVNULL if silent else sys.stderr,
        )

        await proc.wait()

    async def set_upstream(
        self, owner: str, repo: str, cwd: Path, silent: bool = True
    ) -> None:
        """
        Sets the upstream repo for a local repo, e.g. on a cloned fork.

        Note difference between origin and upstream, origin of a cloned fork
        would be user/forked_repo where as upstream would be original_user/forked_repo.

        Args:
            owner (str): Owner of the upstream repo.
            repo (str): Name of the upstream repo (typically the same as the fork)
            cwd (Path): Root of the project where the local git repo is.
            silent (bool, optional): Whether to hook the output
                up to stdout and stderr (False) or to discard and keep silent (True).
                Defaults to True.
        """
        if not self.git:
            raise GitNotInstalledError

        base_url = "https://github.com"
        constructed_upstream = f"{base_url}/{owner}/{repo}.git"

        proc = await asyncio.create_subprocess_exec(
            self.git,
            "remote",
            "add",
            "upstream",
            constructed_upstream,
            cwd=cwd,
            stdout=asyncio.subprocess.DEVNULL if silent else sys.stdout,
            stderr=asyncio.subprocess.DEVNULL if silent else sys.stderr,
        )

        await proc.wait()
