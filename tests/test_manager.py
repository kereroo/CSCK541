import pytest

from record.manager import RecordManager
from record.error import RecordError


@pytest.fixture
def manager():
    return RecordManager(records=[
        {"ID": 1, "Type": "Client", "Name": "Ahmad Al-Khatib",
         "AddressLine1": "Rainbow Street", "AddressLine2": "", "AddressLine3": "",
         "City": "Amman", "State": "", "ZipCode": "11118",
         "Country": "Jordan", "PhoneNumber": "0790000000"},
        {"ID": 1, "Type": "Airline", "CompanyName": "Royal Jordanian"},
        {"ID": 1, "Type": "Flight", "Client_ID": 1, "Airline_ID": 1,
         "Date": "2026-09-16", "StartCity": "Amman", "EndCity": "Dubai"},
    ])

def test_get_returns_existing_client(manager):
    record = manager.get("Client", 1)
    assert record["Name"] == "Ahmad Al-Khatib"


def test_get_accepts_string_id(manager):
    record = manager.get("Client", "1")
    assert record["Name"] == "Ahmad Al-Khatib"


def test_get_raises_when_id_not_found(manager):
    with pytest.raises(RecordError):
        manager.get("Client", 999)


def test_get_raises_when_type_invalid(manager):
    with pytest.raises(RecordError):
        manager.get("Hotel", 1)


def test_search_empty_query_returns_all_of_type(manager):
    results = manager.search("Client", "")
    assert len(results) == 1
    assert results[0]["Name"] == "Ahmad Al-Khatib"


def test_search_matches_case_insensitively(manager):
    results = manager.search("Client", "AHMAD")
    assert len(results) == 1


def test_search_matches_partial_text(manager):
    results = manager.search("Client", "Khatib")
    assert len(results) == 1


def test_search_no_match_returns_empty_list(manager):
    results = manager.search("Client", "Nonexistent")
    assert results == []


def test_search_only_returns_requested_type(manager):
    results = manager.search("Airline", "")
    assert all(record["Type"] == "Airline" for record in results)


def test_create_assigns_next_id(manager):
    fields = {
        "Name": "Layla Hassan",
        "AddressLine1": "King Abdullah St",
        "AddressLine2": "", "AddressLine3": "",
        "City": "Amman", "State": "", "ZipCode": "11183",
        "Country": "Jordan", "PhoneNumber": "0791111111",
    }
    record = manager.create("Client", fields)
    assert record["ID"] == 2


def test_create_increments_id_on_second_create(manager):
    fields = {
        "Name": "Layla Hassan",
        "AddressLine1": "King Abdullah St",
        "AddressLine2": "", "AddressLine3": "",
        "City": "Amman", "State": "", "ZipCode": "11183",
        "Country": "Jordan", "PhoneNumber": "0791111111",
    }
    manager.create("Client", fields)
    second = manager.create("Client", fields)
    assert second["ID"] == 3


def test_create_valid_flight_succeeds(manager):
    fields = {
        "Client_ID": 1, "Airline_ID": 1,
        "Date": "2026-10-01", "StartCity": "Amman", "EndCity": "Cairo",
    }
    record = manager.create("Flight", fields)
    assert record["StartCity"] == "Amman"


def test_create_flight_with_missing_client_raises(manager):
    fields = {
        "Client_ID": 999, "Airline_ID": 1,
        "Date": "2026-10-01", "StartCity": "Amman", "EndCity": "Cairo",
    }
    with pytest.raises(RecordError):
        manager.create("Flight", fields)


def test_create_invalid_type_raises(manager):
    with pytest.raises(RecordError):
        manager.create("Hotel", {})


def test_create_missing_required_field_raises(manager):
    fields = {
        "AddressLine1": "King Abdullah St",
        "City": "Amman", "ZipCode": "11183",
        "Country": "Jordan", "PhoneNumber": "0791111111",
        # "Name" left out on purpose
    }
    with pytest.raises(RecordError):
        manager.create("Client", fields)

def test_update_changes_specified_field(manager):
    updated = manager.update("Client", 1, {"City": "Zarqa"})
    assert updated["City"] == "Zarqa"


def test_update_keeps_unspecified_fields_unchanged(manager):
    updated = manager.update("Client", 1, {"City": "Zarqa"})
    assert updated["Name"] == "Ahmad Al-Khatib"
    assert updated["Country"] == "Jordan"


def test_update_ignores_attempt_to_change_id_and_type(manager):
    updated = manager.update("Client", 1, {"ID": 999, "Type": "Airline"})
    assert updated["ID"] == 1
    assert updated["Type"] == "Client"


def test_update_nonexistent_record_raises(manager):
    with pytest.raises(RecordError):
        manager.update("Client", 999, {"City": "Zarqa"})


def test_update_flight_with_missing_client_raises(manager):
    with pytest.raises(RecordError):
        manager.update("Flight", 1, {"Client_ID": 999})

def test_delete_removes_unreferenced_record(manager):
    deleted = manager.delete("Flight", 1)
    assert deleted["ID"] == 1
    with pytest.raises(RecordError):
        manager.get("Flight", 1)


def test_delete_blocked_when_referenced_by_flight(manager):
    with pytest.raises(RecordError):
        manager.delete("Client", 1)


def test_delete_nonexistent_record_raises(manager):
    with pytest.raises(RecordError):
        manager.delete("Client", 999)


def test_save_then_load_round_trip(manager, tmp_path):
    file_path = tmp_path / "records.json"
    manager.save(str(file_path))

    new_manager = RecordManager()
    new_manager.load(str(file_path))

    assert len(new_manager.records) == 3
    assert new_manager.get("Client", 1)["Name"] == "Ahmad Al-Khatib"


def test_load_missing_file_results_in_empty_list():
    new_manager = RecordManager()
    new_manager.load("this_file_does_not_exist.json")
    assert new_manager.records == []


def test_load_corrupted_file_results_in_empty_list(tmp_path):
    file_path = tmp_path / "bad.json"
    file_path.write_text("this is not valid json {{{")

    new_manager = RecordManager()
    new_manager.load(str(file_path))
    assert new_manager.records == []


def test_save_creates_file(manager, tmp_path):
    file_path = tmp_path / "records.json"
    manager.save(str(file_path))
    assert file_path.exists()

def test_create_valid_airline(manager):
    record = manager.create("Airline", {"CompanyName": "Emirates"})
    assert record["ID"] == 2
    assert record["CompanyName"] == "Emirates"


def test_update_airline_changes_company_name(manager):
    updated = manager.update("Airline", 1, {"CompanyName": "Qatar Airways"})
    assert updated["CompanyName"] == "Qatar Airways"


def test_delete_airline_blocked_when_referenced_by_flight(manager):
    with pytest.raises(RecordError):
        manager.delete("Airline", 1)