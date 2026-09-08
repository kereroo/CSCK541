"""Record manager for the travel agent records system.

Every record lives in one list here, along with the rules about them.

The GUI asks this class and shows what comes back. Storage only reads
and writes files.
"""

CLIENT = "Client"
AIRLINE = "Airline"
FLIGHT = "Flight"

RECORD_TYPES = (CLIENT, AIRLINE, FLIGHT)

# Flights get a "Type" key like the other two, so one list can hold all
# three and still tell them apart.
#
# Flights get an "ID" too. Without one there is no way to say which
# flight to update or delete.


class RecordError(Exception):
    """Raised when a request cannot be carried out.

    The GUI catches it and shows the message, so the user reads
    "Client 4 not found" instead of the app closing.
    """


class RecordManager:
    """Holds the records and does all the work on them."""

    def __init__(self, records=None):
        """Start a manager, optionally with records already in it.

        Tests pass a few fake records in, so they never need a file.
        """
        self.records: list = records if records is not None else []

    # Adding new records
    def create(self, record_type: str, fields: dict) -> dict:
        """Add a new record and return it.

        Pass the form values in fields. Leave the ID out, this works
        it out and fills it in.

        Raises:
            RecordError: unknown type, or a field is invalid.
        """
        raise NotImplementedError("TODO: Kyle")

    # Finding and reading records
    def get(self, record_type: str, record_id: int) -> dict:
        """Return one record, found by its ID.

        Raises:
            RecordError: nothing of that type has that ID.
        """
        raise NotImplementedError("TODO: Kyle")

    def search(self, record_type: str, query: str = "") -> list:
        """Return every record of a type that matches the query.

        Ignores case and accepts part of a word, so "lin" finds
        "Lincoln". An empty query returns the lot, which is how the GUI
        fills its table at startup.
        """
        raise NotImplementedError("TODO: Kyle")

    # Changing records
    def update(self, record_type: str, record_id: int, fields: dict) -> dict:
        """Change only the fields you pass in, and return the result.

        Anything you leave out keeps its old value. The ID and the Type
        never change.

        Raises:
            RecordError: record is missing, or a field is invalid.
        """
        raise NotImplementedError("TODO: Kyle")

    # Removing records
    def delete(self, record_type: str, record_id: int) -> dict:
        """Remove a record and return the one removed.

        You cannot delete a client or airline while flights are booked
        against it, or those flights would point at nothing.

        Raises:
            RecordError: record is missing, or flights still refer to it.
        """
        raise NotImplementedError("TODO: Kyle")

    # Saving to the file and loading it back
    def load(self, path: str) -> None:
        """Fill the list from a file at startup.

        A missing or damaged file is not an error. The list stays empty
        and the app opens as normal.
        """
        raise NotImplementedError("TODO: Kyle, calls storage.load")

    def save(self, path: str) -> None:
        """Write the whole list to a file at shutdown."""
        raise NotImplementedError("TODO: Kyle, calls storage.save")

    # Small jobs, never called from the GUI
    def _next_id(self, record_type: str) -> int:
        """Return the highest ID of that type, plus one.

        Returns 1 when there are none. Old IDs never come back: delete
        client 3 and the next new client is still 4.
        """
        raise NotImplementedError("TODO: Kyle")

    def _flights_for(self, record_type: str, record_id: int) -> list:
        """Return the flights booked against a client or airline.

        Delete uses this to decide whether a record can go.
        """
        raise NotImplementedError("TODO: Kyle")
    