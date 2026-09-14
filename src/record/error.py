"""Shared exceptions for the travel agent records system."""


class RecordError(Exception):
    """Base exception for record-related errors."""


class RecordValidationError(RecordError):
    """Raised when record data is missing, invalid, or incorrectly formatted."""
    