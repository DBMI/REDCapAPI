"""
Module: contains class REDCapInterface, providing a wrapper around the REDCap API.
"""
import configparser
import json
import math
from enum import Enum
from typing import List, Union

import pandas  # type: ignore[import]
import requests
from redcaputilities.logging import setup_logging


class DataRequest(Enum):
    Expanded = 1
    Standard = 2
    Velos = 3


class REDCapInterface:
    """
    Wrapper class around the REDCap API.

    ...

    Attributes
    ----------
    no public attributes

    Methods (starting in CRUD order)
    -------
    create(data_records)
        Inserts new records from a dict, list of dicts or a dataframe.
        Assumes user has included the study_id in each new record.
    retrieve()
        When called without argument, retrieves ALL the records in the database.
    retrieve(record_numbers)
        When called with either a single record number or a list of numbers,
        retrieves those records.
    delete(record_number)
        Deletes the data record at the specified study_id value.
    exists(record_number)
        Returns whether the specified record number exists in the database.
    last_record_number()
        Returns the highest study_id value present in the database.
    next_record_number()
        Returns the next unused study_id value; used in creating new record.
    version()
        Returns the version number of the REDCap API in use.
    """

    def __init__(self, isdev: bool = False, timeout_sec: int = 30):
        """
        Create instance of `REDCapInterface` class.

        Assumes using production data, but can be created with isdev=True to
        point to the development database.
        Gets database token from "F:\\RedCap\\secrets\\config.key"

        Parameters
        ----------
        isdev : bool, optional
            Set to True when using development database (default is False)

        timeout_sec : int, optional
            How long to wait (in seconds) for reponse (default: 10 sec)

        Return
        -------
        none; Instantiates object

        Examples
        --------
        >>> from src.redcapapi import REDCapInterface
        >>>
        >>>
        >>> production_redcap_interface_object = REDCapInterface()
        >>> development_redcap_interface_object = REDCapInterface(isdev=True)
        """
        self.__log = setup_logging(log_filename="redcap_api.log")
        self.__log.info("REDCapInterface object instantiated.")
        self.__api_uri: Union[str, None] = None
        self.__capmc_token: Union[str, None] = None
        self.__isdev = isdev
        self.__read_config_file()
        self.__timeout_sec = timeout_sec

        if self.__isdev and not self.__known_test_record_present():  # pragma: no cover
            self.__log.exception(
                "Unable to find known test record. "
                "You might not be connected to the DEV database."
            )
            raise RuntimeError(
                "WARNING! Unable to find known test record. "
                "You might not be connected to the DEV database."
            )

        # Lets all methods know that we're talking to the correct database.
        self.__valid = True

    def create(self, data_records: Union[dict, pandas.DataFrame]) -> bool:
        """
        Insert new records into database.

        Parameters
        ----------
        data_records : dict, dataframe
            Must contain the new study_id desired.

        Return
        ------
        bool

        Examples
        --------
        >>> from src.redcapapi import REDCapInterface
        >>>
        >>>
        >>> redcap_interface_object = REDCapInterface()
        >>> new_data = {
        >>> 'study_id': '12345',
        >>> 'name': "Patient's Name",
        >>> 'mrn': '000000', ...}
        >>> redcap_interface_object.create(new_data)
        """
        if not self.__valid:  # pragma: no cover
            return False

        if data_records is None:
            return False

        if isinstance(data_records, dict):
            data_records_list = [data_records]
        elif isinstance(data_records, pandas.DataFrame):
            data_records_list = data_records.to_dict("records")
        else:
            return False

        # Remove fields containing no info.
        data_records_list = list(map(self.__discard_empty_fields, data_records_list))
        next_study_id = self.next_record_number()

        # Ensure 'study_id' is included.
        for index, record in enumerate(data_records_list):
            if "study_id" not in record:
                record["study_id"] = next_study_id + index
                data_records_list[index] = record

        # JSONify
        data = json.dumps(data_records_list)

        fields = {
            "token": self.__capmc_token,
            "content": "record",
            "format": "json",
            "type": "flat",
            "data": data,
        }

        assert self.__api_uri is not None, "Unable to read 'API_URL.'"
        response = requests.post(
            self.__api_uri, data=fields, timeout=self.__timeout_sec
        )

        if not isinstance(response, requests.Response):
            self.__log.error("Unable to create records; no 'response' object.")
            return False

        if response.status_code != 200:
            self.__log.error("Unable to create records because: '%s'.", response.text)
            return False

        return True

    def __build_data_pull(
        self,
        record_numbers: Union[list, None],
        data_request: DataRequest = DataRequest.Standard,
    ) -> dict:
        """
        Assemble dict used when retrieving data records.

        Parameters
        ----------
        record_numbers : list Optional
            default is None (to retrieve ALL records)
        data_request : DataRequest, optional
            How many fields do you want?
                Standard (default):
                    returns study_id, dob, primary_consent_date,
                    core_participant_date, date_of_last_activity
                Expanded:
                    returns ALL fields (this is probably too big
                    if also requesting ALL the records)
                Velos:
                    entered_velos, mrn, study_id, time_visit_ended, type_of_draw

        Return
        ------
        dict
        """
        # NOT specifying the "fields" list ==> give me ALL the fields.
        pull_dict = {
            "token": self.__capmc_token,
            "content": "record",
            "format": "json",
            "type": "flat",
            "csvDelimiter": "",
            "rawOrLabel": "raw",
            "rawOrLabelHeaders": "raw",
            "exportCheckboxLabel": "false",
            "exportSurveyFields": "false",
            "exportDataAccessGroups": "false",
            "returnFormat": "json",
        }

        if data_request == DataRequest.Standard:
            pull_dict["fields[0]"] = "study_id"
            pull_dict["fields[1]"] = "mrn"
            pull_dict["fields[2]"] = "first_name"
            pull_dict["fields[3]"] = "last_name"
            pull_dict["fields[4]"] = "street_address_line_1"
            pull_dict["fields[5]"] = "street_address_line_2"
            pull_dict["fields[6]"] = "city"
            pull_dict["fields[7]"] = "state"
            pull_dict["fields[8]"] = "zip_code"
            pull_dict["fields[9]"] = "email_address"
            pull_dict["fields[10]"] = "phone_number"
            pull_dict["fields[11]"] = "dob"
            pull_dict["fields[12]"] = "death_datetime"
            pull_dict["fields[13]"] = "ethnicity"
            pull_dict["fields[14]"] = "race"
            pull_dict["fields[15]"] = "sex"
            pull_dict["fields[16]"] = "primary_consent_date"
            pull_dict["fields[17]"] = "core_participant_date"
            pull_dict["fields[18]"] = "date_of_last_activity"
            pull_dict["fields[19]"] = "date_added"
            pull_dict["fields[20]"] = "duplicate_record___yes"
            pull_dict["fields[21]"] = "appointment_clinic"
            pull_dict["fields[22]"] = "appointment_date"
            pull_dict["fields[23]"] = "appointment_time"
            pull_dict["fields[24]"] = "hpi_score"
            pull_dict["fields[25]"] = "hpi_percentile"
        elif data_request == DataRequest.Velos:
            pull_dict["fields[0]"] = "study_id"
            pull_dict["fields[1]"] = "mrn"
            pull_dict["fields[2]"] = "entered_velos"
            pull_dict["fields[3]"] = "time_visit_ended"
            pull_dict["fields[4]"] = "type_of_draw"

        if (
            record_numbers is not None
            and isinstance(record_numbers, list)
            and len(record_numbers) > 0
        ):
            # Insert into the dictionary a key for each desired record number.
            record_count = 0

            for record_number in record_numbers:
                record_name = f"records[, {record_count}, ]"
                pull_dict[record_name] = record_number
                record_count += 1

        return pull_dict

    def delete(self, record_number: int) -> bool:
        """
        Insert new records into database.

        Parameters
        ----------
        record_number : int
            The study_id of the record to delete.

        Return
        ------
        bool

        Examples
        --------
        >>> from src.redcapapi import REDCapInterface
        >>>
        >>>
        >>> redcap_interface_object = REDCapInterface()
        >>> redcap_interface_object.delete(12345)
        """
        if not self.__valid:  # pragma: no cover
            return False

        if not isinstance(record_number, int):
            return False

        fields = {
            "token": self.__capmc_token,
            "action": "delete",
            "content": "record",
            "records[0]": record_number,
        }

        assert self.__api_uri is not None, "Unable to read 'API_URL.'"
        response = requests.post(
            self.__api_uri, data=fields, timeout=self.__timeout_sec
        )
        return response is not None and response.status_code == 200

    def __discard_empty_fields(self, input_dict: dict) -> dict:
        """Trim dict keys with empty or nan values.

        Parameters
        ----------
        input_dict : dict

        Return
        ------
        input_trimmed : dict
        """
        if input_dict is None or not isinstance(input_dict, dict):
            self.__log.exception("Input 'input_dict' is not an int.")
            raise TypeError("Input 'input_dict' is not an int.")

        input_trimmed = {}

        for key, value in input_dict.items():
            if value is not None:
                if isinstance(value, str) and value != "NaN":
                    input_trimmed[key] = value
                    continue

                if isinstance(value, (int, float)) and not math.isnan(value):
                    input_trimmed[key] = str(value)

        return input_trimmed

    def exists(self, record_number: int) -> bool:
        """
        See if given record number exists in the database.

        Parameters
        ----------
        record_number : int
            The value of the study_id field in the desired record.

        Return
        ------
        bool
            Was that record_number found?

        Examples
        --------
        >>> from src.redcapapi import REDCapInterface
        >>>
        >>>
        >>> redcap_interface_object = REDCapInterface()
        >>>
        >>> if redcap_interface_object.exists(record_number): ...
        """
        if not self.__valid:  # pragma: no cover
            return False

        if isinstance(record_number, int):
            data_pull = self.__build_data_pull([record_number])
        else:
            self.__log.exception("Input 'record_number' is not an int.")
            raise TypeError("Input 'record_number' is not an int.")

        assert self.__api_uri is not None, "Unable to read 'API_URL.'"
        response = requests.post(
            self.__api_uri, data=data_pull, verify=True, timeout=self.__timeout_sec
        )

        try:
            return response.status_code == 200 and "study_id" in response.text
        except RuntimeError:  # pragma: no cover
            return False

    # Check for the presence of a known test record
    # to be doubly sure we're connected to DEV_CAPMC_RECRUITMENT.
    def __known_test_record_present(self) -> bool:
        """
        Check if the known record inserted into the development database is present.

        If present, this confirms that we are connected to the development
        (and not the production) database.

        Return
        -------
        bool
        """
        test_record_number = 6393740  # pragma: no cover
        record = self.retrieve(test_record_number)

        if (
            record is None
            or not isinstance(record, pandas.DataFrame)
            or "first_name" not in record
            or "last_name" not in record
        ):  # pragma: no cover
            self.__log.exception(
                "Unable to retrieve known test record. "
                "You might not be connected to the DEV database."
            )
            raise RuntimeError(
                "Unable to retrieve known test record. "
                "You might not be connected to the DEV database."
            )

        record0 = record.iloc[0]
        first_name_ck = bool(record0.first_name == "TESTER")
        last_name_ck = bool(record0.last_name == "TESTDATA")
        return first_name_ck and last_name_ck

    def last_record_number(
        self, except_for: Union[int, list, None] = None, number_desired: int = 1
    ) -> Union[int, list]:
        """
        Lookup the highest record number (study_id) present in the database.

        Parameters
        ----------
        except_for : int, list or None
            Record numbers to skip over.
        number_desired : int, optional
            How many numbers to return. default is 1

        Return
        -------
        int or list of ints

        Examples
        --------
        >>> from src.redcapapi import REDCapInterface
        >>>
        >>>
        >>> redcap_interface_object = REDCapInterface()
        >>> highest_record_number_in_use = redcap_interface_object.last_record_number()
        """
        last_valid_record_number = self.next_record_number() - 1
        valid_record_numbers_found: List[int] = []

        if except_for is not None:
            if isinstance(except_for, int):
                except_for = [except_for]
            elif not isinstance(except_for, list):  # pragma: no cover
                self.__log.exception("Argument 'except_for' is neither int nor list.")
                raise TypeError("Argument 'except_for' is neither int nor list.")
        else:
            except_for = [None]

        while len(valid_record_numbers_found) < number_desired:
            while (
                not self.exists(last_valid_record_number)
                or last_valid_record_number in except_for
            ):
                if last_valid_record_number > 0:
                    last_valid_record_number -= 1
                else:  # pragma: no cover
                    self.__log.exception("Unable to find any valid record numbers.")
                    raise RuntimeError("Unable to find any valid record numbers.")

            except_for.append(last_valid_record_number)
            valid_record_numbers_found.append(last_valid_record_number)

        if len(valid_record_numbers_found) == 1:
            return valid_record_numbers_found[0]

        return valid_record_numbers_found

    def next_record_number(self) -> int:
        """
        Lookup next available record number.

        Used when creating a new record.

        Return
        ------
        int

        Examples
        --------
        >>> from src.redcapapi import REDCapInterface
        >>>
        >>>
        >>> redcap_interface_object = REDCapInterface()
        >>> new_record_number = redcap_interface_object.next_record_number()
        """
        fields = {
            "token": self.__capmc_token,
            "content": "generateNextRecordName",
        }

        assert self.__api_uri is not None, "Unable to read 'API_URL.'"
        response = requests.post(
            self.__api_uri, data=fields, timeout=self.__timeout_sec
        )

        if response is None or response.status_code != 200:  # pragma: no cover
            self.__log.exception("Unable to query for next record number.")
            raise RuntimeError("Unable to query for next record number.")

        try:
            return int(response.text)
        except TypeError as error:  # pragma: no cover
            self.__log.exception("Unable to parse next record number.")
            raise RuntimeError("Unable to parse next record number.") from error

    def __read_config_file(self) -> None:
        config = configparser.ConfigParser()

        if self.__isdev:
            config.read(r"F:\RedCap\secrets\config-dev.key")
        else:
            config.read(r"F:\RedCap\secrets\config.key")

        self.__api_uri = config.get("API", "API_URL")
        self.__capmc_token = config.get("CAPMC", "CAPMC_TOKEN")

    def retrieve(
        self,
        record_numbers: Union[int, list, None] = None,
        data_request: DataRequest = DataRequest.Standard,
    ) -> pandas.DataFrame:
        """
        Get particular record(s) or all the records.

        Parameters
        ----------
        record_numbers : int or list, optional
            If specified, returns just that/those record(s).
            If None or unspecified, returns all the records. default is None
        data_request : DataRequest, optional
            How many fields do you want?
                Standard (default):
                    returns study_id, dob, primary_consent_date,
                    core_participant_date, date_of_last_activity
                Expanded:
                    returns ALL fields (this is probably too big
                    if also requesting ALL the records)
                Velos:
                    entered_velos, mrn, study_id, time_visit_ended, type_of_draw

        Return
        ------
        dataframe

        Examples
        --------
        >>> from src.redcapapi import REDCapInterface
        >>>
        >>>
        >>> redcap_interface_object = REDCapInterface()
        >>> df_all = redcap_interface_object.retrieve()
        >>> df_selected = redcap_interface_object.retrieve([1234, 2345])
        """
        df = pandas.DataFrame()

        # No need to check for self.__valid here; it's always OK to retrieve records.
        if record_numbers is not None:
            if isinstance(record_numbers, int):
                record_numbers = [record_numbers]
            elif not isinstance(record_numbers, list):
                return df

        data_pull = self.__build_data_pull(record_numbers, data_request=data_request)
        assert self.__api_uri is not None, "Unable to read 'API_URL.'"
        self.__log.info("Requesting REDCap data.")
        response = requests.post(
            self.__api_uri, data=data_pull, verify=True, timeout=self.__timeout_sec
        )

        try:
            if (
                not response
                or response.status_code != 200
                or "study_id" not in response.text
            ):
                self.__log.info("No response in query for record %d.", record_numbers)
                return df
        except TypeError as error:  # pragma: no cover
            self.__log.exception("Unable to parse query response.")
            raise RuntimeError("Unable to parse query response.") from error

        df = pandas.json_normalize(response.json())
        self.__log.info("Received %d records.", len(df))
        return df

    def version(self) -> str:
        """
        Ask REDCap API for its software version number.

        Return
        ------
        str

        Examples
        --------
        >>> from src.redcapapi import REDCapInterface
        >>>
        >>>
        >>> redcap_interface_object = REDCapInterface()
        >>> print(f"Version = {redcap_interface_object.version()}")
        """
        fields = {"token": self.__capmc_token, "content": "version"}

        assert self.__api_uri is not None, "Unable to read 'API_URL.'"
        response = requests.post(
            self.__api_uri, data=fields, verify=True, timeout=self.__timeout_sec
        )

        if (
            not isinstance(response, requests.Response) or response.status_code != 200
        ):  # pragma: no cover
            self.__log.exception("Unable to query REDCap API for version.")
            raise RuntimeError("Unable to query REDCap API for version.")

        try:
            return str(response.text)
        except TypeError as error:  # pragma: no cover
            self.__log.exception("Unable to parse query response.")
            raise RuntimeError("Unable to parse query response.") from error


if __name__ == "__main__":  # pragma: no cover
    REDCap_object = REDCapInterface(isdev=True)
