"""
Dependabot does not yet support updating dependencies specified
using a PEP 621 pyproject.toml.

This script is a local version that is almost certainly not
as good, but it'll do until they implement PEP621 support.

It just shows any potential differences, "potential" because it's
version parsing is best guess and not perfect.

Run with nox --session dependabot to guarantee dependencies are
installed.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import rtoml
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table, box

PROJECT_URL = "https://pypi.org/pypi/{project}/json"
PYPROJECT_TOML = Path(__file__).parent.parent.joinpath("pyproject.toml").resolve()


@dataclass
class Difference:
    """
    Object representing a potential difference in project versions.
    """

    name: str
    current: str
    latest: str


@dataclass
class Version:
    """
    Object representing a dependency version, ensures that if
    a version is e.g. "6", this is canonicalised to "6.0.0"
    """

    version: str

    def __str__(self) -> str:
        """
        Canonicalises the version.
        """
        while len(self.version.split(".")) < 3:
            self.version = f"{self.version}.0"

        return self.version


async def get_latest_versions(projects: list[str]) -> dict[str, str]:
    """
    Gets the latest version for `project` by
    hitting the PyPI JSON API.

    Args:
        project (list[str]): List of projects to get
            latest versions for.

    Raises:
        ValueError: If the project does not have a
            version key (should never happen).

    Returns:
        dict[str, str]: Map of project: version
    """
    logger.info("Getting latest versions")
    results: dict[str, str] = {}
    async with httpx.AsyncClient(
        http2=True,
        headers={"User-Agent": "pytoil-pmd-script", "Accept": "application/json"},
    ) as client:
        for hit in asyncio.as_completed(
            [
                client.get(PROJECT_URL.format(project=project), follow_redirects=True)
                for project in projects
            ]
        ):
            result = await hit
            data: dict[str, Any] = result.json()
            name = data.get("info", {}).get("name", "Unknown")
            version = Version(data.get("info", {}).get("version", "Unknown"))
            logger.info(f"Latest version for {name!r} is {version}")
            results[name] = str(version)

    return results


async def get_current_versions() -> dict[str, str]:
    """
    Extracts all the current versions of all dependencies
    from pyproject.toml

    Returns:
        dict[str, str]: Map of project: version
    """
    with open(PYPROJECT_TOML, encoding="utf-8") as f:
        contents = rtoml.load(f)

    all_deps: list[str] = []
    results: dict[str, str] = {}

    if dependencies := contents.get("project", {}).get("dependencies"):
        all_deps.extend(dependencies)

    if (
        dev_dependencies := contents.get("project", {})
        .get("optional-dependencies", {})
        .get("dev")
    ):
        all_deps.extend(dev_dependencies)

    for dep in all_deps:
        # Because we've pinned everything, this is easy
        name, v = dep.split("==")
        version = Version(v)
        # Look for additional [http2] type things
        if "[" in name:
            bracket_start = name.index("[")
            name = name[:bracket_start]
        logger.info(f"Current version for {name!r} is {version}")

        results[name] = str(version)

    return results


async def main() -> None:
    """
    Main routine.

    Raises:
        ValueError: If the number of projects in pyproject.toml
            and those coming back from PyPI differ
    """
    console = Console()
    current_versions = await get_current_versions()
    latest_versions = await get_latest_versions(projects=list(current_versions.keys()))

    if len(current_versions) != len(latest_versions):
        raise ValueError(
            f"Different lengths, current: {len(current_versions)}, latest:"
            f" {len(latest_versions)}"
        )

    differences: list[Difference] = []

    for project in current_versions.items():
        name, version = project
        if latest_versions[name] != version:
            diff = Difference(name=name, current=version, latest=latest_versions[name])
            differences.append(diff)

    table = Table(box=box.SIMPLE)
    table.add_column("Name", style="bold white")
    table.add_column("Current", style="red")
    table.add_column("Latest", style="green")

    if len(differences) == 0:
        console.print("Everything is up to date ✔", style="bold green")
        return

    console.print("⚠️  Potential Differences detected:", style="bold yellow")

    for diff in differences:
        table.add_row(diff.name, diff.current, diff.latest)

    console.print(table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="poormans_dependabot", description="Sort of dependabot-like local utility"
    )
    parser.add_argument("--verbose", action="store_true", help="Show verbose log info")
    args = parser.parse_args()

    if args.verbose:
        LOG_LEVEL = logging.INFO
    else:
        LOG_LEVEL = logging.WARNING

    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)
    ch = RichHandler()
    ch.setLevel(LOG_LEVEL)
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    asyncio.run(main=main())
