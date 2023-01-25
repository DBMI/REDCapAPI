"""
Module test_redcap_class.py, which exists to support automated
testing of the REDCapInterface class.

Classes
-------
TestREDCap
"""
from datetime import datetime

import pandas
import pytest
from tests.utilities import convert_to_date

from redcap_api import REDCapInterface


def test_bulk_record_retrieval():
    """
    Test retrieving ALL records.

    Return
    ------
    bool
    """
    redcap_interface_object = REDCapInterface(isdev=True, timeout_sec=240)
    retrieved_df = redcap_interface_object.retrieve()
    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned: int = retrieved_df.shape[0]
    assert num_elements_returned > 2
    assert "dob" in retrieved_df.columns

    # Bulk mode won't work in expanded mode--insufficient memory.


def test_create_one_record(fake_record):
    """
    Test creating ONE record.

    Return
    ------
    bool
    """
    redcap_interface_object = REDCapInterface(isdev=True)
    assert not redcap_interface_object.create(None)
    assert not redcap_interface_object.create("should not work")
    next_study_id = redcap_interface_object.next_record_number()
    fake_record["study_id"] = next_study_id
    assert redcap_interface_object.create(fake_record)
    test_df = pandas.DataFrame([fake_record], index=[next_study_id])
    assert redcap_interface_object.create(test_df)


def test_create_multiple_records(fake_record):
    """
    Test creating SEVERAL records.

    Return
    ------
    bool
    """
    redcap_interface_object = REDCapInterface(isdev=True)
    num_records_to_create = 3
    success = True

    for __ in range(num_records_to_create):
        next_study_id = redcap_interface_object.next_record_number()
        fake_record["study_id"] = next_study_id
        success &= redcap_interface_object.create(fake_record)

    assert success


def test_date_conversion():
    """
    Test converting strings to dates.

    Return
    ------
    bool
    """
    date_value_true = datetime.strptime("31/01/1970", "%d/%m/%Y")
    datetime_value_true = datetime.strptime("31/01/1970 12:05:10", "%d/%m/%Y %H:%M:%S")

    date_string_test = "01/31/1970"
    date_string_converted = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test = "01/31/70"
    date_string_converted = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test = "01-31-1970"
    date_string_converted = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test = "01-31-70"
    date_string_converted = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test = "70-01-31"
    date_string_converted = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test = "1970-01-31 12:05:10"
    date_string_converted = convert_to_date(date_string_test)
    assert date_string_converted == datetime_value_true

    date_string_test = "1970-01-31"
    date_string_converted = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test = "31 Jan 1970"
    date_string_converted = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test = "Jan 31 1970"
    date_string_converted = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test = "Jan 31, 1970"
    date_string_converted = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    date_string_test = "Jan 31 1970 12:00AM"
    date_string_converted = convert_to_date(date_string_test)
    assert date_string_converted == date_value_true

    # Cases we expect to return None.
    date_string_test = ""
    date_string_converted = convert_to_date(date_string_test)
    assert date_string_converted is None

    date_string_test = "text only"
    date_string_converted = convert_to_date(date_string_test)
    assert date_string_converted is None

    date_string_test = "1234 cannot be parsed"
    date_string_converted = convert_to_date(date_string_test)
    assert date_string_converted is None


def test_delete_record(known_fake_record_number):
    """
    Test deleting one record.

    Return
    ------
    bool
    """
    redcap_interface_object = REDCapInterface(isdev=True)
    last_record_number = redcap_interface_object.last_record_number(
        except_for=known_fake_record_number
    )

    if last_record_number is None or last_record_number <= 0:  # pragma: no cover
        raise Exception("Unable to find any records I'm allowed to delete.")

    assert redcap_interface_object.delete(last_record_number)

    # Ensure calling "delete" with no record number returns None.
    assert not redcap_interface_object.delete(None)


def test_exists():
    """
    Test method for querying whether given record is present.

    Return
    ------
    bool
    """
    redcap_interface_object = REDCapInterface(isdev=True)
    last_record_number = redcap_interface_object.last_record_number()
    assert redcap_interface_object.exists(last_record_number)

    # Case that should result in False.
    assert not redcap_interface_object.exists(-1)

    # Cases that should throw exception.
    with pytest.raises(TypeError):
        assert not redcap_interface_object.exists(None)

    with pytest.raises(TypeError):
        redcap_interface_object.exists("should throw error")


def test_last_record_number(known_fake_record_number):
    """
    Test method for looking up highest used record number.

    Return
    ------
    bool
    """
    redcap_interface_object = REDCapInterface(isdev=True)
    last_valid_number = redcap_interface_object.last_record_number()
    assert isinstance(last_valid_number, int)
    last_valid_number = redcap_interface_object.last_record_number(
        except_for=known_fake_record_number
    )
    assert isinstance(last_valid_number, int)

    # Force method to look past the first guess (next number - 1).
    last_valid_number = redcap_interface_object.last_record_number(
        except_for=last_valid_number
    )
    assert isinstance(last_valid_number, int)

    # Multiple values
    last_valid_number = redcap_interface_object.last_record_number(number_desired=2)
    assert isinstance(last_valid_number, list)
    assert len(last_valid_number) == 2


