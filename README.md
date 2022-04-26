## HOW TO USE CODE

You will need to generate a token for yourself in the CAPMC project in REDCap. Click _API_ in the REDCap menu:

![image info](./pictures/api.png)

Copy the file `config-example.env` to `config.env`. Put your token into `config.env` and save.

To use the `REDCapInterface` class to retrieve _all_ records, call its `retrieve` method with no records specified:

    from REDCap_API_interface import REDCapInterface

    
    redcap_interface_object = REDCapInterface()
    df = redcap_interface_object.retrieve()

To retrieve selected records, specify a list of record numbers:

    df = redcap_interface_object.retrieve([20, 22])

Or to retrieve just one record by record number:

    df = redcap_interface_object.retrieve(42)