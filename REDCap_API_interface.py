import configparser
import json
import pandas as pd
import requests


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
    update(data_record)
        Overwrites the existing record at the study_id record number in the argument dict or dataframe.
        If there is no existing record with that study_id, creates a new record.
        Only overwrites the properties present in the input argument.
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

    def __init__(self, isdev=False):
        """
        Create instance of `REDCapInterface` class.

        Assumes using production data, but can be created with isdev=True to
        point to the development database.
        Gets database token from "F:\RedCap\secrets\config.key"

        Parameters
        ----------
        isdev : bool, optional
            Set when using development database (default is False)

        Return
        -------
        none; instantiates object

        Examples
        --------
        >>> from REDCap_API_interface import REDCapInterface
        >>>
        >>>
        >>> production_redcap_interface_object = REDCapInterface()
        >>> development_redcap_interface_object = REDCapInterface(isdev=True)
        """
        self.__api_uri = None
        self.__capmc_token = None
        self.__isdev = isdev
        self.__read_config_file()

        if self.__isdev and not self.__known_test_record_present():
            raise RuntimeError(
                "WARNING! Unable to find known test record."
                + "You might not be connected to the DEV database."
            )  # pragma: no cover

        # Lets all methods know that we're talking to the correct database.
        self.__valid = True

    def __build_data_pull(self, record_numbers=None, expanded_record=False):
        """
        Assemble dict used when retrieving data records.

        Parameters
        ----------
        record_numbers : int, list
            default is None (to retrieve ALL records)
            or user can provide a single record number or a list of numbers
        expanded_record : bool
            If true, returns all fields. Otherwise, just returns study_id, dob,
            primary_consent_date, core_participant_date, date_of_last_activity
            default is False

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

        # For now, restrict the fields to just this list
        #  ->unless<- we're in DEV mode AND "expanded_record" selected.
        if not self.__isdev or not expanded_record:
            pull_dict["fields[0]"] = ("study_id",)
            pull_dict["fields[1]"] = ("dob",)
            pull_dict["fields[2]"] = ("primary_consent_date",)
            pull_dict["fields[3]"] = ("core_participant_date",)
            pull_dict["fields[4]"] = ("date_of_last_activity",)

        if record_numbers is not None:
            # Insert into the dictionary a key for each desired record number.
            record_count = 0

            for record_number in record_numbers:
                record_name = f"records[, {record_count}, ]"
                pull_dict[record_name] = record_number
                record_count += 1

        return pull_dict

    def create(self, data_records):
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
        >>> from REDCap_API_interface import REDCapInterface
        >>>
        >>>
        >>> redcap_interface_object = REDCapInterface()
        >>> new_data = {'study_id': '12345', 'name': "Patient's Name", 'mrn': '000000', ...}
        >>> redcap_interface_object.create(new_data)
        """
        if not self.__valid:  # pragma: no cover
            return None

        if data_records is None:
            return None

        if isinstance(data_records, dict):
            data_records = [data_records]
        elif isinstance(data_records, pd.DataFrame):
            data_records = data_records.to_dict("records")
        else:
            return False

        data = json.dumps(data_records)

        fields = {
            "token": self.__capmc_token,
            "content": "record",
            "format": "json",
            "type": "flat",
            "data": data,
        }

        r = requests.post(self.__api_uri, data=fields)
        return r is not None and r.status_code == 200

    def delete(self, record_number):
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
        >>> from REDCap_API_interface import REDCapInterface
        >>>
        >>>
        >>> redcap_interface_object = REDCapInterface()
        >>> redcap_interface_object.delete(12345)
        """
        if not self.__valid:  # pragma: no cover
            return None

        if record_number is not None:
            fields = {
                "token": self.__capmc_token,
                "action": "delete",
                "content": "record",
                "records[0]": record_number,
            }

            r = requests.post(self.__api_uri, data=fields)
            return r is not None and r.status_code == 200

    def exists(self, record_number=None):
        """
        Test whether given record number exists in the database.

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
        >>> from REDCap_API_interface import REDCapInterface
        >>>
        >>>
        >>> redcap_interface_object = REDCapInterface()
        >>>
        >>> if redcap_interface_object.exists(record_number): ...
        """
        if not self.__valid:  # pragma: no cover
            return None

        data_pull = None

        if record_number is not None:
            if isinstance(record_number, int):
                data_pull = self.__build_data_pull([record_number])
            elif not isinstance(record_number, list):
                raise TypeError("Input 'record_number' is neither int nor list.")

            r = requests.post(self.__api_uri, data=data_pull, verify=True)

            try:
                return r.status_code == 200 and "study_id" in r.text
            except RuntimeError:  # pragma: no cover
                return False
        else:
            return False

    # Check for the presence of a known test record to be doubly sure we're connected to DEV_CAPMC_RECRUITMENT.
    def __known_test_record_present(self):
        """
        Test whether the known record inserted into the development database is present.

        If present, this confirms that we are connected to the development
        (and not the production) database.

        Return
        -------
        bool
        """
        test_record_number = 6393740  # pragma: no cover
        record = self.retrieve(test_record_number, expanded_record=True)

        if (
            record is None
            or not isinstance(record, pd.DataFrame)
            or "first_name" not in record
            or "last_name" not in record
        ):
            raise RuntimeError(
                "Unable to retrieve known test record."
                + "You might not be connected to the DEV database."
            )  # pragma: no cover

        return (
            record.iloc[0].first_name == "TESTER"
            and record.iloc[0].last_name == "TESTDATA"
        )

    def last_record_number(self, except_for=None, number_desired=1):
        """
        Lookup the highest record number (study_id) present in the database.

        Parameters
        ----------
        except_for : int, list
            Record numbers to skip over.
        number_desired : int, optional
            How many numbers to return. default is 1

        Return
        -------
        int or list of ints

        Examples
        --------
        >>> from REDCap_API_interface import REDCapInterface
        >>>
        >>>
        >>> redcap_interface_object = REDCapInterface()
        >>> highest_record_number_in_use = redcap_interface_object.last_record_number()
        """
        last_valid_record_number = self.next_record_number() - 1
        valid_record_numbers_found = []

        if except_for is not None:
            if isinstance(except_for, int):
                except_for = [except_for]
            elif not isinstance(except_for, list):  # pragma: no cover
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
                else:
                    raise RuntimeError(
                        "Unable to find any valid record numbers."
                    )  # pragma: no cover

            except_for.append(last_valid_record_number)
            valid_record_numbers_found.append(last_valid_record_number)

        if len(valid_record_numbers_found) == 1:
            return valid_record_numbers_found[0]
        else:
            return valid_record_numbers_found

    def next_record_number(self):
        """
        Lookup next available record number.

        Used when creating a new record.

        Return
        ------
        int

        Examples
        --------
        >>> from REDCap_API_interface import REDCapInterface
        >>>
        >>>
        >>> redcap_interface_object = REDCapInterface()
        >>> new_record_number = redcap_interface_object.next_record_number()
        """
        fields = {
            "token": self.__capmc_token,
            "content": "generateNextRecordName",
        }

        r = requests.post(self.__api_uri, data=fields)

        if r is None or r.status_code != 200:
            raise RuntimeError(
                "Unable to query for next record number."
            )  # pragma: no cover

        try:
            return int(r.text)
        except TypeError:  # pragma: no cover
            raise RuntimeError("Unable to parse next record number.")

    def __read_config_file(self):
        config = configparser.ConfigParser()

        if self.__isdev:
            config.read(r"F:\RedCap\secrets\config-dev.key")
        else:
            config.read(r"F:\RedCap\secrets\config.key")

        self.__api_uri = config.get("API", "API_URL")
        self.__capmc_token = config.get("CAPMC", "CAPMC_TOKEN")

    def retrieve(self, record_numbers=None, expanded_record=False):
        """
        Get particular record(s) or all the records.

        Parameters
        ----------
        record_numbers : int or list, optional
            If specified, returns just that/those record(s).
            If None or unspecified, returns all the records. default is None
        expanded_record : bool, optional
            If true, returns all the fields available. Otherwise, returns study_id, dob,
            primary_consent_date, core_participant_date, date_of_last_activity
            default is False

        Return
        ------
        dataframe

        Examples
        --------
        >>> from REDCap_API_interface import REDCapInterface
        >>>
        >>>
        >>> redcap_interface_object = REDCapInterface()
        >>> df_all = redcap_interface_object.retrieve()
        >>> df_selected = redcap_interface_object.retrieve([1234, 2345])
        """
        # No need to check for self.__valid here; it's always OK to retrieve records.
        if record_numbers is not None:
            if isinstance(record_numbers, int):
                record_numbers = [record_numbers]
            elif not isinstance(record_numbers, list):
                return None

        data_pull = self.__build_data_pull(
            record_numbers, expanded_record=expanded_record
        )
        r = requests.post(self.__api_uri, data=data_pull, verify=True)

        try:
            if not r or r.status_code != 200 or "study_id" not in r.text:
                raise RuntimeError("Unable to query REDCap API for records.")
        except TypeError:  # pragma: no cover
            raise RuntimeError("Unable to parse query response.")

        dates_df = pd.json_normalize(r.json())
        return dates_df

    def update(self, new_data_records=None):
        """
        Change an existing record.

        Since there is no native "update" method in the REDCap API, this wrapper method:
        1. makes two copies of the existing record: one to modify, one as a backup
        2. deletes the existing record
        3. modifies the copy of the existing record
        4. tries to insert the modified record into the database under the same study_id
        5. if the insert fails, tries to restore the backup copy of the record by inserting that into the database under the same study_id
        6. if unable to insert the backup, throws an exception

        Parameters
        ----------
        new_data_records : dict or dataframe

        Return
        ------
        dataframe

        Examples
        --------
        >>> from REDCap_API_interface import REDCapInterface
        >>>
        >>>
        >>> redcap_interface_object = REDCapInterface()
        >>> new_info = {'study_id': str(record_number_to_update),
        >>>             'date_of_last_activity': right_now}
        >>> redcap_interface_object.update(new_info)
        """
        if not self.__valid:  # pragma: no cover
            return None

        if isinstance(new_data_records, dict):
            new_data_records = [new_data_records]
        elif isinstance(new_data_records, pd.DataFrame):
            new_data_records = new_data_records.to_dict("records")
        elif not isinstance(new_data_records, list):
            raise TypeError("Input is neither a dict, list nor dataframe.")

        for new_data_record in new_data_records:
            # Get a copy of what's there now.
            record_number = int(new_data_record["study_id"])
            existing_record = self.retrieve(record_number, expanded_record=True)

            if existing_record is None or len(existing_record) == 0:
                # There's no match--so create a new one.
                if not self.create(new_data_record):  # pragma: no cover
                    raise RuntimeError("Unable to create new record.")
            else:
                # Delete existing record so that we'll be allowed to
                #  insert a record with the same record number.
                if self.delete(record_number):
                    draft_record = existing_record.copy()

                    # Overwrite our copy of what's currently in REDCap
                    #  with whatever properties we've been given.
                    for key in new_data_record:
                        # Not allowed to update the primary key "study_id".
                        if key != "study_id":
                            try:
                                new_value = new_data_record[key]
                                draft_record[key] = new_value

                            except KeyError:  # pragma: no cover
                                raise KeyError(
                                    f"Unable to update dataframe field {key}."
                                )

                    # Push the modified record.
                    if not self.create(draft_record):
                        # If that didn't work, we need to put the original record back.
                        if self.create(existing_record):
                            # Need to notify that update didn't work.
                            # However, we restored the original record.
                            raise RuntimeError(
                                "Unable to update; original record was restored."
                            )
                        else:  # pragma: no cover
                            # Ok, now we have a problem.
                            # We deleted the original record,
                            # are unable to insert the modified record,
                            # AND can't restore the deleted record.
                            raise RuntimeError("Unable to restore deleted record.")

            return True

    def version(self):
        """
        Ask REDCap API for its software version number.

        Return
        ------
        str

        Examples
        --------
        >>> from REDCap_API_interface import REDCapInterface
        >>>
        >>>
        >>> redcap_interface_object = REDCapInterface()
        >>> print(f"Version = {redcap_interface_object.version()}")
        """
        fields = {"token": self.__capmc_token, "content": "version"}

        r = requests.post(self.__api_uri, data=fields, verify=True)

        if not r or r.status_code != 200:  # pragma: no cover
            raise RuntimeError("Unable to query REDCap API for version.")

        try:
            return r.text
        except TypeError:  # pragma: no cover
            raise RuntimeError("Unable to parse query response.")


if __name__ == "__main__":  # pragma: no cover
    REDCap_object = REDCapInterface(isdev=True)
