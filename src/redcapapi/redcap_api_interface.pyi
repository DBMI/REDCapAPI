from typing import Union

import pandas  # type: ignore[import]

class REDCapInterface:
    def __init__(self, isdev: bool = ..., timeout_sec: int = ...) -> None:
        self.__timeout_sec = None
        self.__api_uri = None
        self.__capmc_token = None
        self.__discard_empty_fields = None
        self.__valid = None
        self.__isdev = None
        self.__log = None
        ...
    def create(self, data_records: Union[dict, pandas.DataFrame]) -> bool: ...
    def delete(self, record_number: int) -> bool: ...
    def exists(self, record_number: int) -> bool: ...
    def last_record_number(
        self, except_for: Union[int, list, None] = ..., number_desired: int = ...
    ) -> Union[int, list]: ...
    def next_record_number(self) -> int: ...
    def retrieve(
        self, record_numbers: Union[int, list, None] = ..., expanded_record: bool = ...
    ) -> pandas.DataFrame: ...
    def update(self, new_data_records: Union[dict, pandas.DataFrame] = ...) -> bool: ...
    def version(self) -> str: ...
    def __read_config_file(self) -> None:
        pass
    def __known_test_record_present(self) -> bool:
        pass
    def __build_data_pull(
        self, record_numbers: Union[list, None], expanded_record: bool
    ) -> dict:
        pass
    def __update_one_record(
        self, new_data_record: dict, existing_record: pandas.DataFrame
    ) -> bool:
        pass
