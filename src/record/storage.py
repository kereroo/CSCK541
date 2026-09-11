"""File system persistence for the travel agent records system.

Storage only ever reads and writes files. It knows nothing about what
a valid Client or Flight looks like - that's models' job. It knows
nothing about IDs or business rules - that's manager's job. It only
ever sees the whole records list, never one record on its own.
"""

import json
import os

# Records are written to a temp file first, then moved into place, so
# a crash mid-save leaves the old file intact rather than a half
# written one. This is the suffix used for that temp file.
TMP_SUFFIX = ".tmp"


def records_exist(path: str) -> bool:
    """Return True if a records file is already sitting at path.

    Manager's load() can check this before trying to read, though
    load_records() below is also safe to call on a path that doesn't
    exist - it's here mainly so the app can decide "first run" vs
    "loading saved data" if that distinction ever matters to the GUI.
    """
    raise NotImplementedError("TODO")


def load_records(path: str) -> list:
    """Read the file at path and return the list of record dicts.

    Raises:
        FileNotFoundError: nothing exists at path.
        ValueError: the file exists but isn't a JSON list (corrupt or
            the wrong kind of file). Manager.load() catches both of
            these and starts with an empty list instead of crashing.
    """
    raise NotImplementedError("TODO")


def save_records(records: list, path: str) -> None:
    """Write the whole records list to path.

    Writes to a temp file next to path first, then moves it into
    place, so a crash partway through a save can't corrupt the last
    good copy on disk.
    """
    raise NotImplementedError("TODO")