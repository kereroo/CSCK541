# Travel agent record management system

A desktop application for a specialist travel agent. It holds three kinds
of record: clients, airlines, and the flights that link the two. The user
creates, updates, searches and deletes them all through a window.

CSCK541 end of module assignment, University of Liverpool.

## Requirements

Python 3.11 or newer, with tkinter. Install dependencies with:

```
pip install -r requirements.txt
```

Most Python installations include tkinter already. On Debian or Ubuntu it
is a separate package:

```
sudo apt install python3-tk
```

## Running it

From the project root:

```
python src/main.py
```

The app reads `src/record/record.json` on start up and writes it back
when you close the window. A first run has no file yet, so the app opens
with an empty list and creates the file when you close it.

## Running the tests

From the project root:

```
pytest
```

## Records

Every record is a dictionary in one list. The app assigns the `ID`, and
`Type` says which of the three kinds a record is.

**Client**

`Name`, `AddressLine1`, `AddressLine2`, `AddressLine3`, `City`, `State`,
`ZipCode`, `Country`, `PhoneNumber`

**Airline**

`CompanyName`

**Flight**

`Client_ID`, `Airline_ID`, `Date`, `StartCity`, `EndCity`

The brief gives flights neither an `ID` nor a `Type`. We added both.
Without a `Type` one list cannot tell the three kinds apart, and without
an `ID` there is no way to say which flight to update or delete.

## Layout

```
src/
    main.py             starts the app, loads on open and saves on close
    gui/
        layout.py       the window, the forms and the tables
    record/
        manager.py      the list of records and the rules about them
        model.py        field validation for each record type
        storage.py      reading and writing the JSON file
        error.py        the exceptions the other modules raise
        record.json     where the records are kept
tests/                  unit tests
docs/                   report and meeting minutes
```

The GUI only ever talks to `RecordManager`. Storage never sees a single
record on its own, and models never touch the file system, so each module
can be tested without the other two.

## Rules

IDs are never reused. Delete client 3 and the next new client is 4.

A client or airline cannot be deleted while flights are booked against
it, and a flight cannot be created against a client or airline that does
not exist.

Search ignores case and matches part of a word, so "lin" finds
"Lincoln". An empty search returns everything.

A missing or damaged data file is not an error. The list stays empty and
the app opens as normal.
