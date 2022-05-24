[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Pylint](./.github/badges/pylint-badge.svg?dummy=8484744)
![Coverage Status](./.github/badges/coverage-badge.svg?dummy=8484744)
![Last Commit Date](./.github/badges/last-commit-badge.svg?dummy=8484744)

[GitHub Pages site](https://dbmi.github.io/REDCap_API_Calls/index.html)
# How to use `REDCapInterface` class to connect with REDCap API

## Obtaining a token
You will need to generate a token for yourself in the CAPMC project in REDCap. Click _API_ in the REDCap menu...:

![image info](./pictures/select_API.png)

...and then click _Request API token_:

![image info](./pictures/request_token.png)

Copy the file `config-example.key` to `F:\RedCap\secrets\config.key`. Put your token into `config.key` and save the file.

## Installing the `dbmi_redcap` package
`pip install git+https://github.com/DBMI/REDCAP_API_Calls.git`

This will allow you to import the `REDCapInterface` class within python:
`from dbmi_redcap import REDCapInterface`
## Using the `REDCapInterface` Class
### CREATE
To create a new record, instantiate an object of the `REDCapInterface` class and call its `create` method, supplying a `dict` or `pandas.DataFrame` object:

    from dbmi_redcap import REDCapInterface


    redcap_interface_object = REDCapInterface()
    new_data = {'study_id': '12345', 'name': "Patient's Name", 'mrn': 000000, ...}
    redcap_interface_object.create(new_data)

### RETRIEVE
To retrieve _all_ records, instantiate an object of the `REDCapInterface` class and call its `retrieve` method with no records specified:

    from dbmi_redcap import REDCapInterface


    redcap_interface_object = REDCapInterface()
    df = redcap_interface_object.retrieve()

To retrieve selected records, specify a list of record numbers:

    df = redcap_interface_object.retrieve([20, 22])

Or to retrieve just one record by record number:

    df = redcap_interface_object.retrieve(42)
### UPDATE
To update an existing record, instantiate an object of the `REDCapInterface` class and call its `update` method, supplying a `dict` or `pandas.DataFrame` object containing the `study_id` of the record to be modified, along with any updated fields.:

    from dbmi_redcap import REDCapInterface


    redcap_interface_object = REDCapInterface()
    new_info = {'study_id': str(record_number_to_update),
                'date_of_last_activity': right_now}
    redcap_interface_object.update(new_info)
### DELETE
Use the `delete` method of the `REDCapInterface` class, specifying the record number (`study_id`) of the record to be deleted:

    from dbmi_redcap import REDCapInterface


    redcap_interface_object = REDCapInterface()
    redcap_interface_object.delete(record_number_to_delete)
### HELPER FUNCTIONS
To determine whether a specific record is present in the database, use the `exists()` method:

    from dbmi_redcap import REDCapInterface


    redcap_interface_object = REDCapInterface()

    if redcap_interface_object.exists(record_number): ...

To assist in creating a new record, look up the next available record number using the `next_record_number` method:

    from dbmi_redcap import REDCapInterface


    redcap_interface_object = REDCapInterface()
    new_record_number = redcap_interface_object.next_record_number()

This `new_record_number` is guaranteed _not_ to exist. The highest record number that _does_ exist is found with the `last_record_number` method:

    from dbmi_redcap import REDCapInterface


    redcap_interface_object = REDCapInterface()
    highest_record_number_in_use = redcap_interface_object.last_record_number()

To check what software version is used in the REDCapAPI, use the `version` method:

    from dbmi_redcap import REDCapInterface


    redcap_interface_object = REDCapInterface()
    print(f"Version = {redcap_interface_object.version()}")
