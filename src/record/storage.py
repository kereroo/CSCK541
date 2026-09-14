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
    """Return True if a records file already exists at path.

        Manager can use this before attempting to load the file, for example
        to distinguish a first run from loading previously saved records.
    """
    return os.path.isfile(path)


def load_records(path: str) -> list:
    """Read the file at path and return the list of record dicts.

    Raises:
        FileNotFoundError: nothing exists at path.
        ValueError: the file exists but isn't a JSON list (corrupt or
            the wrong kind of file).
    """
    if not records_exist(path):
        raise FileNotFoundError(f"No records file at {path!r}")
    
    with open(path, "r", encoding="utf-8") as file:
        records = file.read()

    if not records.strip():
        return []
    try:
        data = json.loads(records)

    except json.JSONDecodeError as exc:
        raise ValueError(f"Records file at {path!r} is not valid JSON") from exc
    
    if not isinstance(data, list):
        raise ValueError(f"Records file at {path!r} is not a JSON list")
    
    return data



def save_records(records: list, path: str) -> None:
    """Write the whole records list to path.

    Writes to a temp file next to path first, then moves it into
    place, so a crash partway through a save can't corrupt the last
    good copy on disk.
    """
    dirname = os.path.dirname(path)

    if dirname and not os.path.isdir(dirname):
        os.makedirs(dirname, exist_ok=True)

    temp_path = path + TMP_SUFFIX

    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False)

    os.replace(temp_path, path)
