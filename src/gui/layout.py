import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class TravelRecordSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Specialist Travel Agent - Record Management System")
        self.root.geometry("1100x600")
        self.root.minsize(900, 500)

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
        client_fields = ["Client ID", "First Name", "Last Name", "Email", "Phone", "Passport No."]
        flight_fields = ["Flight No.", "Origin", "Destination", "Departure Date", "Arrival Date", "Airline ID"]
        airline_fields = ["Airline ID", "Airline Name", "Country of Origin", "Contact Number"]

        # Build the layouts dynamically using a reusable method
        self.build_crud_layout(self.tab_clients, "Client", client_fields)
        self.build_crud_layout(self.tab_flights, "Flight", flight_fields)
        self.build_crud_layout(self.tab_airlines, "Airline", airline_fields)

    def build_crud_layout(self, parent_frame, entity_name, fields):
        """
        A reusable function to generate the layout for any given record type.
        Creates a Form on the left and a Data Table on the right.
        """
        # --- LEFT PANEL: Form and Buttons ---
        left_panel = ttk.LabelFrame(parent_frame, text=f"Manage {entity_name}s", padding=(10, 10))
        left_panel.pack(side="left", fill="y", padx=10, pady=10)

        # Dictionary to store the entry widgets so we can get their data later
        entries = {}

        # Dynamically generate form labels and entry boxes based on the fields list
        for idx, field in enumerate(fields):
            lbl = ttk.Label(left_panel, text=f"{field}:")
            lbl.grid(row=idx, column=0, padx=5, pady=10, sticky="e")

            ent = ttk.Entry(left_panel, width=25)
            ent.grid(row=idx, column=1, padx=5, pady=10, sticky="w")
            entries[field] = ent

        # Button Frame (Placed directly below the form)
        btn_frame = ttk.Frame(left_panel)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)

        # CRUD Buttons
        btn_width = 12
        ttk.Button(btn_frame, text="➕ Create", width=btn_width,
                   command=lambda: self.dummy_action("Create", entity_name)).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="🔍 Search", width=btn_width,
                   command=lambda: self.dummy_action("Search", entity_name)).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="✏️ Update", width=btn_width,
                   command=lambda: self.dummy_action("Update", entity_name)).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="❌ Delete", width=btn_width,
                   command=lambda: self.dummy_action("Delete", entity_name)).grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(btn_frame, text="🧹 Clear Form", command=lambda: self.clear_form(entries)).grid(row=2, column=0,
                                                                                                  columnspan=2,
                                                                                                  sticky="ew", padx=5,
                                                                                                  pady=5)

        # --- RIGHT PANEL: Data Table (Treeview) ---
        right_panel = ttk.LabelFrame(parent_frame, text=f"{entity_name} Database", padding=(10, 10))
        right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Treeview Scrollbar
        tree_scroll = ttk.Scrollbar(right_panel)
        tree_scroll.pack(side="right", fill="y")

        # Treeview (Table)
        tree = ttk.Treeview(right_panel, columns=fields, show="headings", yscrollcommand=tree_scroll.set)

        # Configure columns and headings dynamically
        for field in fields:
            tree.heading(field, text=field)
            tree.column(field, width=120, anchor="center")

        tree.pack(side="left", fill="both", expand=True)
        tree_scroll.config(command=tree.yview)

        # (Optional) Insert some dummy data to show how it looks
        tree.insert("", "end", values=["Placeholder"] * len(fields))

    def clear_form(self, entries_dict):
        """Clears all entry fields in the given form."""
        for entry in entries_dict.values():
            entry.delete(0, tk.END)

    def dummy_action(self, action, entity):
        """Placeholder method for button clicks."""
        messagebox.showinfo("Action Triggered",
                            f"{action} action triggered for {entity} record.\n\nYou will need to wire this up to your database/backend logic!")


if __name__ == "__main__":
    root = tk.Tk()
    app = TravelRecordSystem(root)
    root.mainloop()