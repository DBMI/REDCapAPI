"""
Module test_redcap_class.py, which exists to support automated
testing of the REDCapInterface class.

Classes
-------
TestREDCap
"""
import json
from datetime import datetime

import pandas
import pytest

from redcapapi import DataRequest, REDCapInterface
from tests.utilities import convert_to_date


def test_create_one_record(
    requests_mock,
    url,
    known_fake_record,
    fake_next_record,
    fake_ok_response,
    fake_record_dict,
):
    """
    Test creating ONE record.
    """
    ##  Register the mock URI, HTTP method, JSON payload, and status code
    ##  to support the internal method __known_test_record_present(),
    ##  which is called by __init__ method.
    requests_mock.post(url, json=known_fake_record)
    redcap_interface_object: REDCapInterface = REDCapInterface(
        isdev=True, test_mode=True
    )
    assert isinstance(redcap_interface_object, REDCapInterface)
    #
    #   Exercise next_record_number()
    #
    requests_mock.post(url, json=fake_next_record, status_code=200)
    next_study_id: int = redcap_interface_object.next_record_number()
    assert isinstance(next_study_id, int)
    assert next_study_id == fake_next_record
    #
    #   Create record from dict object.
    #
    requests_mock.post(url, json=fake_next_record, status_code=200)
    assert redcap_interface_object.create(fake_record_dict)

    # Create record from pandas.DataFrame object.
    test_df: pandas.DataFrame = pandas.DataFrame(
        [fake_record_dict], index=[next_study_id]
    )
    assert redcap_interface_object.create(test_df)


def test_create_multiple_records(
    requests_mock, url, known_fake_record, fake_next_record, fake_records_dataframe
):
    """
    Test creating SEVERAL records simultaneously.
    """
    requests_mock.post(url, json=known_fake_record)
    redcap_interface_object = REDCapInterface(isdev=True, test_mode=True)
    requests_mock.post(url, json=fake_next_record, status_code=200)
    assert redcap_interface_object.create(fake_records_dataframe)


def test_convert_dates():
    """
    Test converting strings to dates.
    """
    date_value_true: datetime = datetime.strptime("31/01/1970", "%d/%m/%Y")
    datetime_value_true: datetime = datetime.strptime(
        "31/01/1970 12:05:10", "%d/%m/%Y %H:%M:%S"
    )

    date_string_test: str = "01/31/1970"
    date_string_converted: datetime = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test: str = "01/31/70"
    date_string_converted: datetime = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test: str = "01-31-1970"
    date_string_converted: datetime = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test: str = "01-31-70"
    date_string_converted: datetime = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test: str = "70-01-31"
    date_string_converted: datetime = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test: str = "1970-01-31 12:05:10"
    date_string_converted: datetime = convert_to_date(date_string_test)
    assert date_string_converted == datetime_value_true

    date_string_test: str = "1970-01-31"
    date_string_converted: datetime = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test: str = "31 Jan 1970"
    date_string_converted: datetime = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test: str = "Jan 31 1970"
    date_string_converted: datetime = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test: str = "Jan 31, 1970"
    date_string_converted: datetime = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test: str = "Jan 31 1970 12:00AM"
    date_string_converted: datetime = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    # Cases we expect to return None.
    date_string_test: str = ""
    date_string_converted: datetime = convert_to_date(date_string_test)
    assert date_string_converted is None

    date_string_test: str = "text only"
    date_string_converted: datetime = convert_to_date(date_string_test)
    assert date_string_converted is None

    date_string_test: str = "1234 cannot be parsed"
    date_string_converted: datetime = convert_to_date(date_string_test)
    assert date_string_converted is None


def test_delete_record(
    requests_mock,
    url,
    known_fake_record,
    fake_next_record_pair,
    known_fake_record_number,
):
    """
    Test deleting one record.
    """
    requests_mock.post(url, json=known_fake_record, status_code=200)
    redcap_interface_object: REDCapInterface = REDCapInterface(
        isdev=True, test_mode=True
    )
    requests_mock.post(url, fake_next_record_pair)
    last_record_number = redcap_interface_object.last_record_number(
        except_for=known_fake_record_number
    )

    if last_record_number is None or last_record_number <= 0:  # pragma: no cover
        raise Exception("Unable to find any records I'm allowed to delete.")

    assert redcap_interface_object.delete(last_record_number)

    # Ensure calling "delete" with no record number returns None.
    assert not redcap_interface_object.delete(None)


def test_exists(
    requests_mock, url, known_fake_record, fake_next_record_pair, fake_missing_record
):
    """
    Test method for querying whether given record is present.
    """
    requests_mock.post(url, json=known_fake_record, status_code=200)
    redcap_interface_object: REDCapInterface = REDCapInterface(
        isdev=True, test_mode=True
    )
    requests_mock.post(url, fake_next_record_pair)
    last_record_number: int = redcap_interface_object.last_record_number()
    requests_mock.post(url, json=known_fake_record, status_code=200)
    assert redcap_interface_object.exists(last_record_number)

    # Case that should result in False.
    requests_mock.post(url, json=fake_missing_record, status_code=400)
    assert not redcap_interface_object.exists(-1)

    # Cases that should throw exception.
    with pytest.raises(TypeError):
        assert not redcap_interface_object.exists(None)

    with pytest.raises(TypeError):
        redcap_interface_object.exists("should throw error")


