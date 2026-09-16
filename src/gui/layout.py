import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from src.record.manager import RecordManager
from src.record.error import RecordError


class TravelRecordSystem:
    def __init__(self, root, manager):
        self.root = root
        self.manager = manager
        self.root.title("Specialist Travel Agent - Record Management System")
        self.root.geometry("1100x600")
        self.root.minsize(900, 500)

        # Hook window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Instance-level dictionaries for global access across methods
        self.entries = {}
        self.trees = {}

        # Apply standard theme
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')

        # Create Notebook (Tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Define tabs
        self.tab_clients = ttk.Frame(self.notebook)
        self.tab_flights = ttk.Frame(self.notebook)
        self.tab_airlines = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_clients, text="👥 Client Records")
        self.notebook.add(self.tab_flights, text="✈️ Flight Records")
        self.notebook.add(self.tab_airlines, text="🏢 Airline Records")

        # Define form and tree fields for each entity
        client_form_fields = ["Name", "Address Line 1", "City", "Zip Code", "Country", "Phone Number"]
        client_tree_fields = ["ID"] + client_form_fields

        flight_form_fields = ["Client_ID", "Airline_ID", "Date", "Start City", "End City"]
        flight_tree_fields = ["ID"] + flight_form_fields

        airline_form_fields = ["Company Name"]
        airline_tree_fields = ["ID"] + airline_form_fields

        # Build layouts dynamically
        self.build_crud_layout(self.tab_clients, "Client", client_form_fields, client_tree_fields)
        self.build_crud_layout(self.tab_flights, "Flight", flight_form_fields, flight_tree_fields)
        self.build_crud_layout(self.tab_airlines, "Airline", airline_form_fields, airline_tree_fields)

        # Populate tables with initial data
        for entity in ["Client", "Flight", "Airline"]:
            self.refresh(entity)

    def build_crud_layout(self, parent_frame, entity_name, form_fields, tree_fields):
        """Generates layout with a Form on the left and a Data Table on the right."""
        self.entries[entity_name] = {}

        # --- LEFT PANEL: Form and Buttons ---
        left_panel = ttk.LabelFrame(parent_frame, text=f"Manage {entity_name}s", padding=(10, 10))
        left_panel.pack(side="left", fill="y", padx=10, pady=10)

        for idx, field in enumerate(form_fields):
            lbl = ttk.Label(left_panel, text=f"{field}:")
            lbl.grid(row=idx, column=0, padx=5, pady=10, sticky="e")

            ent = ttk.Entry(left_panel, width=25)
            ent.grid(row=idx, column=1, padx=5, pady=10, sticky="w")

            self.entries[entity_name][field] = ent

        # Button Frame
        btn_frame = ttk.Frame(left_panel)
        btn_frame.grid(row=len(form_fields), column=0, columnspan=2, pady=20)

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

        tree_scroll = ttk.Scrollbar(right_panel)
        tree_scroll.pack(side="right", fill="y")

        tree = ttk.Treeview(right_panel, columns=tree_fields, show="headings", yscrollcommand=tree_scroll.set)
        self.trees[entity_name] = tree

        for field in tree_fields:
            tree.heading(field, text=field)
            tree.column(field, width=120, anchor="center")

        tree.pack(side="left", fill="both", expand=True)
        tree_scroll.config(command=tree.yview)

        tree.bind("<<TreeviewSelect>>", lambda e, en=entity_name: self.on_select(en))

    def refresh(self, entity_name, records=None):
        """Refreshes the Treeview table with new or search-filtered records."""
        tree = self.trees[entity_name]
        tree.delete(*tree.get_children())
        if records is None:
            records = self.manager.search(entity_name, "")
        for record in records:
            tree.insert("", "end", values=[record.get(f, "") for f in tree.cget("columns")])

    def on_select(self, entity_name):
        """Fills form entries with data from selected Treeview row."""
        tree = self.trees[entity_name]
        selected_item = tree.selection()

        if not selected_item:
            return

        item_values = tree.item(selected_item[0], 'values')
        tree_fields = tree.cget("columns")

        self.clear_form(entity_name)

        for field, value in zip(tree_fields, item_values):
            if field in self.entries[entity_name]:
                self.entries[entity_name][field].insert(0, str(value))

    def clear_form(self, entity_name):
        """Clears all form entries for an entity."""
        for entry in self.entries[entity_name].values():
            entry.delete(0, tk.END)

    def handle_action(self, action, entity_name):
        """Executes CRUD commands against RecordManager and updates UI."""
        values = {field: entry.get().strip() for field, entry in self.entries[entity_name].items()}
        tree = self.trees[entity_name]

        try:
            if action == "Create":
                self.manager.create(entity_name, values)
                self.clear_form(entity_name)
                self.refresh(entity_name)

            elif action == "Update":
                selected = tree.selection()
                if not selected:
                    raise RecordError("Please select a record from the table to update.")
                record_id = tree.item(selected[0], 'values')[0]
                self.manager.update(entity_name, record_id, values)
                self.clear_form(entity_name)
                self.refresh(entity_name)

            elif action == "Delete":
                selected = tree.selection()
                if not selected:
                    raise RecordError("Please select a record from the table to delete.")
                record_id = tree.item(selected[0], 'values')[0]
                self.manager.delete(entity_name, record_id)
                self.clear_form(entity_name)
                self.refresh(entity_name)

            elif action == "Search":
                query = " ".join(val for val in values.values() if val).strip()
                results = self.manager.search(entity_name, query)
                self.refresh(entity_name, records=results)

        except RecordError as exc:
            messagebox.showerror("Error", str(exc))

    def on_close(self):
        """Destroys UI window on exit (file saving is handled in main.py)."""
        self.root.destroy()


def main():
    app_root = tk.Tk()
    app_manager = RecordManager()
    TravelRecordSystem(app_root, app_manager)
    app_root.mainloop()


if __name__ == "__main__":
    main()