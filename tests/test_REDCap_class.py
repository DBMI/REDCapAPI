import pandas as pd
from unittest import TestCase
from REDCap_API_interface import REDCapInterface


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
