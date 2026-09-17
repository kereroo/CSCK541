import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from record.error import RecordError, RecordValidationError


class TestRecordError(unittest.TestCase):
    def test_record_error_is_an_exception(self):
        """Test that RecordError can be raised like any other exception."""
        with self.assertRaises(RecordError):
            raise RecordError("something went wrong")

    def test_validation_error_is_a_record_error(self):
        """Test that the validation error inherits from RecordError."""
        self.assertTrue(issubclass(RecordValidationError, RecordError))

    def test_catching_record_error_catches_validation_error(self):
        """Test that one except clause is enough to catch both."""
        with self.assertRaises(RecordError):
            raise RecordValidationError("Name value is required")

    def test_the_message_survives(self):
        """Test that the text given to the error reaches the GUI."""
        error = RecordValidationError("Name value is required")
        self.assertEqual(str(error), "Name value is required")


if __name__ == "__main__":
    unittest.main()