def test_multiple_record_retrieval():
    """
    Test retrieving SEVERAL records.

    Return
    ------
    bool
    """
    redcap_interface_object = REDCapInterface(isdev=True)
    two_valid_numbers = redcap_interface_object.last_record_number(number_desired=2)
    retrieved_df = redcap_interface_object.retrieve(two_valid_numbers)
    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned: int = retrieved_df.shape[0]
    assert num_elements_returned == 2
    assert "dob" in retrieved_df.columns

    # Expanded mode.
    retrieved_df = redcap_interface_object.retrieve(
        record_numbers=two_valid_numbers, expanded_record=True
    )
    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned: int = retrieved_df.shape[0]
    assert num_elements_returned == 2
    assert "meeting_notes" in retrieved_df.columns


def test_next_record_number():
    """
    Test method for determining which is next unused record number.

    Return
    ------
    bool
    """
    redcap_interface_object = REDCapInterface(isdev=True)
    next_number = redcap_interface_object.next_record_number()
    assert isinstance(next_number, int)


def test_object_instantiation(api_version_string):
    """
    Test creating REDCapInterface object.

    Return
    ------
    bool
    """
    #   This is the ONLY time in testing that we'll instantiate a REDCapInterface object
    #    WITHOUT the isdev flag set. It's to ensure we CAN read the production token.
    production_redcap_interface_object = REDCapInterface(isdev=False)
    assert isinstance(production_redcap_interface_object, REDCapInterface)
    version_number = production_redcap_interface_object.version()
    assert version_number == api_version_string

    #   We'll use the isdev = True flag to specify we want to talk to the DEV database.
    redcap_interface_object = REDCapInterface(isdev=True)
    assert isinstance(redcap_interface_object, REDCapInterface)
    version_number = redcap_interface_object.version()
    assert version_number == api_version_string


def test_single_record_retrieval():
    """
    Test retrieving ONE record.

    Return
    ------
    bool
    """
    redcap_interface_object = REDCapInterface(isdev=True)
    last_record_number = redcap_interface_object.last_record_number()
    retrieved_df = redcap_interface_object.retrieve(last_record_number)
    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned: int = retrieved_df.shape[0]
    assert num_elements_returned == 1
    assert "dob" in retrieved_df.columns

    retrieved_df = redcap_interface_object.retrieve("should not work")
    assert isinstance(retrieved_df, pandas.DataFrame)
    assert len(retrieved_df) == 0

    with pytest.raises(RuntimeError):
        redcap_interface_object.retrieve(-1)

    # Test expanded mode.
    retrieved_df = redcap_interface_object.retrieve(
        record_numbers=last_record_number, expanded_record=True
    )

    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned: int = retrieved_df.shape[0]
    assert num_elements_returned == 1
    assert "meeting_notes" in retrieved_df.columns


def test_update_record(known_fake_record_number):
    """
    Test updating given record.

    Return
    ------
    bool
    """
    redcap_interface_object = REDCapInterface(isdev=True)
    last_record_number = redcap_interface_object.last_record_number(
        except_for=known_fake_record_number
    )

    if last_record_number is None or last_record_number <= 0:  # pragma: no cover
        raise Exception("Unable to find any records I'm allowed to update.")

    right_now = datetime.now()
    right_now_string = datetime.strftime(right_now, "%Y-%m-%d")
    new_info = {
        "study_id": str(last_record_number),
        "date_of_last_activity": right_now_string,
    }
    # Test with dictionary as input.
    assert redcap_interface_object.update(new_info)

    # Check that the date_of_last_activity field was really updated.
    updated_record = redcap_interface_object.retrieve(last_record_number)
    assert updated_record is not None
    assert isinstance(updated_record, pandas.DataFrame)
    assert "date_of_last_activity" in updated_record
    retrieved_datestring = updated_record["date_of_last_activity"][0]
    assert right_now_string == retrieved_datestring

    # Test again with dataframe input.
    right_now_string = datetime.strftime(right_now, "%Y-%m-%d")
    new_info = {
        "study_id": str(last_record_number),
        "date_of_last_activity": right_now_string,
    }
    new_info_df = pandas.DataFrame(data=new_info, index=[0])
    assert redcap_interface_object.update(new_info_df)

    # Check that the date_of_last_activity field was really updated.
    updated_record = redcap_interface_object.retrieve(last_record_number)
    assert updated_record is not None
    assert isinstance(updated_record, pandas.DataFrame)
    assert "date_of_last_activity" in updated_record
    retrieved_datestring = updated_record["date_of_last_activity"][0]
    assert right_now_string == retrieved_datestring

    # Test inputs that should raise errors.
    with pytest.raises(TypeError):
        redcap_interface_object.update("should throw error")

    # What if the attempted update can't be inserted? Ensure
    new_info["this_column_does_not_exist"] = "this won't work"
    new_info_df = pandas.DataFrame(data=new_info, index=[0])

    with pytest.raises(RuntimeError) as error_raised:
        redcap_interface_object.update(new_info_df)
        assert "Unable to update; original record was restored." == str(
            error_raised.value
        )
