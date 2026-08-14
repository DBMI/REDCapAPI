"""
Module test_redcap_class.py, which exists to support automated
testing of the REDCapInterface class.

Classes
-------
TestREDCap
"""
import pandas
import pytest

from helpers import (
    api_version_string,
    fake_record_dict,
    fake_records_dataframe,
    known_fake_record_number,
)
from src.redcapapi import DataRequest, REDCapInterface


def exercise_create_one_record():
    """
    Test creating ONE record.
    """
    redcap_interface_object: REDCapInterface = REDCapInterface(isdev=True)

    # Some corner cases.
    assert not redcap_interface_object.create(None)
    assert not redcap_interface_object.create("should not work")

    # Create from dict object.
    assert redcap_interface_object.create(fake_record_dict())

    # Create from pandas.DataFrame object.
    next_study_id: int = redcap_interface_object.next_record_number()
    test_df: pandas.DataFrame = pandas.DataFrame(
        [fake_record_dict()], index=[next_study_id]
    )
    assert redcap_interface_object.create(test_df)


def exercise_create_multiple_records():
    """
    Test creating SEVERAL records simultaneously.
    """
    redcap_interface_object: REDCapInterface = REDCapInterface(isdev=True)
    assert redcap_interface_object.create(fake_records_dataframe())


def exercise_delete_record():
    """
    Test deleting one record.
    """
    redcap_interface_object: REDCapInterface = REDCapInterface(isdev=True)
    last_record_number: int = redcap_interface_object.last_record_number(
        except_for=known_fake_record_number()
    )

    if last_record_number is None or last_record_number <= 0:  # pragma: no cover
        raise Exception("Unable to find any records I'm allowed to delete.")

    assert redcap_interface_object.delete(last_record_number)

    # Ensure calling "delete" with no record number returns None.
    assert not redcap_interface_object.delete(None)


def exercise_exists():
    """
    Test method for querying whether given record is present.
    """
    redcap_interface_object: REDCapInterface = REDCapInterface(isdev=True)
    last_record_number: int = redcap_interface_object.last_record_number()
    assert redcap_interface_object.exists(last_record_number)

    # Case that should result in False.
    assert not redcap_interface_object.exists(-1)

    # Cases that should throw exception.
    with pytest.raises(TypeError):
        assert not redcap_interface_object.exists(None)

    with pytest.raises(TypeError):
        redcap_interface_object.exists("should throw error")


def exercise_instantiate_object():
    """
    Test creating REDCapInterface object.
    """
    #   This is the ONLY time in testing that we'll instantiate a REDCapInterface object
    #    WITHOUT the isdev flag set. It's to ensure we CAN read the production token.
    production_redcap_interface_object: REDCapInterface = REDCapInterface(isdev=False)
    assert isinstance(production_redcap_interface_object, REDCapInterface)
    version_number: str = production_redcap_interface_object.version()
    assert version_number == api_version_string()

    #   We'll use the isdev = True flag to specify we want to talk to the DEV database.
    redcap_interface_object: REDCapInterface = REDCapInterface(isdev=True)
    assert isinstance(redcap_interface_object, REDCapInterface)
    version_number = redcap_interface_object.version()
    assert version_number == api_version_string()


def exercise_last_record_number():
    """
    Test method for looking up highest used record number.
    """
    redcap_interface_object: REDCapInterface = REDCapInterface(isdev=True)
    last_valid_number: int = redcap_interface_object.last_record_number()
    assert isinstance(last_valid_number, int)
    last_valid_number = redcap_interface_object.last_record_number(
        except_for=known_fake_record_number()
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


def exercise_next_record_number():
    """
    Test method for determining which is next unused record number.

    Return
    ------
    bool
    """
    redcap_interface_object: REDCapInterface = REDCapInterface(isdev=True)
    next_number: int = redcap_interface_object.next_record_number()
    assert isinstance(next_number, int)


def exercise_report():
    redcap_interface_object: REDCapInterface = REDCapInterface(
        isdev=False, timeout_sec=240
    )
    retrieved_df: pandas.DataFrame = redcap_interface_object.report(report_id=16322)
    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned: int = retrieved_df.shape[0]
    assert num_elements_returned > 10000
    assert "contact_1_date_time" in retrieved_df.columns


def exercise_retrieve_all_records():
    """
    Test retrieving ALL records.
    """
    redcap_interface_object: REDCapInterface = REDCapInterface(
        isdev=False, timeout_sec=240
    )
    retrieved_df: pandas.DataFrame = redcap_interface_object.retrieve()
    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned: int = retrieved_df.shape[0]
    assert num_elements_returned > 2
    assert "dob" in retrieved_df.columns

    # Bulk mode won't work in expanded mode--insufficient memory.


def exercise_retrieve_multiple_records():
    """
    Test retrieving SEVERAL records.
    """
    redcap_interface_object: REDCapInterface = REDCapInterface(isdev=True)
    two_valid_numbers: list = redcap_interface_object.last_record_number(
        number_desired=2
    )
    retrieved_df: pandas.DataFrame = redcap_interface_object.retrieve(two_valid_numbers)
    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned: int = retrieved_df.shape[0]
    assert num_elements_returned == 2
    assert "dob" in retrieved_df.columns

    # Expanded mode.
    retrieved_df = redcap_interface_object.retrieve(
        record_numbers=two_valid_numbers, data_request=DataRequest.Expanded
    )
    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned = retrieved_df.shape[0]
    assert num_elements_returned == 2
    assert "meeting_notes" in retrieved_df.columns


def exercise_retrieve_single_record():
    """
    Test retrieving ONE record.
    """
    redcap_interface_object: REDCapInterface = REDCapInterface(isdev=True)
    last_record_number: int = redcap_interface_object.last_record_number()
    retrieved_df: pandas.DataFrame = redcap_interface_object.retrieve(
        last_record_number
    )
    assert isinstance(retrieved_df, pandas.DataFrame)
    num_elements_returned: int = retrieved_df.shape[0]
    assert num_elements_returned == 1
    assert "dob" in retrieved_df.columns

    retrieved_df = redcap_interface_object.retrieve("should not work")
    assert isinstance(retrieved_df, pandas.DataFrame)
    assert len(retrieved_df) == 0

    retrieved_df = redcap_interface_object.retrieve(-1)
    assert isinstance(retrieved_df, pandas.DataFrame)
    assert len(retrieved_df) == 0

    # Test expanded mode.
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


if __name__ == "__main__":
    #exercise_create_one_record()
    #exercise_create_multiple_records()
    #exercise_delete_record()
    #exercise_exists()
    #exercise_instantiate_object()
    #exercise_last_record_number()
    #exercise_next_record_number()
    exercise_report()
    exercise_retrieve_all_records()
    exercise_retrieve_multiple_records()
    exercise_retrieve_single_record()
