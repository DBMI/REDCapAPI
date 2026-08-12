"""
Contains test fixtures available across all test_*.py files.
"""

import pandas
import pytest

from tests.helpers import fake_record_dict, fake_records_dataframe


@pytest.fixture(name="api_version_string")
def fixture_api_version_string() -> str:
    return "14.5.44"


@pytest.fixture(name="fake_next_record")
def fixture_fake_next_record() -> int:
    return 123456


@pytest.fixture(name="fake_ok_response")
def fixture_fake_ok_response() -> int:
    return 123456


# https://stackoverflow.com/a/33879151/20241849
@pytest.fixture(name="fake_records_dataframe")
def fixture_fake_records_dataframe() -> pandas.DataFrame:
    """
    Synthesize multiple records for testing.

    Return
    ------
    pandas.DataFrame
    """
    return fake_records_dataframe()


# https://stackoverflow.com/a/33879151/20241849
@pytest.fixture(name="fake_record_dict")
def fixture_fake_record_dict() -> dict:
    """
    Synthesize single record for testing.

    Return
    ------
    dict
    """
    return fake_record_dict()


# We loaded a known fake patient name into this record number.
# When we read that name, we can be sure we're looking at the DEV database.
# Accordingly, when deleting or updating records in test, we do NOT want
# to touch that special record. So we'll provide its record number to
# the last_record_number() method to specify that number is to be avoided.
@pytest.fixture(name="known_fake_record_number")
def fixture_known_fake_record_number() -> int:
    return 6393740


@pytest.fixture(name="known_fake_record")
def fixture_known_fake_record() -> dict:
    return {"study_id": "6393740", "first_name": "TESTER", "last_name": "TESTDATA"}


@pytest.fixture(name="url")
def fixture_url() -> str:
    return r"https://redcap.ucsd.edu/api/"
