"""
Contains test fixtures available across BOTH test and exercise files.
"""
import re
from datetime import datetime

import pandas
from faker import Faker


def api_version_string() -> str:
    return "14.5.44"


# https://stackoverflow.com/a/33879151/20241849
def fake_records_dataframe() -> pandas.DataFrame:
    """
    Synthesize multiple records for testing.

    Return
    ------
    pandas.DataFrame
    """
    num_records_to_synthesize: int = 3
    fake = Faker()
    dataframes: list = []

    for index in range(num_records_to_synthesize):
        birthdate: datetime = fake.date_of_birth(minimum_age=18, maximum_age=115)
        primary_consent_date: datetime = fake.date_between(birthdate)
        core_participant_date: datetime = fake.date_between(primary_consent_date)
        contact_date_one: datetime = fake.date_between(core_participant_date)

        # Strip off the extension.
        phone_number: str = fake.phone_number()
        phone_number = re.sub(r"x\d+", "", phone_number)

        record: dict = {
            "study_id": fake.random_int(min = 1, max = 10000),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "phone_number": phone_number,
            "email_address": fake.email(),
            "dob": birthdate.strftime("%Y-%m-%d"),
            "ethnicity": fake.random_int(min=1, max=2),
            "race": fake.random_int(min=1, max=5),
            "sex": fake.random_int(min=1, max=3),
            "contact_1_date_time": contact_date_one.strftime("%Y-%m-%d"),
            "core_participant_date": core_participant_date.strftime("%Y-%m-%d"),
            "primary_consent_date": primary_consent_date.strftime("%Y-%m-%d"),
            "date_of_last_activity": datetime.now().strftime("%Y-%m-%d"),
            "meeting_notes": fake.sentences(nb=3),
            "entered_velos___yes": "something",
        }

        dataframes.append(pandas.DataFrame([record], index=[index]))

    return pandas.concat(dataframes)


# https://stackoverflow.com/a/33879151/20241849
def fake_record_dict() -> dict:
    """
    Synthesize single record for testing.

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


def known_fake_record_number() -> int:
    return 6393740
