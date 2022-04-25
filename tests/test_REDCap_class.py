import pandas as pd
from datetime import datetime
from unittest import TestCase
from REDCap_API_interface import REDCapInterface
from utilities import convert_to_date

class TestREDCap(TestCase):
    def test_object_instantiation(self):
        redcap_interface_object = REDCapInterface(False)
        message = "Unable to instantiate a REDCapInterface object."
        self.assertIsInstance(redcap_interface_object, REDCapInterface, message)

        version_number = redcap_interface_object.version()
        self.assertEqual(version_number, "10.6.21")
        pass

    def test_single_record_retrieval(self):
        redcap_interface_object = REDCapInterface(False)
        df = redcap_interface_object.retrieve(6345949)
        message = "Unable to retrieve data frame from REDCap."
        self.assertIsInstance(df, pd.DataFrame, message)
        num_elements_returned: int = df.shape[0]
        message = f"Expected 1 element in dataframe but received {num_elements_returned}."
        self.assertEqual(num_elements_returned, 1, message)

    def test_multiple_record_retrieval(self):
        redcap_interface_object = REDCapInterface(False)
        df = redcap_interface_object.retrieve([6345966, 6345949])
        message = "Unable to retrieve data frame from REDCap."
        self.assertIsInstance(df, pd.DataFrame, message)
        num_elements_returned: int = df.shape[0]
        message = f"Expected 2 elements in dataframe but received {num_elements_returned}."
        self.assertEqual(num_elements_returned, 2, message)

    def test_bulk_record_retrieval(self):
        redcap_interface_object = REDCapInterface(False)
        df = redcap_interface_object.retrieve()
        message = "Unable to retrieve data frame from REDCap."
        self.assertIsInstance(df, pd.DataFrame, message)
        num_elements_returned: int = df.shape[0]
        message = f"Expected many elements in dataframe but received {num_elements_returned}."
        self.assertGreater(num_elements_returned, 2, message)

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
