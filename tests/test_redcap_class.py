"""
Module test_redcap_class.py, which exists to support automated
testing of the REDCapInterface class.

Classes
-------
TestREDCap
"""
from datetime import datetime
from unittest import TestCase
import re
import pandas as pd
from faker import Faker
from src.dbmi_redcap import REDCapInterface
from utilities import convert_to_date


class TestREDCap(TestCase):
    """
    Class used for testing the REDCapInterface class.

    ...

    Attributes
    ----------
    api_version_string : str
        Set to the expected REDCap API version.
    known_fake_record_number : int
        The record we inserted into the DEV database
        that--when we see it--that confirms we're really in the DEV database.

    Methods
    -------
    test_bulk_record_retrieval()
        Tests retrieving ALL the records from our REDCap database.
    test_create_one_record()
        Tests creating one record from fake data.
    test_create_multiple_records()
        Tests creating several records.
    test_date_conversion()
        Tests many formats of date/time string data.
    test_delete_record()
        Tests method to delete a record.
    test_exists()
        Tests method that asks database whether given record exists.
    test_last_record_number()
        Tests method last_record_number() in both single and multiple modes.
    test_multiple_record_retrieval()
        Tests the retrieve() method using a list of desired records.
    test_next_record_number()
        Tests method that asks for next unused record number.
    test_object_instantiation()
        Tests the __init__ method of the REDCapInterface class.
    test_single_record_retrieval()
        Tests retrieving a single record.
    test_update_record()
        Tests updating a given record.
    """

    # We loaded a known fake patient name into this record number.
    # When we read that name, we can be sure we're looking at the DEV database.
    # Accordingly, when deleting or updating records in test, we do NOT want
    # to touch that special record. So we'll provide its record number to
    # the last_record_number() method to specify that number is to be avoided.
    api_version_string = "10.6.21"
    known_fake_record_number = 6393740

    def test_bulk_record_retrieval(self):
        """
        Test retrieving ALL records.

        Return
        ------
        bool
        """
        redcap_interface_object = REDCapInterface(isdev=True)
        retrieved_df = redcap_interface_object.retrieve()
        self.assertIsInstance(
            retrieved_df, pd.DataFrame, "Unable to retrieve data frame from REDCap."
        )
        num_elements_returned: int = retrieved_df.shape[0]
        message = (
            f"Expected many elements in dataframe but received {num_elements_returned}."
        )
        self.assertGreater(num_elements_returned, 2, message)
        self.assertTrue("dob" in retrieved_df.columns)

        # Bulk mode won't work in expanded mode--insufficient memory.

    def test_create_one_record(self):
        """
        Test creating ONE record.

        Return
        ------
        bool
        """
        redcap_interface_object = REDCapInterface(isdev=True)
        self.assertTrue(redcap_interface_object.create(None) is None)
        self.assertFalse(redcap_interface_object.create("should not work"))
        next_study_id = redcap_interface_object.next_record_number()
        record = self.__create_fake_record(next_study_id)
        self.assertTrue(redcap_interface_object.create(record))
        df = pd.DataFrame([record], index=[next_study_id])
        self.assertTrue(redcap_interface_object.create(df))

    def test_create_multiple_records(self):
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
            record = self.__create_fake_record(next_study_id)
            success &= redcap_interface_object.create(record)

        self.assertTrue(success)

    def test_date_conversion(self):
        """
        Test converting strings to dates.

        Return
        ------
        bool
        """
        date_value_true = datetime.strptime("31/01/1970", "%d/%m/%Y")
        datetime_value_true = datetime.strptime(
            "31/01/1970 12:05:10", "%d/%m/%Y %H:%M:%S"
        )

        date_string_test = "01/31/1970"
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = "01/31/70"
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = "01-31-1970"
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = "01-31-70"
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = "70-01-31"
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = "1970-01-31 12:05:10"
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, datetime_value_true)

        date_string_test = "1970-01-31"
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = "31 Jan 1970"
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = "Jan 31 1970"
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = "Jan 31, 1970"
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        date_string_test = "Jan 31 1970 12:00AM"
        date_string_converted = convert_to_date(date_string_test)
        self.assertEqual(date_string_converted, date_value_true)

        # Cases we expect to return None.
        date_string_test = ""
        date_string_converted = convert_to_date(date_string_test)
        self.assertTrue(date_string_converted is None)

        date_string_test = "text only"
        date_string_converted = convert_to_date(date_string_test)
        self.assertTrue(date_string_converted is None)

        date_string_test = "1234 cannot be parsed"
        date_string_converted = convert_to_date(date_string_test)
        self.assertTrue(date_string_converted is None)

    def test_delete_record(self):
        """
        Test deleting one record.

        Return
        ------
        bool
        """
        redcap_interface_object = REDCapInterface(isdev=True)
        last_record_number = redcap_interface_object.last_record_number(
            except_for=TestREDCap.known_fake_record_number
        )

        if last_record_number is None or last_record_number <= 0:  # pragma: no cover
            raise Exception("Unable to find any records I'm allowed to delete.")

        self.assertTrue(
            redcap_interface_object.delete(last_record_number),
            "Unable to delete object.",
        )

        # Ensure calling "delete" with no record number returns None.
        self.assertTrue(
            redcap_interface_object.delete(None) is None,
            "Get the wrong answer back when supplying null record number.",
        )

    def test_exists(self):
        """
        Test method for querying whether given record is present.

        Return
        ------
        bool
        """
        redcap_interface_object = REDCapInterface(isdev=True)
        last_record_number = redcap_interface_object.last_record_number()
        self.assertTrue(redcap_interface_object.exists(last_record_number))

        # Cases that should result in False.
        self.assertFalse(redcap_interface_object.exists(None))
        self.assertFalse(redcap_interface_object.exists(-1))

        # Case that should throw exception.
        with self.assertRaises(TypeError):
            redcap_interface_object.exists("should throw error")

    def test_last_record_number(self):
        """
        Test method for looking up highest used record number.

        Return
        ------
        bool
        """
        redcap_interface_object = REDCapInterface(isdev=True)
        last_valid_number = redcap_interface_object.last_record_number()
        self.assertTrue(isinstance(last_valid_number, int))
        last_valid_number = redcap_interface_object.last_record_number(
            except_for=TestREDCap.known_fake_record_number
        )
        self.assertTrue(isinstance(last_valid_number, int))

        # Force method to look past the first guess (next number - 1).
        last_valid_number = redcap_interface_object.last_record_number(
            except_for=last_valid_number
        )
        self.assertTrue(isinstance(last_valid_number, int))

        # Multiple values
        last_valid_number = redcap_interface_object.last_record_number(number_desired=2)
        self.assertTrue(isinstance(last_valid_number, list))
        self.assertEqual(len(last_valid_number), 2)

    def test_multiple_record_retrieval(self):
        """
        Test retrieving SEVERAL records.

        Return
        ------
        bool
        """
        redcap_interface_object = REDCapInterface(isdev=True)
        two_valid_numbers = redcap_interface_object.last_record_number(number_desired=2)
        retrieved_df = redcap_interface_object.retrieve(two_valid_numbers)
        self.assertIsInstance(
            retrieved_df, pd.DataFrame, "Unable to retrieve data frame from REDCap."
        )
        num_elements_returned: int = retrieved_df.shape[0]
        self.assertEqual(
            num_elements_returned,
            2,
            f"Expected 2 elements in dataframe but received {num_elements_returned}.",
        )
        self.assertTrue("dob" in retrieved_df.columns)

        # Expanded mode.
        retrieved_df = redcap_interface_object.retrieve(
            record_numbers=two_valid_numbers, expanded_record=True
        )
        self.assertIsInstance(
            retrieved_df, pd.DataFrame, "Unable to retrieve data frame from REDCap."
        )
        num_elements_returned: int = retrieved_df.shape[0]
        self.assertEqual(
            num_elements_returned,
            2,
            f"Expected 2 elements in dataframe but received {num_elements_returned}.",
        )
        self.assertTrue("meeting_notes" in retrieved_df.columns)

    def test_next_record_number(self):
        """
        Test method for determining which is next unused record number.

        Return
        ------
        bool
        """
        redcap_interface_object = REDCapInterface(isdev=True)
        next_number = redcap_interface_object.next_record_number()
        self.assertTrue(isinstance(next_number, int))

    def test_object_instantiation(self):
        """
        Test creating REDCapInterface object.

        Return
        ------
        bool
        """
        #   This is the ONLY time in testing that we'll instantiate a REDCapInterface object
        #    WITHOUT the isdev flag set. It's to ensure we CAN read the production token.
        production_redcap_interface_object = REDCapInterface(isdev=False)
        self.assertIsInstance(
            production_redcap_interface_object,
            REDCapInterface,
            "Unable to instantiate a PRODUCTION REDCapInterface object.",
        )
        version_number = production_redcap_interface_object.version()
        self.assertEqual(version_number, TestREDCap.api_version_string)

        #   We'll use the isdev = True flag to specify we want to talk to the DEV database.
        redcap_interface_object = REDCapInterface(isdev=True)
        self.assertIsInstance(
            redcap_interface_object,
            REDCapInterface,
            "Unable to instantiate a DEV REDCapInterface object.",
        )

        version_number = redcap_interface_object.version()
        self.assertEqual(version_number, TestREDCap.api_version_string)

    def test_single_record_retrieval(self):
        """
        Test retrieving ONE record.

        Return
        ------
        bool
        """
        redcap_interface_object = REDCapInterface(isdev=True)
        last_record_number = redcap_interface_object.last_record_number()
        retrieved_df = redcap_interface_object.retrieve(last_record_number)
        self.assertIsInstance(
            retrieved_df, pd.DataFrame, "Unable to retrieve data frame from REDCap."
        )
        num_elements_returned: int = retrieved_df.shape[0]
        self.assertEqual(
            num_elements_returned,
            1,
            f"Expected 1 element in dataframe but received {num_elements_returned}.",
        )
        self.assertTrue("dob" in retrieved_df.columns)

        self.assertTrue(redcap_interface_object.retrieve("should not work") is None)

        with self.assertRaises(RuntimeError):
            redcap_interface_object.retrieve(-1)

        # Test expanded mode.
        retrieved_df = redcap_interface_object.retrieve(
            record_numbers=last_record_number, expanded_record=True
        )

        self.assertIsInstance(
            retrieved_df, pd.DataFrame, "Unable to retrieve data frame from REDCap."
        )
        num_elements_returned: int = retrieved_df.shape[0]
        self.assertEqual(
            num_elements_returned,
            1,
            f"Expected 1 element in dataframe but received {num_elements_returned}.",
        )
        self.assertTrue("meeting_notes" in retrieved_df.columns)

    def test_update_record(self):
        """
        Test updating given record.

        Return
        ------
        bool
        """
        redcap_interface_object = REDCapInterface(isdev=True)
        last_record_number = redcap_interface_object.last_record_number(
            except_for=TestREDCap.known_fake_record_number
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
        self.assertTrue(redcap_interface_object.update(new_info))

        # Check that the date_of_last_activity field was really updated.
        updated_record = redcap_interface_object.retrieve(last_record_number)
        self.assertTrue(
            updated_record is not None and isinstance(updated_record, pd.DataFrame),
            "Unable to retrieve updated record.",
        )
        self.assertTrue(
            "date_of_last_activity" in updated_record,
            "Unable to find 'date_of_last_activity' in updated record.",
        )
        retrieved_datestring = updated_record["date_of_last_activity"][0]
        self.assertEqual(
            right_now_string, retrieved_datestring, "Record was not updated."
        )

        # Test again with dataframe input.
        right_now_string = datetime.strftime(right_now, "%Y-%m-%d")
        new_info = {
            "study_id": str(last_record_number),
            "date_of_last_activity": right_now_string,
        }
        new_info_df = pd.DataFrame(data=new_info, index=[0])
        self.assertTrue(redcap_interface_object.update(new_info_df))

        # Check that the date_of_last_activity field was really updated.
        updated_record = redcap_interface_object.retrieve(last_record_number)
        self.assertTrue(
            updated_record is not None and isinstance(updated_record, pd.DataFrame),
            "Unable to retrieve updated record.",
        )
        self.assertTrue(
            "date_of_last_activity" in updated_record,
            "Unable to find 'date_of_last_activity' in updated record.",
        )
        retrieved_datestring = updated_record["date_of_last_activity"][0]
        self.assertEqual(
            right_now_string, retrieved_datestring, "Record was not updated."
        )

        # Test inputs that should raise errors.
        with self.assertRaises(TypeError):
            redcap_interface_object.update("should throw error")

        # What if the attempted update can't be inserted? Ensure
        new_info["this_column_does_not_exist"] = "this won't work"
        new_info_df = pd.DataFrame(data=new_info, index=[0])

        with self.assertRaises(RuntimeError) as error_raised:
            redcap_interface_object.update(new_info_df)
        self.assertEqual(
            "Unable to update; original record was restored.",
            str(error_raised.exception),
            "Did not receive message that original record was restored.",
        )

    @staticmethod
    def __create_fake_record(next_study_id):
        """
        Synthesize data for testing.

        Paramters
        ---------
        next_study_id :   int

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
            "study_id": next_study_id,
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


if __name__ == "__main__":  # pragma: no cover
    pass
