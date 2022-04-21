import configparser
import json
import pandas as pd
import requests
from utilities import convert_to_date


class REDCapInterface:
    def __init__(self, isdev=False):
        config = configparser.ConfigParser()

        if isdev:
            config.read('config-dev.env')
        else:
            config.read('config.env')

        self.API_URL = config.get('API', 'API_URL')
        self.CAPMC_TOKEN = config.get('CAPMC', 'CAPMC_TOKEN')
        self.RECORDS_PER_PAYLOAD = 100

    @staticmethod
    def build_data_payload(study_id, dob, pcd, cpd, dla):
        # BUILD A SINGLE JSON ENTRY FOR THE PAYLOAD OBJECT
        if dob is None and pcd is None and cpd is None and dla is None:
            return ""
        else:
            payload_entry = "{\"study_id\":" + study_id

            if dob is not None:
                payload_entry = payload_entry + ",\"dob_2\":\"" + dob.strftime("%Y-%m-%d") + "\""
            if pcd is not None:
                payload_entry = payload_entry + ",\"primary_consent_date_2\":\"" + pcd.strftime("%Y-%m-%d") + "\""
            if cpd is not None:
                payload_entry = payload_entry + ",\"core_participant_date_2\":\"" + cpd.strftime("%Y-%m-%d") + "\""
            if dla is not None:
                payload_entry = payload_entry + ",\"date_of_last_activity_2\":\"" + dla.strftime("%Y-%m-%d") + "\""
            payload_entry = payload_entry + "}"

            return payload_entry

    def build_data_pull(self, record_numbers=None):
        pull_dict = {
            'token': self.CAPMC_TOKEN,
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'csvDelimiter': '',
            'fields[0]': 'study_id',
            'fields[1]': 'dob',
            'fields[2]': 'primary_consent_date',
            'fields[3]': 'core_participant_date',
            'fields[4]': 'date_of_last_activity',
            'rawOrLabel': 'raw',
            'rawOrLabelHeaders': 'raw',
            'exportCheckboxLabel': 'false',
            'exportSurveyFields': 'false',
            'exportDataAccessGroups': 'false',
            'returnFormat': 'json'
        }

        if record_numbers:
            # Insert into the dictionary a key for each desired record number.
            record_count = 0

            for record_number in record_numbers:
                record_name = f"records[, {record_count}, ]"
                pull_dict[record_name] = record_number
                record_count += 1

        return pull_dict

    def create(self, data_records):
        count_total = 0
        count_with_dates = 0
        payload = []

        for i in data_records.index:
            count_total += 1
            dob = convert_to_date(data_records['dob'][i])
            pcd = convert_to_date(data_records['primary_consent_date'][i])
            cpd = convert_to_date(data_records['core_participant_date'][i])
            dla = convert_to_date(data_records['date_of_last_activity'][i])
            payload_entry = self.build_data_payload(data_records['study_id'][i], dob, pcd, cpd, dla)

            if payload_entry != "":
                count_with_dates += 1

                if count_with_dates % self.RECORDS_PER_PAYLOAD == 1:
                    payload = "[" + payload_entry + ", "
                elif (count_with_dates % self.RECORDS_PER_PAYLOAD == 0) or \
                     (count_total == data_records.shape[0]):
                    # Finish up this chunk of records.
                    payload = payload + payload_entry + "]"

                    # Wrap with token.
                    data_push = {
                        'token': self.CAPMC_TOKEN,
                        'content': 'record',
                        'format': 'json',
                        'type': 'flat',
                        'overwriteBehavior': 'normal',
                        'data': payload,
                        'returnContent': 'count',
                        'returnFormat': 'json'
                    }

                    # Send off to the API.
                    r = requests.post(self.API_URL, data=data_push, verify=True)

                    if not r or r.status_code != 200:
                        raise Exception("Unable to post records to REDCap API.")

                else:
                    payload = payload + payload_entry + ", "

    def delete(self, record_number):
        if record_number:
            fields = {
                'token': self.CAPMC_TOKEN,
                'action': 'delete',
                'content': 'record',
                'records[0]': record_number
            }

            r = requests.post(self.API_URL, data=fields)
            return r is not None and r.status_code == 200

    def insert(self, new_data_record=None):
        if new_data_record:
            data = json.dumps([new_data_record])

            fields = {
                'token': self.CAPMC_TOKEN,
                'content': 'record',
                'format': 'json',
                'type': 'flat',
                'data': data,
            }

            r = requests.post(self.API_URL, data=fields)
            return r is not None and r.status_code == 200

    def retrieve(self, record_numbers=None):
        if record_numbers:
            if isinstance(record_numbers, int):
                record_numbers = [record_numbers]
            elif not isinstance(record_numbers, list):
                return []

        data_pull = self.build_data_pull(record_numbers)
        r = requests.post(self.API_URL, data=data_pull, verify=True)

        if not r or r.status_code != 200:
            raise Exception("Unable to query REDCap API for records.")

        dates_df = pd.json_normalize(r.json())

        # Convert strings to new fields in datetime format.
        dates_df['dob_dt'] = dates_df['dob'].apply(convert_to_date)
        dates_df['primary_consent_date_dt'] = dates_df['primary_consent_date'].apply(convert_to_date)
        dates_df['core_participant_date_dt'] = dates_df['core_participant_date'].apply(convert_to_date)
        dates_df['date_of_last_activity_dt'] = dates_df['date_of_last_activity'].apply(convert_to_date)
        return dates_df

    def update(self, new_data_records=None):
        for new_data_record in new_data_records:
            # Get a copy of what's there now.
            record_number = new_data_record['record']
            existing_record = self.retrieve(record_number)

            if existing_record is None:
                # There's no match--so create a new one.
                if not self.insert(new_data_record):
                    raise Exception("Unable to insert new record.")
            else:
                # Delete existing record so that we'll be allowed to
                #  insert a record with the same record number.
                if self.delete(record_number):
                    draft_record = existing_record.copy()

                    # Overwrite our copy of what's currently in REDCap
                    #  with the properties we've been given.
                    for key in new_data_record:
                        draft_record[key] = new_data_record[key]

                    # Push the modified record.
                    if not self.insert(draft_record):
                        # If that didn't work, we need to put the original record back.
                        if self.insert(existing_record):
                            # Need to notify that update didn't work.
                            # However, we restored the original record.
                            raise Exception("Unable to update; original record was restored.")
                        else:
                            # Ok, now we have a problem.
                            # We deleted the original record,
                            # are unable to insert the modified record,
                            # AND can't restore the deleted record.
                            raise Exception("Unable to restore deleted record.")

            return True

    def version(self):
        fields = {
            'token': self.CAPMC_TOKEN,
            'content': 'version'
        }

        r = requests.post(self.API_URL, data=fields, verify=True)

        if not r or r.status_code != 200:
            raise Exception("Unable to query REDCap API for version.")

        return r.text


if __name__ == '__main__':
    REDCap_object = REDCapInterface(True)
