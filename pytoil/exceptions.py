class PytoilException(Exception):
    """
    Base pytoil exception from which all subclasses
    must inherit.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class GitNotInstalledError(PytoilException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class CodeNotInstalledError(PytoilException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class MissingInterpreterError(PytoilException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class CondaNotInstalledError(PytoilException):
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


class GoNotInstalledError(PytoilException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class CargoNotInstalledError(PytoilException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
