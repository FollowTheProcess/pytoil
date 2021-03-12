"""
Custom exceptions for pytoil.

Author: Tom Fleet
Created: 04/02/2021
"""


class VirtualenvAlreadyExistsError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class VirtualenvDoesNotExistError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class InvalidConfigError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class GitNotInstalledError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class CondaNotInstalledError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class LocalRepoExistsError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class RepoNotFoundError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class MissingInterpreterError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class BadEnvironmentFileError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class InvalidURLError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class InvalidRepoPathError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class CodeNotInstalledError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class UnknownCondaInstallationError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
