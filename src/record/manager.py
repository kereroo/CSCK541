"""Record manager for the travel agent records system.

Every record lives in one list here, along with the rules about them.

The GUI asks this class and shows what comes back. Storage only reads
and writes files.
"""

from record import model, storage
from record.error import RecordError

CLIENT = "Client"
AIRLINE = "Airline"
FLIGHT = "Flight"

RECORD_TYPES = (CLIENT, AIRLINE, FLIGHT)

# Flights get a "Type" key like the other two, so one list can hold all
# three and still tell them apart.
#
# Flights get an "ID" too. Without one there is no way to say which
# flight to update or delete.

# Which key on a flight points back at a client or an airline. Delete
# reads this to find the flights that would be left pointing at
# nothing, and create reads it to check a booking names real records.
FLIGHT_LINKS = {
    CLIENT: "Client_ID",
    AIRLINE: "Airline_ID",
}


class RecordManager:
    """Holds the records and does all the work on them."""

    def __init__(self, records=None):
        """Start a manager, optionally with records already in it.

        Tests pass a few fake records in, so they never need a file.
        """
        self.records: list = records if records is not None else []

        # Highest ID handed out so far for each type. Kept apart from
        # the records themselves so a deleted ID is never given out
        # again while the app is open.
        self._last_ids: dict = {}

    # Adding new records
    def create(self, record_type: str, fields: dict) -> dict:
        """Add a new record and return it.

        Pass the form values in fields. Leave the ID out, this works
        it out and fills it in.

        A flight is also checked against the client and the airline it
        names, so a booking can never be made against a record that
        isn't there.

        Raises:
            RecordError: unknown type, or a field is invalid.
        """
        self._check_type(record_type)

        record = model.build_record(record_type, fields)

        if record_type == FLIGHT:
            self._check_links(record)

        record = {"ID": self._next_id(record_type), **record}
        self.records.append(record)
        return record

    # Finding and reading records
    def get(self, record_type: str, record_id: int) -> dict:
        """Return one record, found by its ID.

        The GUI hands over whatever is in the form, so "4" is accepted
        as well as 4.

        Raises:
            RecordError: nothing of that type has that ID.
        """
        self._check_type(record_type)

        try:
            record_id = int(record_id)
        except (TypeError, ValueError):
            raise RecordError(f"{record_id!r} is not a valid ID") from None

        for record in self.records:
            if record["Type"] == record_type and record["ID"] == record_id:
                return record

        raise RecordError(f"{record_type} {record_id} not found")

    def search(self, record_type: str, query: str = "") -> list:
        """Return every record of a type that matches the query.

        Ignores case and accepts part of a word, so "lin" finds
        "Lincoln". An empty query returns the lot, which is how the GUI
        fills its table at startup.
        """
        self._check_type(record_type)

        found = [record for record in self.records
                 if record["Type"] == record_type]

        wanted = str(query).strip().lower()
        if not wanted:
            return found

        return [record for record in found
                if any(wanted in str(value).lower()
                       for value in record.values())]

    # Changing records
    def update(self, record_type: str, record_id: int, fields: dict) -> dict:
        """Change only the fields you pass in, and return the result.

        Anything you leave out keeps its old value. The ID and the Type
        never change.

        Raises:
            RecordError: record is missing, or a field is invalid.
        """
        existing = self.get(record_type, record_id)

        # Anything the caller sends for ID or Type is ignored rather
        # than rejected, so the GUI can hand back a whole row it read
        # out of the table without having to strip it first.
        changed = {key: value for key, value in fields.items()
                   if key not in ("ID", "Type")}

        record = model.build_record(record_type,
                                    {**existing, **changed})

        if record_type == FLIGHT:
            self._check_links(record)

        record = {"ID": existing["ID"], **record}
        self.records[self.records.index(existing)] = record
        return record

    # Removing records
    def delete(self, record_type: str, record_id: int) -> dict:
        """Remove a record and return the one removed.

        You cannot delete a client or airline while flights are booked
        against it, or those flights would point at nothing.

        Raises:
            RecordError: record is missing, or flights still refer to it.
        """
        record = self.get(record_type, record_id)

        booked = self._flights_for(record_type, record["ID"])
        if booked:
            raise RecordError(
                f"{record_type} {record['ID']} still has {len(booked)} "
                f"flight(s) booked against it"
            )

        self.records.remove(record)
        return record

    # Saving to the file and loading it back
    def load(self, path: str) -> None:
        """Fill the list from a file at startup.

        A missing or damaged file is not an error. The list stays empty
        and the app opens as normal.
        """
        try:
            self.records = storage.load_records(path)
        except (OSError, ValueError):
            self.records = []

        # IDs start again from whatever is in the file just loaded.
        self._last_ids = {}

    def save(self, path: str) -> None:
        """Write the whole list to a file at shutdown."""
        storage.save_records(self.records, path)

    # Small jobs, never called from the GUI
    def _next_id(self, record_type: str) -> int:
        """Return the highest ID of that type, plus one.

        Returns 1 when there are none. Old IDs never come back: delete
        client 3 and the next new client is still 4.
        """
        highest = max(
            [record["ID"] for record in self.records
             if record["Type"] == record_type]
            + [self._last_ids.get(record_type, 0)]
        )

        self._last_ids[record_type] = highest + 1
        return highest + 1

    def _flights_for(self, record_type: str, record_id: int) -> list:
        """Return the flights booked against a client or airline.

        Delete uses this to decide whether a record can go.
        """
        link = FLIGHT_LINKS.get(record_type)
        if link is None:
            return []

        return [record for record in self.records
                if record["Type"] == FLIGHT and record.get(link) == record_id]

    def _check_type(self, record_type: str) -> None:
        """Raise unless record_type is one of the three we handle."""
        if record_type not in RECORD_TYPES:
            raise RecordError(f"{record_type!r} is not a record type")

    def _check_links(self, flight: dict) -> None:
        """Raise unless the client and airline on a flight both exist.

        Calls get(), so the message the user sees is the same one they
        would get looking that client or airline up by hand.
        """
        for record_type, link in FLIGHT_LINKS.items():
            self.get(record_type, flight.get(link))
            
