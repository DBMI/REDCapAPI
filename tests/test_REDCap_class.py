import pandas as pd
import re
from datetime import datetime
from faker import Faker
from unittest import TestCase
from REDCap_API_interface import REDCapInterface
from utilities import convert_to_date


class TestREDCap(TestCase):

    # We loaded a known fake patient name into this record number.
    # When we read that name, we can be sure we're looking at the DEV database.
    # Accordingly, when deleting or updating records in test, we do NOT want
    # to touch that special record. So we'll provide its record number to
    # the last_record_number() method to specify that number is to be avoided.
    known_fake_record_number = 6393740
    api_version_string = "10.6.21"

    def test_bulk_record_retrieval(self):
        redcap_interface_object = REDCapInterface(isdev=True)
        df = redcap_interface_object.retrieve()
        message = "Unable to retrieve data frame from REDCap."
        self.assertIsInstance(df, pd.DataFrame, message)
        num_elements_returned: int = df.shape[0]
        message = f"Expected many elements in dataframe but received {num_elements_returned}."
        self.assertGreater(num_elements_returned, 2, message)

    def test_create_one_record(self):
        redcap_interface_object = REDCapInterface(isdev=True)
        self.assertTrue(redcap_interface_object.create(None) is None)
        self.assertFalse(redcap_interface_object.create("should not work"))
        next_study_id = redcap_interface_object.next_record_number()
        record = self.create_fake_record(next_study_id)
        self.assertTrue(redcap_interface_object.create(record))

    def test_create_multiple_records(self):
        redcap_interface_object = REDCapInterface(isdev=True)
        num_records_to_create = 3
        success = True

        for record_index in range(num_records_to_create):
            next_study_id = redcap_interface_object.next_record_number()
            record = self.create_fake_record(next_study_id)
            success &= redcap_interface_object.create(record)

        self.assertTrue(success)

    def test_date_conversion(self):
        date_value_true = datetime.strptime("31/01/1970", "%d/%m/%Y")
        datetime_value_true = datetime.strptime("31/01/1970 12:05:10", "%d/%m/%Y %H:%M:%S")

        date_string_test = '01/31/1970'
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = '01/31/70'
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = '01-31-1970'
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = '01-31-70'
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = '70-01-31'
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = '1970-01-31 12:05:10'
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, datetime_value_true)

        date_string_test = '1970-01-31'
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = '31 Jan 1970'
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = 'Jan 31 1970'
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = 'Jan 31, 1970'
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = 'Jan 31 1970 12:00AM'
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        # Cases we expect to return None.
        date_string_test = ''
        date_string_converted = convert_to_date(date_string_test)
        self.assertTrue(date_string_converted is None)

        date_string_test = 'text only'
        date_string_converted = convert_to_date(date_string_test)
        self.assertTrue(date_string_converted is None)

        date_string_test = '1234 cannot be parsed'
        date_string_converted = convert_to_date(date_string_test)
        self.assertTrue(date_string_converted is None)

    def test_delete_record(self):
        redcap_interface_object = REDCapInterface(isdev=True)
        last_record_number = redcap_interface_object.last_record_number(except_for=TestREDCap.known_fake_record_number)

        if last_record_number is None or last_record_number <= 0:  # pragma: no cover
            raise Exception("Unable to find any records I'm allowed to delete.")

        self.assertTrue(redcap_interface_object.delete(last_record_number),
                        "Unable to delete object.")

    def test_exists(self):
        redcap_interface_object = REDCapInterface(isdev=True)
        last_record_number = redcap_interface_object.last_record_number()
        self.assertTrue(redcap_interface_object.exists(last_record_number))
        self.assertFalse(redcap_interface_object.exists(None))

        with self.assertRaises(TypeError):
            redcap_interface_object.exists("should throw error")

        self.assertFalse(redcap_interface_object.exists(-1))

    def test_known_record_present(self):
        redcap_interface_object = REDCapInterface(isdev=True)
        self.assertTrue(redcap_interface_object._known_test_record_present())

    def test_last_record_number(self):
        redcap_interface_object = REDCapInterface(isdev=True)
        last_valid_number = redcap_interface_object.last_record_number()
        self.assertTrue(isinstance(last_valid_number, int))
        last_valid_number = redcap_interface_object.last_record_number(except_for=TestREDCap.known_fake_record_number)
        self.assertTrue(isinstance(last_valid_number, int))

        # Force method to look past the first guess (next number - 1).
        last_valid_number = redcap_interface_object.last_record_number(except_for=last_valid_number)
        self.assertTrue(isinstance(last_valid_number, int))

        # Multiple values
        last_valid_number = redcap_interface_object.last_record_number(number_desired=2)
        self.assertTrue(isinstance(last_valid_number, list))
        self.assertEqual(len(last_valid_number), 2)

    def test_multiple_record_retrieval(self):
        redcap_interface_object = REDCapInterface(isdev=True)
        two_valid_numbers = redcap_interface_object.last_record_number(number_desired=2)
        df = redcap_interface_object.retrieve(two_valid_numbers)
        self.assertIsInstance(df, pd.DataFrame, "Unable to retrieve data frame from REDCap.")
        num_elements_returned: int = df.shape[0]
        self.assertEqual(num_elements_returned, 2,
                         f"Expected 2 elements in dataframe but received {num_elements_returned}.")

    def test_next_record_number(self):
        redcap_interface_object = REDCapInterface(isdev=True)
        next_number = redcap_interface_object.next_record_number()
        self.assertTrue(isinstance(next_number, int))

    def test_object_instantiation(self):
        #   This is the ONLY time in testing that we'll instantiate a REDCapInterface object
        #    WITHOUT the isdev flag set. It's to ensure we CAN read the production token.
        production_redcap_interface_object = REDCapInterface(isdev=False)
        self.assertIsInstance(production_redcap_interface_object, REDCapInterface,
                              "Unable to instantiate a PRODUCTION REDCapInterface object.")
        version_number = production_redcap_interface_object.version()
        self.assertEqual(version_number, TestREDCap.api_version_string)

        #   We'll use the isdev = True flag to specify we want to talk to the DEV database.
        redcap_interface_object = REDCapInterface(isdev=True)
        self.assertIsInstance(redcap_interface_object, REDCapInterface,
                              "Unable to instantiate a DEV REDCapInterface object.")

        version_number = redcap_interface_object.version()
        self.assertEqual(version_number, TestREDCap.api_version_string)

    def test_single_record_retrieval(self):
        redcap_interface_object = REDCapInterface(isdev=True)
        last_record_number = redcap_interface_object.last_record_number()
        df = redcap_interface_object.retrieve(last_record_number)
        self.assertIsInstance(df, pd.DataFrame, "Unable to retrieve data frame from REDCap.")
        num_elements_returned: int = df.shape[0]
        self.assertEqual(num_elements_returned, 1,
                         f"Expected 1 element in dataframe but received {num_elements_returned}.")
        self.assertTrue(redcap_interface_object.retrieve("should not work") is None)

        with self.assertRaises(RuntimeError):
            redcap_interface_object.retrieve(-1)

    def test_update_record(self):
        redcap_interface_object = REDCapInterface(isdev=True)
        last_record_number = redcap_interface_object.last_record_number(except_for=TestREDCap.known_fake_record_number)

        if last_record_number is None or last_record_number <= 0:  # pragma: no cover
            raise Exception("Unable to find any records I'm allowed to update.")

        right_now = datetime.now()
        right_now_string = datetime.strftime(right_now, '%Y-%m-%d')
        new_info = {'study_id': str(last_record_number),
                    'date_of_last_activity': right_now_string}
        new_info_df = pd.DataFrame(data=new_info, index=[0])
        self.assertTrue(redcap_interface_object.update(new_info_df))

        # Check that the date_of_last_activity field was really updated.
        updated_record = redcap_interface_object.retrieve(last_record_number)
        self.assertTrue(updated_record is not None and isinstance(updated_record, pd.DataFrame),
                        "Unable to retrieve updated record.")
        self.assertTrue('date_of_last_activity' in updated_record,
                        "Unable to find 'date_of_last_activity' in updated record.")
        retrieved_datestring = updated_record['date_of_last_activity'][0]
        self.assertEqual(right_now_string, retrieved_datestring, "Record was not updated.")

        with self.assertRaises(TypeError):
            redcap_interface_object.update("should throw error")

        # What if the attempted update can't be inserted? Ensure
        new_info['this_column_does_not_exist'] = "this won't work"
        new_info_df = pd.DataFrame(data=new_info, index=[0])

        with self.assertRaises(RuntimeError) as error_raised:
            redcap_interface_object.update(new_info_df)
        self.assertEqual(
            "Unable to update; original record was restored.",
            str(error_raised.exception)
        )

    @staticmethod
    def create_fake_record(next_study_id):
        fake = Faker()
        birthdate = fake.date_of_birth(minimum_age=18, maximum_age=115)
        primary_consent_date = fake.date_between(birthdate)
        core_participant_date = fake.date_between(primary_consent_date)

        # Strip off the extension.
        phone_number = fake.phone_number()
        phone_number = re.sub(r'x\d+', '', phone_number)

        record = {
            'study_id': next_study_id,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'phone_number': phone_number,
            'email_address': fake.email(),
            'dob': birthdate.strftime("%Y-%m-%d"),
            'ethnicity': fake.random_int(min=1, max=2),
            'race': fake.random_int(min=1, max=5),
            'sex': fake.random_int(min=1, max=3),
            'core_participant_date': core_participant_date.strftime("%Y-%m-%d"),
            'primary_consent_date': primary_consent_date.strftime("%Y-%m-%d"),
            'date_of_last_activity': datetime.now().strftime("%Y-%m-%d"),
        }

        return record
