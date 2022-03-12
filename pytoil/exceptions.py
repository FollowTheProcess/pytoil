"""
Exceptions implemented in pytoil.
"""


from __future__ import annotations


class PytoilException(Exception):
    """
    Base pytoil exception from which all subclasses
    must inherit.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ExternalToolNotInstalledError(PytoilException):
    """
    Base exception for any child exception responsible
    for raising in the presence of a required external
    tool that's not installed.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class GitNotInstalledError(ExternalToolNotInstalledError):
    """
    Raise when calling something that needs the user
    to have git installed.
    """

    def __init__(self) -> None:
        self.message = "'git' executable not found on $PATH. Is git installed?"
        super().__init__(self.message)


class CondaNotInstalledError(ExternalToolNotInstalledError):
    """
    Trying to do something that requires the user to have
    the `conda` package manager installed.
    """

    def __init__(self) -> None:
        self.message = "Conda not found on $PATH. Is it installed?"
        super().__init__(self.message)


class EnvironmentAlreadyExistsError(PytoilException):
    """
    Trying to overwrite an existing environment, only applicable
    to conda environments.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class BadEnvironmentFileError(PytoilException):
    """
    The conda environment's `environment.yml` is malformed.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class EnvironmentDoesNotExistError(PytoilException):
    """
    Trying to do something to a virtual environment that does not
    exist.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class UnsupportedCondaInstallationError(PytoilException):
    """
    User's conda installation is not one of the supported
    ones for pytoil. See environments/conda.py.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class RepoNotFoundError(PytoilException):
    """
    The repo object trying to be operated on does not exist.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class GoNotInstalledError(ExternalToolNotInstalledError):
    """
    The user does not have `go` installed.
    """

    def __init__(self) -> None:
        self.message = "Go not found on $PATH. Is it installed?"
        super().__init__(self.message)


class CargoNotInstalledError(ExternalToolNotInstalledError):
    """
    The user does not have `cargo` installed.
    """

    def __init__(self) -> None:
        self.message = "Cargo not found on $PATH. Is it installed?"
        super().__init__(self.message)


class FlitNotInstalledError(ExternalToolNotInstalledError):
    """
    The user does not have `flit` installed.
    """

    def __init__(self) -> None:
        self.message = "Flit not found on $PATH. Is it installed?"
        super().__init__(self.message)


class PoetryNotInstalledError(ExternalToolNotInstalledError):
    """
    The user does not have `poetry` installed.
    """

    def __init__(self) -> None:
        self.message = "Poetry not found on $PATH. Is it installed?"
        super().__init__(self.message)
