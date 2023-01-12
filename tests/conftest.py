"""
Contains test fixtures available across all test_*.py files.
"""
from datetime import datetime
import pytest
import re
from faker import Faker


@pytest.fixture(name="api_version_string")
def fixture_api_version_string() -> str:
    return "12.4.6"


# https://stackoverflow.com/a/33879151/20241849
@pytest.fixture(name="fake_record", scope="function")
def fixture_fake_record() -> dict:
    """
    Synthesize data for testing.

    Return
    ------
    dict
    """
    fake = Faker()
    birthdate = fake.date_of_birth(minimum_age=18, maximum_age=115)
    primary_consent_date = fake.date_between(birthdate)
    core_participant_date = fake.date_between(primary_consent_date)

    # Strip off the extension.
    phone_number = fake.phone_number()
    phone_number = re.sub(r"x\d+", "", phone_number)

    record = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "phone_number": phone_number,
        "email_address": fake.email(),
        "dob": birthdate.strftime("%Y-%m-%d"),
        "ethnicity": fake.random_int(min=1, max=2),
        "race": fake.random_int(min=1, max=5),
        "sex": fake.random_int(min=1, max=3),
        "core_participant_date": core_participant_date.strftime("%Y-%m-%d"),
        "primary_consent_date": primary_consent_date.strftime("%Y-%m-%d"),
        "date_of_last_activity": datetime.now().strftime("%Y-%m-%d"),
    }

    return record


# We loaded a known fake patient name into this record number.
# When we read that name, we can be sure we're looking at the DEV database.
# Accordingly, when deleting or updating records in test, we do NOT want
# to touch that special record. So we'll provide its record number to
# the last_record_number() method to specify that number is to be avoided.
@pytest.fixture(name="known_fake_record_number")
def fixture_known_fake_record_number() -> int:
    return 6393740
