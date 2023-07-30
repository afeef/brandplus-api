from abc import ABC

from app.domain.repositories import __all__ as abstract_classes


class RepositoryException(Exception):
    def __init__(self, message, *errors):
        Exception.__init__(self, message)
        self.message = message
        self.errors = errors


class Repository(*abstract_classes, ABC):
    pass
