"""
Module utilities. Provides place for needed static methods.
"""
from datetime import datetime
from typing import Union
import re


def convert_to_date(date_string: str) -> Union[datetime, None]:
    """
    Convert strings to datetime objects.

    Converts string like "Jan 31, 1970" to datetime.datetime(1970, 1, 31, 0, 0).
    Attempts to cover every format variation we've seen in input data.

    Parameters
    ----------
    date_string : str
        String of date and (possibly) time information.

    Return
    -------
    datetime.datetime
        Value contained in the input date/time string.

    Examples
    --------
    >>> d = convert_to_date("Apr 28, 2022")
    >>> d
    >>> datetime.datetime(2022, 4, 28, 0, 0)
    """

    # Remove leading/trailing whitespace.
    date_string = date_string.strip()

    # Remove commas so that "Jan 31, 1970" becomes "Jan 31 1970".
    date_string = date_string.replace(",", "")

    # Reject if input is empty or does not contain any digits.
    if date_string == "" or len(date_string) < 1 or not re.search(r"\d", date_string):
        return None

    # Build a list of tuples: (regex pattern, format string).
    date_translations = []

    # Match 01/31/1970, 01-31-1970
    pattern = re.compile(r"(?P<month>\d{1,2})[/-](?P<day>\d{1,2})[/-](?P<year>\d{4})")
    four_digit_year_format = "%Y-%m-%d"
    date_translations.append((pattern, four_digit_year_format))

    # Match 01/31/70 or 01-31-70
    pattern = re.compile(r"(?P<month>\d{1,2})[/-](?P<day>\d{1,2})[/-](?P<year>\d{2})")
    two_digit_year_format = "%y-%m-%d"
    date_translations.append((pattern, two_digit_year_format))

    # Match 1970/01/31 12:05:10 or 1970-01-31 12:05:10
    pattern = re.compile(
        r"(?P<year>\d{4})[/-](?P<month>\d{1,2})[/-](?P<day>\d{1,2})"
        r"\s+(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})"
    )
    date_and_time_format = "%Y-%m-%d  %H:%M:%S"
    date_translations.append((pattern, date_and_time_format))

    # Match 1970-01-31
    pattern = re.compile(
        r"(?P<year>\d{4})[/-](?P<month>[/-]\d{1,2})[/-](?P<day>\d{1,2})"
    )
    date_translations.append((pattern, four_digit_year_format))

    # Match 70/01/31 or 70-01-31
    pattern = re.compile(r"(?P<year>\d{2})[/-](?P<month>\d{1,2})[/-](?P<day>\d{1,2})")
    date_translations.append((pattern, two_digit_year_format))

    # Match 31 Jan 1970
    pattern = re.compile(
        r"(?P<day>\d{1,2})\s+(?P<month>[A-Z][a-z]{2})\s+(?P<year>\d{4})"
    )
    y4_mon_d_format = "%Y-%b-%d"
    date_translations.append((pattern, y4_mon_d_format))

    # Match Jan 31 1970
    pattern = re.compile(
        r"(?P<month>[A-Z][a-z]{2})\s?(?P<day>\d{1,2})\s+(?P<year>\d{4})"
    )
    date_translations.append((pattern, y4_mon_d_format))

    for pattern, datetime_format in date_translations:
        search_result = pattern.search(date_string)

        if search_result:
            # First try creating datetime including hour:min:sec, which might not be present.
            try:
                return datetime.strptime(
                    search_result.group("year")
                    + "-"
                    + search_result.group("month")
                    + "-"
                    + search_result.group("day")
                    + " "
                    + search_result.group("hour")
                    + ":"
                    + search_result.group("min")
                    + ":"
                    + search_result.group("sec"),
                    datetime_format,
                )
            except ValueError:
                pass  # pragma: no cover
            except IndexError:
                # Fallback to just date.
                try:
                    return datetime.strptime(
                        search_result.group("year")
                        + "-"
                        + search_result.group("month")
                        + "-"
                        + search_result.group("day"),
                        datetime_format,
                    )
                except ValueError:
                    pass

    return None


if __name__ == "__main__":  # pragma: no cover
    pass
