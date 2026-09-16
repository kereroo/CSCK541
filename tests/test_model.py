import pytest
from datetime import datetime

from record.model import build_record, check_type, as_text, as_whole_number, as_date
from record.error import RecordValidationError


def test_check_type_accepts_client():
    check_type("Client")


def test_check_type_accepts_airline():
    check_type("Airline")


def test_check_type_accepts_flight():
    check_type("Flight")


def test_check_type_rejects_lowercase():
    with pytest.raises(RecordValidationError):
        check_type("client")


def test_check_type_rejects_unknown_type():
    with pytest.raises(RecordValidationError):
        check_type("Hotel")



def test_as_text_strips_whitespace():
    assert as_text("  hello  ") == "hello"


def test_as_text_converts_none_to_empty_string():
    assert as_text(None) == ""


def test_as_text_converts_non_string_to_string():
    assert as_text(42) == "42"


def test_as_text_required_and_blank_raises():
    with pytest.raises(RecordValidationError):
        as_text("", required=True)


def test_as_text_required_and_filled_does_not_raise():
    assert as_text("hello", required=True) == "hello"


def test_as_text_not_required_and_blank_returns_empty_string():
    assert as_text("", required=False) == ""



def test_as_whole_number_accepts_positive_int():
    assert as_whole_number(4) == 4


def test_as_whole_number_accepts_numeric_string():
    assert as_whole_number("4") == 4


def test_as_whole_number_rejects_zero():
    with pytest.raises(RecordValidationError):
        as_whole_number(0)


def test_as_whole_number_rejects_negative():
    with pytest.raises(RecordValidationError):
        as_whole_number(-3)


def test_as_whole_number_rejects_decimal():
    with pytest.raises(RecordValidationError):
        as_whole_number(4.5)


def test_as_whole_number_rejects_boolean():
    with pytest.raises(RecordValidationError):
        as_whole_number(True)


def test_as_whole_number_rejects_non_numeric_string():
    with pytest.raises(RecordValidationError):
        as_whole_number("four")


def test_as_date_accepts_date_only_string():
    assert as_date("2026-09-16") == "2026-09-16"


def test_as_date_accepts_date_and_time_string():
    assert as_date("2026-09-16 14:30") == "2026-09-16 14:30"


def test_as_date_accepts_datetime_object():
    assert as_date(datetime(2026, 9, 16)) == "2026-09-16"


def test_as_date_rejects_blank_string():
    with pytest.raises(RecordValidationError):
        as_date("")


def test_as_date_rejects_malformed_string():
    with pytest.raises(RecordValidationError):
        as_date("16/09/2026")

def test_build_record_valid_client():
    fields = {
        "Name": "Ahmad Al-Khatib",
        "AddressLine1": "Rainbow Street",
        "AddressLine2": "",
        "AddressLine3": "",
        "City": "Amman",
        "State": "",
        "ZipCode": "11118",
        "Country": "Jordan",
        "PhoneNumber": "0790000000",
    }
    record = build_record("Client", fields)
    assert record["Type"] == "Client"
    assert record["Name"] == "Ahmad Al-Khatib"
    assert record["City"] == "Amman"


def test_build_record_valid_airline():
    record = build_record("Airline", {"CompanyName": "Royal Jordanian"})
    assert record["Type"] == "Airline"
    assert record["CompanyName"] == "Royal Jordanian"


def test_build_record_valid_flight():
    fields = {
        "Client_ID": "1",
        "Airline_ID": "2",
        "Date": "2026-09-16",
        "StartCity": "Amman",
        "EndCity": "Dubai",
    }
    record = build_record("Flight", fields)
    assert record["Type"] == "Flight"
    assert record["Client_ID"] == 1
    assert record["Airline_ID"] == 2
    assert record["Date"] == "2026-09-16"


def test_build_record_rejects_unknown_type():
    with pytest.raises(RecordValidationError):
        build_record("Hotel", {})


def test_build_record_missing_required_field_raises():
    fields = {
        "AddressLine1": "Rainbow Street",
        "City": "Amman",
        "ZipCode": "11118",
        "Country": "Jordan",
        "PhoneNumber": "0790000000",
        # "Name" left out on purpose
    }
    with pytest.raises(RecordValidationError):
        build_record("Client", fields)


def test_build_record_missing_optional_field_defaults_to_empty_string():
    fields = {
        "Name": "Ahmad Al-Khatib",
        "AddressLine1": "Rainbow Street",
        "City": "Amman",
        "ZipCode": "11118",
        "Country": "Jordan",
        "PhoneNumber": "0790000000",
        # AddressLine2 and AddressLine3 left out — both optional
    }
    record = build_record("Client", fields)
    assert record["AddressLine2"] == ""
    assert record["AddressLine3"] == ""