import re
from faker import Faker
from REDCap_API_interface import REDCapInterface


def anonymize_database():
    redcap_interface_object = REDCapInterface(False)
    df = redcap_interface_object.retrieve([6345966, 6345949])

    fake = Faker()

    for index, row in df.iterrows():
        birthdate = fake.date_of_birth(minimum_age=18, maximum_age=115)
        df.at[index, 'dob'] = birthdate.strftime("%m/%d/%y")
        df.at[index, 'dob_dt'] = birthdate
        primary_consent_date = fake.date_between(birthdate)
        df.at[index, 'primary_consent_date'] = primary_consent_date.strftime("%m/%d/%y")
        df.at[index, 'primary_consent_date_dt'] = primary_consent_date
        date_of_last_activity = fake.date_between(primary_consent_date)
        df.at[index, 'date_of_last_activity'] = date_of_last_activity.strftime("%m/%d/%y")
        df.at[index, 'date_of_last_activity_dt'] = date_of_last_activity
        core_participant_date = fake.date_between(primary_consent_date)
        df.at[index, 'core_participant_date'] = core_participant_date.strftime("%m/%d/%y")
        df.at[index, 'core_participant_date_dt'] = core_participant_date
        df.at[index, 'mrn'] = str(fake.random_int(min=100000, max=500000))
        df.at[index, 'first_name'] = fake.first_name()
        df.at[index, 'last_name'] = fake.last_name()
        df.at[index, 'preferred_name'] = fake.first_name()
        df.at[index, 'dob_2'] = birthdate.strftime("%y-%m-%d")
        patient_dead = False

        # Only include death date occasionally.
        if fake.random_int(min = 0, max = 9) > 7:
            latest_date = max([date_of_last_activity, core_participant_date])
            df.at[index, 'death_datetime'] = fake.date_between(latest_date).strftime("%m/%d/%y")
            patient_dead = True

        df.at[index, 'first_name_from_hp'] = df.at[index, 'first_name']
        df.at[index, 'last_name_from_hp']= df.at[index, 'last_name']
        df.at[index, 'sex'] = fake.random_int(min = 1, max=3)
        df.at[index, 'race'] = fake.random_int(min=1, max=5)
        df.at[index, 'ethnicity'] = fake.random_int(min=1, max=2)
        address_pieces = re.split(',|\n', fake.address(), maxsplit=1)
        df.at[index, 'street_address_line_1'] = address_pieces[0].strip()
        df.at[index, 'street_address_line_2'] = address_pieces[1].strip()
        df.at[index, 'email_address'] = fake.email()

        # Once in a while change the email
        if fake.random_int(min=0, max=9) > 8:
            df.at[index, 'new_email_address'] = fake.email()

        phone_number = fake.phone_number()
        df.at[index, 'phone_number'] = phone_number

        # Once in a while change the phone number
        if fake.random_int(min=0, max=9) > 8:
            df.at[index, 'new_phone_number'] = fake.phone_number()

        df.at[index, 'physician'] = fake.name()

        if patient_dead:
            df.at[index, 'appointment_date'] = None
            df.at[index, 'appointment_time'] = None
        else:
            appointment_datetime = fake.date_this_year(before_today=False, after_today=True)
            df.at[index, 'appointment_date'] = appointment_datetime.strftime("%m/%d/%y")
            df.at[index, 'appointment_time'] = appointment_datetime.strftime("%H:%M")

        df.at[index, 'date_added'] = fake.past_datetime(start_date='-5d')
        df.at[index, 'pmi_id'] = str(fake.random_int(min=100000, max=500000))


if __name__ == '__main__':
    anonymize_database()
