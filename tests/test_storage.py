import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add the src directory to sys.path so we can import storage
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from record import storage

class StorageTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a temporary directory and file paths for testing."""
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)

        self.non_existent_file = self.tmp_path / 'non-existent.json'
        self.test_file = self.tmp_path / 'test.json'
        self.test_file.write_text('[]')

    def tearDown(self):
        """Clean up the temporary directory after tests."""
        self.tmp_dir.cleanup()

    def test_records_exist(self):
        """Test if it correctly identifies existing and non-existing files."""
        self.assertFalse(storage.records_exist(str(self.non_existent_file)))
        self.assertTrue(storage.records_exist(str(self.test_file)))

    def test_load_records_success(self):
        """Test loading records from a file that exists and contains valid JSON."""
        records = [{"id": 1, "name": "Test Record"}]
        self.test_file.write_text(json.dumps(records))
        loaded_records = storage.load_records(str(self.test_file))
        self.assertEqual(loaded_records, records)

    def test_load_records_file_not_found(self):
        """Test loading records from a file that does not exist."""
        with self.assertRaises(FileNotFoundError):
            storage.load_records(str(self.non_existent_file))

    def test_load_records_non_json(self):
        """Test loading records from a file that exists but is not valid JSON."""
        invalid_json_file = self.tmp_path / 'invalid.txt'
        invalid_json_file.write_text("This is not a JSON file.")

        with self.assertRaises(ValueError) as context:
            storage.load_records(str(invalid_json_file))
        self.assertIn("is not valid JSON", str(context.exception))

    def test_load_records_non_list_json(self):
        """Test loading records from a file that exists and is valid JSON but not a list."""
        non_list_json = "This is a valid JSON string but not a list."
        test_json_file = self.tmp_path / 'test.json'
        test_json_file.write_text(json.dumps(non_list_json))

        with self.assertRaises(ValueError) as context:
            storage.load_records(str(test_json_file))
        self.assertIn("is not a JSON list", str(context.exception))


    def test_save_records(self):
        """Test saving records to a file and verify the contents."""
        records = [{"id": 1, "name": "Test Record"}]
        path = str(self.tmp_path / 'test_records.json')

        storage.save_records(records, str(path))

        # Verify that the file was created and contains the correct data
        loaded_records = json.loads(Path(path).read_text())
        self.assertEqual(loaded_records, records)

if __name__ == '__main__':  
    unittest.main()