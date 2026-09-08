"""Record definitions for the travel agent records system.

Each function here checks one record's fields and hands back a clean
dict, or raises if something is wrong. Manager calls these before it
ever adds a record to the list, so bad data never gets that far.

Models never touch the file system and never see the full records
list - they only ever look at the one dict of fields they're given.
"""

from datetime import datetime

CLIENT = "Client"
AIRLINE = "Airline"
FLIGHT = "Flight"
RECORD_TYPES = (CLIENT, AIRLINE, FLIGHT)

# Which fields belong to each record type, and which of those must not
# be left blank. Manager's create/update both need this same list, so
# it lives here rather than in two places.
FIELDS = {
    CLIENT: (
        "Name", "AddressLine1", "AddressLine2", "AddressLine3",
        "City", "State", "ZipCode", "Country", "PhoneNumber",
    ),
    AIRLINE: ("CompanyName",),
    FLIGHT: ("Client_ID", "Airline_ID", "Date", "StartCity", "EndCity"),
}

REQUIRED = {
    CLIENT: ("Name", "AddressLine1", "City", "ZipCode", "Country", "PhoneNumber"),
    AIRLINE: ("CompanyName",),
    FLIGHT: ("Client_ID", "Airline_ID", "Date", "StartCity", "EndCity"),
}

# Fields that must hold a whole number rather than free text.
INT_FIELDS = {
    FLIGHT: ("Client_ID", "Airline_ID"),
}


class RecordValidationError(ValueError):
    """Raised when a field is missing, empty, or the wrong shape.

    Manager catches this the same way it catches its own RecordError,
    so the GUI shows one kind of message either way.
    """


# Building and checking one record
def build_record(record_type: str, fields: dict) -> dict:
    """Validate fields and return the validated record dictionary."""

    check_type(record_type)

    validate = {
        "Type": record_type
    }

    for field in FIELDS[record_type]:
        value = fields.get(field, "")

        if field in INT_FIELDS.get(record_type, ()):
            # TODO: validate and convert whole-number fields
            pass

        elif field == "Date":
            # TODO: validate and format the date
            pass

        else:
            # TODO: validate text fields
            pass

    return validate


def check_type(record_type: str) -> None:
    """Raise if record_type isn't one of Client/Airline/Flight."""
    raise NotImplementedError("TODO")


# Field-level checks, shared by build_record for every type
def as_text(value, required: bool = False) -> str:
    """Turn value into a string, optionally rejecting it if blank.

    None becomes "". Numbers and other non-string values are
    converted with str(value) rather than rejected outright.
    """
    raise NotImplementedError("TODO")


def as_whole_number(value) -> int:
    """Turn value into an int, or raise if it can't be.

    The GUI always hands over text, so "4" must work as well as 4.
    "" and "four" must not.
    """
    raise NotImplementedError("TODO")


def as_date(value) -> str:
    """Turn value into a stored date string, or raise if it can't be.

    Accepts a datetime object (converted to a string) or already-
    formatted text in "YYYY-MM-DD" or "YYYY-MM-DD HH:MM". Anything
    else is rejected, since it can't safely go into JSON either way.
    """
    raise NotImplementedError("TODO")