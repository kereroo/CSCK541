import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Constants
DATA_PATH = "travel_records.dat"


# --- Dummy backend classes to ensure the script runs ---
class RecordError(Exception):
    """Custom exception raised by RecordManager operations."""
    pass


class RecordManager:
    """Mock manager to simulate backend operations."""

    def create(self, entity, values):
        pass  # Add real creation logic here

    def update(self, entity, values):
        pass  # Add real update logic here

    def delete(self, entity, values):
        pass  # Add real delete logic here

    def search(self, entity, values):
        pass  # Add real search logic here

    @staticmethod
    def save(path):
        print(f"Data saved to {path} successfully.")


# --------------------------------------------------------


class TravelRecordSystem:
    def __init__(self, root, manager):
        self.root = root
        self.manager = manager  # Passed manager argument saved to instance
        self.root.title("Specialist Travel Agent - Record Management System")
        self.root.geometry("1100x600")
        self.root.minsize(900, 500)

        # Hook the window close event to save before exiting
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Instance-level dictionaries for global access across methods
        self.entries = {}
        self.trees = {}

        # Apply a cleaner theme available in standard tkinter
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')

        # Create a Notebook (Tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Define the tabs
        self.tab_clients = ttk.Frame(self.notebook)
        self.tab_flights = ttk.Frame(self.notebook)
        self.tab_airlines = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_clients, text="👥 Client Records")
        self.notebook.add(self.tab_flights, text="✈️ Flight Records")
        self.notebook.add(self.tab_airlines, text="🏢 Airline Records")

        # Define the fields for each entity

        # Clients (Client_ID auto-generated, so we omit it from the form but keep it in the Treeview)
        client_form_fields = ["Name", "Address Line 1", "Address Line 2",
                              "Address Line 3", "City", "State", "Zip Code",
                              "Country", "Phone Number"]
        client_tree_fields = ["Client_ID"] + client_form_fields

        # Flights
        flight_fields = ["Client_ID", "Airline_ID", "Date", "Start City", "End City"]

        # Airlines
        airline_fields = ["Airline_ID", "Company Name", "Country of Origin", "Contact Number"]

        # Build the layouts dynamically using a reusable method
        self.build_crud_layout(self.tab_clients, "Client", client_form_fields, client_tree_fields)
        self.build_crud_layout(self.tab_flights, "Flight", flight_fields, flight_fields)
        self.build_crud_layout(self.tab_airlines, "Airline", airline_fields, airline_fields)

    def build_crud_layout(self, parent_frame, entity_name, form_fields, tree_fields):
        """
        A reusable function to generate the layout for any given record type.
        Creates a Form on the left and a Data Table on the right.
        """
        # Initialize dictionaries for this specific entity
        self.entries[entity_name] = {}

        # --- LEFT PANEL: Form and Buttons ---
        left_panel = ttk.LabelFrame(parent_frame, text=f"Manage {entity_name}s", padding=(10, 10))
        left_panel.pack(side="left", fill="y", padx=10, pady=10)

        # Dynamically generate form labels and entry boxes based on the form_fields list
        for idx, field in enumerate(form_fields):
            lbl = ttk.Label(left_panel, text=f"{field}:")
            lbl.grid(row=idx, column=0, padx=5, pady=10, sticky="e")

            ent = ttk.Entry(left_panel, width=25)
            ent.grid(row=idx, column=1, padx=5, pady=10, sticky="w")

            # Store in instance dict
            self.entries[entity_name][field] = ent

        # Button Frame (Placed directly below the form)
        btn_frame = ttk.Frame(left_panel)
        btn_frame.grid(row=len(form_fields), column=0, columnspan=2, pady=20)

        # CRUD Buttons mapped to wrapped handlers
        btn_width = 12
        ttk.Button(btn_frame, text="➕ Create", width=btn_width,
                   command=lambda e=entity_name: self.handle_action("Create", e)).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="🔍 Search", width=btn_width,
                   command=lambda e=entity_name: self.handle_action("Search", e)).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="✏️ Update", width=btn_width,
                   command=lambda e=entity_name: self.handle_action("Update", e)).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="❌ Delete", width=btn_width,
                   command=lambda e=entity_name: self.handle_action("Delete", e)).grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(btn_frame, text="🧹 Clear Form",
                   command=lambda e=entity_name: self.clear_form(e)).grid(row=2, column=0, columnspan=2,
                                                                          sticky="ew", padx=5, pady=5)

        # --- RIGHT PANEL: Data Table (Treeview) ---
        right_panel = ttk.LabelFrame(parent_frame, text=f"{entity_name} Database", padding=(10, 10))
        right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Treeview Scrollbar
        tree_scroll = ttk.Scrollbar(right_panel)
        tree_scroll.pack(side="right", fill="y")

        # Treeview (Table) using tree_fields (which might contain IDs auto-generated)
        tree = ttk.Treeview(right_panel, columns=tree_fields, show="headings", yscrollcommand=tree_scroll.set)

        # Save tree to instance dictionary so it can be accessed globally
        self.trees[entity_name] = tree

        # Configure columns and headings dynamically
        for field in tree_fields:
            tree.heading(field, text=field)
            tree.column(field, width=120, anchor="center")

        tree.pack(side="left", fill="both", expand=True)
        tree_scroll.config(command=tree.yview)

        # Bind the row selection event to populate the form
        tree.bind("<<TreeviewSelect>>", lambda e, en=entity_name: self.on_select(en))

        # (Optional) Insert some dummy data to show how it looks
        tree.insert("", "end", values=["Placeholder"] * len(tree_fields))

    def on_select(self, entity_name):
        """Fills the form with data from the clicked row in the Treeview."""
        tree = self.trees[entity_name]
        selected_item = tree.selection()

        if not selected_item:
            return

        # Get row data and column headings
        item_values = tree.item(selected_item[0], 'values')
        tree_fields = tree.cget("columns")

        self.clear_form(entity_name)

        # Repopulate the inputs
        for field, value in zip(tree_fields, item_values):
            if field in self.entries[entity_name]:
                self.entries[entity_name][field].insert(0, str(value))

    def clear_form(self, entity_name):
        """Clears all entry fields in the form for a specific entity."""
        for entry in self.entries[entity_name].values():
            entry.delete(0, tk.END)

    def handle_action(self, action, entity_name):
        """Wraps manager interactions with UI try/except blocks to prevent crashes."""
        # Grab current values from the relevant form dictionary
        values = {field: entry.get() for field, entry in self.entries[entity_name].items()}

        try:
            if action == "Create":
                self.manager.create(entity_name, values)
            elif action == "Update":
                self.manager.update(entity_name, values)
            elif action == "Delete":
                self.manager.delete(entity_name, values)
            elif action == "Search":
                self.manager.search(entity_name, values)

        except RecordError as exc:
            # Show a tidy pop-up dialog instead of letting the application crash
            messagebox.showerror("Error", str(exc))

    def on_close(self):
        """Hook called when the 'X' button is clicked to close the app."""
        self.manager.save(DATA_PATH)
        self.root.destroy()


def main():
    """Main entry point mapped to prevent variable scope shadowing."""
    app_root = tk.Tk()

    # Initialize our dummy manager and pass it to the UI
    app_manager = RecordManager()

    # Instantiate the UI (no need to assign it to an unused variable)
    TravelRecordSystem(app_root, app_manager)

    app_root.mainloop()


if __name__ == "__main__":
    main()