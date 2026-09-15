"""Start the travel agent records system.

The app reads whatever was saved last time before opening the window,
and writes the records back when the user closes it.
"""

import os
import tkinter as tk

from gui.layout import TravelRecordSystem
from record.manager import RecordManager

# Where the records are kept. The path comes from this file's own
# location, so the app looks in the same place whether it starts from
# the project root or from inside src.
DATA_FILE = os.path.join(os.path.dirname(__file__), "record", "record.json")


def main() -> None:
    """Load the saved records and open the window."""
    manager = RecordManager()

    # A first run has no file yet. The manager starts empty and the
    # window opens anyway.
    manager.load(DATA_FILE)

    root = tk.Tk()
    TravelRecordSystem(root, manager)

    # Registered after the window is built, so this replaces the
    # handler the GUI sets for itself. Loading and saving then live in
    # one file.
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root, manager))

    root.mainloop()


def on_close(root, manager) -> None:
    """Write the records back, then shut the window."""
    manager.save(DATA_FILE)
    root.destroy()


if __name__ == "__main__":
    main()
