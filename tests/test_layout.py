import sys
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from gui.layout import TravelRecordSystem
from record.error import RecordError

class TestTravelRecordSystem(unittest.TestCase):
    def setUp(self):
        """Set up a mock RecordManager and a Tkinter root for testing."""
        self.root = tk.Tk()
        # Hide the main window during tests
        self.root.withdraw() 

        self.manager = MagicMock()
        self.manager.search.return_value = []

        self.app = TravelRecordSystem(self.root, self.manager)

    def tearDown(self):
        """Destroy the Tkinter root after tests."""
        self.root.destroy()

    def test_tab_creation(self):
        """Test that tabs are created for the given entities."""
        self.assertEqual(len(self.app.notebook.tabs()), 3)

    def test_create_call(self):
        """Test that the create action calls the manager's create method."""
        self.app.entries["Airline"]["CompanyName"].insert(0, "Test Airline")
        self.app.handle_action("Create", "Airline")
        self.manager.create.assert_called_once_with("Airline", {"CompanyName": "Test Airline"})

    def test_refresh_populates_table(self):
        """Test that the refresh method populates the treeview with records."""
        self.manager.search.return_value = [{"ID": "1", "CompanyName": "Test Airline"}]
        self.app.refresh("Airline")

        tree = self.app.trees["Airline"]
        row_ids = tree.get_children()
        self.assertEqual(tree.item(row_ids[0])['values'], ([1, "Test Airline"]))

    def test_clear_form_clears_entries(self):
        """Test that the clear_form method clears all entry fields."""
        self.app.entries["Airline"]["CompanyName"].insert(0, "Test Airline")
        self.app.clear_form("Airline")
        self.assertEqual(self.app.entries["Airline"]["CompanyName"].get(), "")

    def test_handle_action_update_without_selection(self):
        """Test that an error is raised when trying to update without selecting a record."""
        with patch('tkinter.messagebox.showerror') as mock_showerror:
            self.app.handle_action("Update", "Airline")
            mock_showerror.assert_called_once_with("Error", "Please select a record from the table to update.")

    def test_handle_action_deletion_without_selection(self):
        """Test that an error is raised when trying to delete without selecting a record"""
        with patch('tkinter.messagebox.showerror') as mock_showerror:
            self.app.handle_action("Delete", "Airline")
            mock_showerror.assert_called_once_with("Error", "Please select a record from the table to delete.")

    def test_handle_action_search_from_filled_form(self):
        """Test that search joins non-empty values"""
        self.app.entries["Client"]["Name"].insert(0, "Lucy")
        self.app.entries["Client"]["City"].insert(0, "Dublin")

        self.app.handle_action("Search", "Client")

        self.manager.search.assert_called_with("Client", "Lucy Dublin")

    def test_handle_action_search_empty_field(self):
        """Test that search with blank form returns an empty string"""
        self.app.handle_action("Search", "Client")

        self.manager.search.assert_called_with("Client", "")

    def test_show_error_on_record_error(self):
        """Test that RecordError is raise durin Create"""
        self.manager.create.side_effect = RecordError("Name value is required")

        with patch('tkinter.messagebox.showerror') as mock_showerror:
            self.app.handle_action("Create", "Airline")
            mock_showerror.assert_called_once_with("Error", "Name value is required")

    def selection_simulator(self, name, values):
        """Helper to add a row and select it"""
        tree = self.app.trees[name]
        row_id = tree.insert("", "end", values=values)
        tree.selection_set(row_id)
        return row_id

    def test_update_call_uses_selected_id(self):
        """Test that Update sends selected row's ID and current values"""
        self.selection_simulator("Airline", ["0", "Old Airline"])
        self.app.entries["Airline"]["CompanyName"].insert(0, "New Name")
        self.app.handle_action("Update", "Airline")

        self.manager.update.assert_called_once_with("Airline", "0", {"CompanyName": "New Name"})
    
    def test_delete_call_uses_selected_id(self):
        """Test that Delete sends selected row's ID and current values"""
        self.selection_simulator("Airline", ["5", "Old Airline"])

        self.app.handle_action("Delete", "Airline")

        self.manager.delete.assert_called_once_with("Airline", "5")

if __name__ == "__main__":
    unittest.main()