import configparser
import json
import os
import pandas as pd
import requests


class REDCapInterface:
    def __init__(self, _isdev=False):
        self.API_URL = None
        self.CAPMC_TOKEN = None
        self.RECORDS_PER_PAYLOAD = 100
        self.isdev = _isdev
        self._read_config_file()

        if self.isdev and not self._known_test_record_present():
            raise RuntimeError("WARNING! Unable to find known test record." +
                               "You might not be connected to the DEV database.")  # pragma: no cover

        # Lets all methods know that we're talking to the correct database.
        self.valid = True

    def _build_data_pull(self, record_numbers=None, expanded_record=False):
        # NOT specifying the "fields" list ==> give me ALL the fields.
        pull_dict = {
            'token': self.CAPMC_TOKEN,
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'csvDelimiter': '',
            'rawOrLabel': 'raw',
            'rawOrLabelHeaders': 'raw',
            'exportCheckboxLabel': 'false',
            'exportSurveyFields': 'false',
            'exportDataAccessGroups': 'false',
            'returnFormat': 'json'
        }

        # For now, restrict the fields to just this list
        #  ->unless<- we're in DEV mode AND "expanded_record" selected.
        if not self.isdev or not expanded_record:
            pull_dict['fields[0]'] = 'study_id',
            pull_dict['fields[1]'] = 'dob',
            pull_dict['fields[2]'] = 'primary_consent_date',
            pull_dict['fields[3]'] = 'core_participant_date',
            pull_dict['fields[4]'] = 'date_of_last_activity',

        if record_numbers:
            # Insert into the dictionary a key for each desired record number.
            record_count = 0

            for record_number in record_numbers:
                record_name = f"records[, {record_count}, ]"
                pull_dict[record_name] = record_number
                record_count += 1

        return pull_dict

    def create(self, data_records):
        if not self.valid:  # pragma: no cover
            return None

        if data_records is None:
            return None

        if isinstance(data_records, dict):
            data_records = [data_records]
        elif isinstance(data_records, pd.DataFrame):
            data_records = data_records.to_dict('records')
        else:
            return False

        data = json.dumps(data_records)

        fields = {
            'token': self.CAPMC_TOKEN,
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'data': data,
        }

        r = requests.post(self.API_URL, data=fields)
        return r is not None and r.status_code == 200

    def delete(self, record_number):
        if not self.valid:  # pragma: no cover
            return None

        if record_number:
            fields = {
                'token': self.CAPMC_TOKEN,
                'action': 'delete',
                'content': 'record',
                'records[0]': record_number
            }

            r = requests.post(self.API_URL, data=fields)
            return r is not None and r.status_code == 200

    def exists(self, record_number=None):
        if not self.valid:  # pragma: no cover
            return None

        if record_number:
            if isinstance(record_number, int):
                data_pull = self._build_data_pull([record_number])
            elif not isinstance(record_number, list):
                raise TypeError("Input 'record_number' is neither int nor list.")

            r = requests.post(self.API_URL, data=data_pull, verify=True)

            try:
                return r.status_code == 200 and 'study_id' in r.text
            except RuntimeError:  # pragma: no cover
                return False
        else:
            return False

    # Check for the presence of a known test record to be doubly sure we're connected to DEV_CAPMC_RECRUITMENT.
    def _known_test_record_present(self):
        test_record_number = 6393740  # pragma: no cover
        record = self.retrieve(test_record_number, expanded_record=True)

        if record is None or not isinstance(record, pd.DataFrame) \
                or 'first_name' not in record or 'last_name' not in record:
            raise RuntimeError("Unable to retrieve known test record." +
                               "You might not be connected to the DEV database.")  # pragma: no cover

        return record.iloc[0].first_name == 'TESTER' and record.iloc[0].last_name == 'TESTDATA'

    def last_record_number(self, except_for=None):
        last_valid_record_number = self.next_record_number() - 1

        while not self.exists(last_valid_record_number) or last_valid_record_number == except_for:
            if last_valid_record_number > 0:
                last_valid_record_number -= 1
            else:
                raise RuntimeError("Unable to find any valid record numbers.")  # pragma: no cover

        return last_valid_record_number

    def next_record_number(self):
        fields = {
            'token': self.CAPMC_TOKEN,
            'content': 'generateNextRecordName',
        }

        r = requests.post(self.API_URL, data=fields)

        if r is None or r.status_code != 200:
            raise RuntimeError("Unable to query for next record number.")  # pragma: no cover

        try:
            return int(r.text)
        except TypeError:  # pragma: no cover
            raise RuntimeError("Unable to parse next record number.")

    def _read_config_file(self):
        config = configparser.ConfigParser()

        if self.isdev:
            config.read('F:\RedCap\secrets\config-dev.key')
        else:
            config.read('F:\RedCap\secrets\config.key')

        self.API_URL = config.get('API', 'API_URL')
        self.CAPMC_TOKEN = config.get('CAPMC', 'CAPMC_TOKEN')

    def retrieve(self, record_numbers=None, expanded_record=False):
        # No need to check for self.valid here; it's always OK to retrieve records.
        if record_numbers:
            if isinstance(record_numbers, int):
                record_numbers = [record_numbers]
            elif not isinstance(record_numbers, list):
                return None

        data_pull = self._build_data_pull(record_numbers, expanded_record=expanded_record)
        r = requests.post(self.API_URL, data=data_pull, verify=True)

        if not r or r.status_code != 200 or "study_id" not in r.text:
            raise RuntimeError("Unable to query REDCap API for records.")

        dates_df = pd.json_normalize(r.json())
        return dates_df

    def update(self, new_data_records=None):
        if not self.valid:  # pragma: no cover
            return None

        if isinstance(new_data_records, pd.DataFrame):
            new_data_records = [new_data_records]
        elif not isinstance(new_data_records, list):
            raise TypeError("Input is neither a single dict nor a list of dict objects.")

        for new_data_record in new_data_records:
            # Get a copy of what's there now.
            record_number = int(new_data_record['study_id'][0])
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

                                if isinstance(new_value, pd.Series):
                                    new_value = new_value[0]

                                draft_record[key] = new_value

                            except KeyError:  # pragma: no cover
                                raise KeyError(f"Unable to update dataframe field {key}.")

                    # Push the modified record.
                    if not self.create(draft_record):
                        # If that didn't work, we need to put the original record back.
                        if self.create(existing_record):
                            # Need to notify that update didn't work.
                            # However, we restored the original record.
                            raise RuntimeError("Unable to update; original record was restored.")
                        else:  # pragma: no cover
                            # Ok, now we have a problem.
                            # We deleted the original record,
                            # are unable to insert the modified record,
                            # AND can't restore the deleted record.
                            raise RuntimeError("Unable to restore deleted record.")

            return True

    def version(self):
        fields = {
            'token': self.CAPMC_TOKEN,
            'content': 'version'
        }

        r = requests.post(self.API_URL, data=fields, verify=True)

        if not r or r.status_code != 200: # pragma: no cover
            raise RuntimeError("Unable to query REDCap API for version.")

        return r.text


if __name__ == '__main__':  # pragma: no cover
    REDCap_object = REDCapInterface(True)
