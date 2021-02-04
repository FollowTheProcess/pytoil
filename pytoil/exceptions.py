"""
Custom exceptions for pytoil.

Author: Tom Fleet
Created: 04/02/2021
"""


class VirtualenvAlreadyExistsError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