def test_last_record_number(
    requests_mock,
    url,
    known_fake_record,
    fake_next_record_pair,
    known_fake_record_number,
    fake_next_record_triple,
):
    """
    Test method for looking up highest used record number.
    """
    requests_mock.post(url, json=known_fake_record, status_code=200)
    redcap_interface_object: REDCapInterface = REDCapInterface(
        isdev=True, test_mode=True
    )
    requests_mock.post(url, fake_next_record_pair)
    last_valid_number = redcap_interface_object.last_record_number()
    assert isinstance(last_valid_number, int)
    requests_mock.post(url, fake_next_record_pair)
    last_valid_number = redcap_interface_object.last_record_number(
        except_for=known_fake_record_number
    )
    assert isinstance(last_valid_number, int)

    # Force method to look past the first guess (next number - 1).
    requests_mock.post(url, fake_next_record_triple)
    last_valid_number = redcap_interface_object.last_record_number(
        except_for=last_valid_number
    )
    assert isinstance(last_valid_number, int)

    # Multiple values
    requests_mock.post(url, fake_next_record_triple)
    last_valid_number = redcap_interface_object.last_record_number(number_desired=2)
    assert isinstance(last_valid_number, list)
    assert len(last_valid_number) == 2


def test_report(requests_mock, url, known_fake_record, fake_records_dataframe):
    redcap_interface_object: REDCapInterface = REDCapInterface(
        isdev=False, timeout_sec=240, test_mode=True
    )

    json_string: str = fake_records_dataframe.to_json(orient='records')
    parsed_data: list[dict] = json.loads(json_string)
    requests_mock.post(url, json=parsed_data, status_code=200)
    retrieved_df: pandas.DataFrame = redcap_interface_object.report(report_id=1234)
    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned: int = retrieved_df.shape[0]
    assert num_elements_returned > 1
    assert "contact_1_date_time" in retrieved_df.columns


def test_retrieve_all_records(requests_mock, url, known_fake_record, fake_records_dataframe):
    """
    Test retrieving ALL records.
    """
    requests_mock.post(url, json=known_fake_record, status_code=200)
    redcap_interface_object: REDCapInterface = REDCapInterface(
        isdev=False, timeout_sec=240, test_mode=True
    )

    json_string: str = fake_records_dataframe.to_json(orient='records')
    parsed_data: list[dict] = json.loads(json_string)
    requests_mock.post(url, json=parsed_data, status_code=200)
    retrieved_df = redcap_interface_object.retrieve()
    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned: int = retrieved_df.shape[0]
    assert num_elements_returned > 2
    assert "dob" in retrieved_df.columns

    # Bulk mode won't work in expanded mode--insufficient memory.


def test_retrieve_multiple_records(requests_mock, url, known_fake_record, fake_next_record_pair, fake_records_dataframe):
    """
    Test retrieving SEVERAL records.
    """
    requests_mock.post(url, json=known_fake_record, status_code=200)
    redcap_interface_object: REDCapInterface = REDCapInterface(
        isdev=True, test_mode=True
    )
    requests_mock.post(url, fake_next_record_pair)
    two_valid_numbers = redcap_interface_object.last_record_number(number_desired=2)

    just_two_records: pandas.DataFrame = fake_records_dataframe.iloc[[0, 1]]
    json_string: str = just_two_records.to_json(orient='records')
    parsed_data: list[dict] = json.loads(json_string)
    requests_mock.post(url, json=parsed_data, status_code=200)
    retrieved_df = redcap_interface_object.retrieve(two_valid_numbers)

    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned: int = retrieved_df.shape[0]
    assert num_elements_returned == 2
    assert "dob" in retrieved_df.columns

    # Expanded mode.
    retrieved_df = redcap_interface_object.retrieve(
        record_numbers=two_valid_numbers, data_request=DataRequest.Expanded
    )
    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned: int = retrieved_df.shape[0]
    assert num_elements_returned == 2
    assert "meeting_notes" in retrieved_df.columns


def test_retrieve_single_record(requests_mock, url, known_fake_record, fake_next_record_pair, fake_missing_record, fake_records_dataframe):
    """
    Test retrieving ONE record.
    """
    requests_mock.post(url, json=known_fake_record, status_code=200)
    redcap_interface_object: REDCapInterface = REDCapInterface(
        isdev=True, test_mode=True
    )
    requests_mock.post(url, fake_next_record_pair)
    last_record_number:int = redcap_interface_object.last_record_number()
    retrieved_df: pandas.DataFrame = redcap_interface_object.retrieve(last_record_number)
    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned: int = retrieved_df.shape[0]
    assert num_elements_returned == 1
    assert "dob" in retrieved_df.columns

    retrieved_df = redcap_interface_object.retrieve("should not work")
    assert isinstance(retrieved_df, pandas.DataFrame)
    assert len(retrieved_df) == 0

    requests_mock.post(url, json=fake_missing_record, status_code=400)
    retrieved_df = redcap_interface_object.retrieve(-1)
    assert isinstance(retrieved_df, pandas.DataFrame)
    assert len(retrieved_df) == 0

    # Test expanded mode.
    just_one_record: pandas.DataFrame = fake_records_dataframe.iloc[[0]]
    json_string: str = just_one_record.to_json(orient='records')
    parsed_data: list[dict] = json.loads(json_string)
    requests_mock.post(url, json=parsed_data, status_code=200)
    retrieved_df = redcap_interface_object.retrieve(
        record_numbers=last_record_number, data_request=DataRequest.Expanded
    )
    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned: int = retrieved_df.shape[0]
    assert num_elements_returned == 1
    assert "meeting_notes" in retrieved_df.columns

    # Test "Velos" mode.
    retrieved_df = redcap_interface_object.retrieve(
        record_numbers=last_record_number, data_request=DataRequest.Velos
    )

    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned: int = retrieved_df.shape[0]
    assert num_elements_returned == 1
    assert "entered_velos___yes" in retrieved_df.columns
