class PytoilException(Exception):
    """
    Base pytoil exception from which all subclasses
    must inherit.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ExternalToolNotInstalledException(PytoilException):
    """
    Base exception for any child exception responsible
    for raising in the presence of a required external
    tool that's not installed.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class GitNotInstalledError(ExternalToolNotInstalledException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class CodeNotInstalledError(ExternalToolNotInstalledException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class MissingInterpreterError(PytoilException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class CondaNotInstalledError(ExternalToolNotInstalledException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class EnvironmentAlreadyExistsError(PytoilException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class BadEnvironmentFileError(PytoilException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class EnvironmentDoesNotExistError(PytoilException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class UnsupportedCondaInstallationError(PytoilException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class RepoNotFoundError(PytoilException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class GoNotInstalledError(ExternalToolNotInstalledException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class CargoNotInstalledError(ExternalToolNotInstalledException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class FlitNotInstalledError(ExternalToolNotInstalledException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class PoetryNotInstalledError(ExternalToolNotInstalledException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
