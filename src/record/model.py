"""Record definitions and validation for the travel agent records system.

This module validates the fields belonging to a single record and
returns a cleaned dictionary, or raises RecordValidationError when
the supplied data is invalid.

It does not access the file system and does not inspect the complete
records list. Record relationships and business rules are handled by
the record manager.
"""

from datetime import datetime
from record.error import RecordValidationError


CLIENT = "Client"
AIRLINE = "Airline"
FLIGHT = "Flight"

RECORD_TYPES = (CLIENT, AIRLINE, FLIGHT)


# Fields belonging to each record type.
FIELDS = {
    CLIENT: (
        "Name",
        "AddressLine1",
        "AddressLine2",
        "AddressLine3",
        "City",
        "State",
        "ZipCode",
        "Country",
        "PhoneNumber",
    ),
    AIRLINE: (
        "CompanyName",
    ),
    FLIGHT: (
        "Client_ID",
        "Airline_ID",
        "Date",
        "StartCity",
        "EndCity",
    ),
}


# Fields that must not be left blank.
REQUIRED = {
    CLIENT: (
        "Name",
        "AddressLine1",
        "City",
        "ZipCode",
        "Country",
        "PhoneNumber",
    ),
    AIRLINE: (
        "CompanyName",
    ),
    FLIGHT: (
        "Client_ID",
        "Airline_ID",
        "Date",
        "StartCity",
        "EndCity",
    ),
}


# Fields that must hold positive whole numbers.
INT_FIELDS = {
    FLIGHT: (
        "Client_ID",
        "Airline_ID",
    )
}


# Accepted text formats for stored dates, tried in order.
DATE_FORMATS = (
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
)


def build_record(record_type: str, fields: dict) -> dict:
    """Validate fields and return a cleaned record dictionary."""

    check_type(record_type)

    validated_record = {
        "Type": record_type
    }

    for field in FIELDS[record_type]:
        value = fields.get(field, "")
        required = field in REQUIRED[record_type]

        if field in INT_FIELDS.get(record_type, ()):
            validated_record[field] = as_whole_number(value)

        elif field == "Date":
            validated_record[field] = as_date(value)

        else:
            validated_record[field] = as_text(
                value,
                required=required
            )

    return validated_record


def check_type(record_type: str) -> None:
    """Raise if record_type is not Client, Airline, or Flight."""

    if record_type not in RECORD_TYPES:
        raise RecordValidationError(
            f"Unknown record type: {record_type!r}"
        )


def as_text(value, required: bool = False) -> str:
    """Convert a value to cleaned text.

    None becomes an empty string. Other non-string values are converted
    using str(). Leading and trailing whitespace is removed.

    Raises:
        RecordValidationError: if the field is required and blank.
    """

    if value is None:
        value = ""
    elif not isinstance(value, str):
        value = str(value)

    value = value.strip()

    if required and value == "":
        raise RecordValidationError(
            "This field must not be empty"
        )

    return value


def as_whole_number(value) -> int:
    """Convert a value to a positive whole number.

    Values such as 4 and "4" are accepted.
    Blank values, words, zero, negative numbers, and decimals
    are rejected.

    Raises:
        RecordValidationError: if the value is not a positive integer.
    """

    if isinstance(value, bool):
        raise RecordValidationError(
            f"Must be a whole number, got {value!r}"
        )

    if isinstance(value, float):
        raise RecordValidationError(
            f"Must be a whole number, got {value!r}"
        )

    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise RecordValidationError(
            f"Must be a whole number, got {value!r}"
        ) from exc

    if number <= 0:
        raise RecordValidationError(
            f"Must be greater than 0, got {value!r}"
        )

    return number


def as_date(value) -> str:
    """Convert a value to a valid stored date string.

    Accepts datetime objects or text formatted as:
    YYYY-MM-DD
    YYYY-MM-DD HH:MM

    Raises:
        RecordValidationError: if the value is blank or invalid.
    """

    if isinstance(value, datetime):
        return value.strftime(DATE_FORMATS[0])

    text = as_text(value, required=True)

    for fmt in DATE_FORMATS:
        try:
            datetime.strptime(text, fmt)
            return text
        except ValueError:
            continue

    raise RecordValidationError(
        f"Date must be 'YYYY-MM-DD' or "
        f"'YYYY-MM-DD HH:MM', got {value!r}"
    )
