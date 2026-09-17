import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import main


class TestMain(unittest.TestCase):
    def test_data_file_points_at_the_json_file(self):
        """Test that the app looks for record.json inside src/record."""
        self.assertTrue(main.DATA_FILE.endswith("record.json"))
        self.assertIn("record", Path(main.DATA_FILE).parts)

    def test_on_close_saves_then_destroys(self):
        """Test that closing saves the records and shuts the window."""
        root = MagicMock()
        manager = MagicMock()

        main.on_close(root, manager)

        manager.save.assert_called_once_with(main.DATA_FILE)
        root.destroy.assert_called_once_with()

    @patch('main.TravelRecordSystem')
    @patch('main.tk.Tk')
    @patch('main.RecordManager')
    def test_main_loads_the_saved_records(self, mock_manager_class,
                                          mock_tk, mock_gui):
        """Test that the records are loaded before the window opens."""
        manager = mock_manager_class.return_value

        main.main()

        manager.load.assert_called_once_with(main.DATA_FILE)

    @patch('main.TravelRecordSystem')
    @patch('main.tk.Tk')
    @patch('main.RecordManager')
    def test_main_gives_the_gui_the_same_manager(self, mock_manager_class,
                                                 mock_tk, mock_gui):
        """Test that the window is built with the manager that was loaded."""
        manager = mock_manager_class.return_value
        root = mock_tk.return_value

        main.main()

        mock_gui.assert_called_once_with(root, manager)
        root.mainloop.assert_called_once_with()

    @patch('main.TravelRecordSystem')
    @patch('main.tk.Tk')
    @patch('main.RecordManager')
    def test_main_registers_a_close_handler_that_saves(self,
                                                       mock_manager_class,
                                                       mock_tk, mock_gui):
        """Test that the registered close handler saves and destroys."""
        manager = mock_manager_class.return_value
        root = mock_tk.return_value

        main.main()

        name, handler = root.protocol.call_args[0]
        self.assertEqual(name, "WM_DELETE_WINDOW")

        handler()

        manager.save.assert_called_once_with(main.DATA_FILE)
        root.destroy.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
