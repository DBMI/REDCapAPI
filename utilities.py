from datetime import datetime
import re


def convert_to_date(date_string):
    # Remove leading/trailing whitespace.
    date_string = date_string.strip().replace(r" [\d]{2}:[\d]{2}:[\d]{2}", "").strip()

    if date_string == "":
        return None
    elif re.match(r"[\d]{1,2}/[\d]{1,2}/[\d]{4}", date_string):  # Match 01/31/1970
        return datetime.strptime(date_string, '%m/%d/%Y')
    elif re.match(r"[\d]{1,2}/[\d]{1,2}/[\d]{2}", date_string):  # Match 01/31/70
        return datetime.strptime(date_string, '%m/%d/%y')
    elif re.match(r"[\d]{1,2}-[\d]{1,2}-[\d]{4}", date_string):  # Match 01-31-1970
        return datetime.strptime(date_string, '%m-%d-%Y')
    elif re.match(r"[\d]{1,2}-[\d]{1,2}-[\d]{2}", date_string):  # Match 01-31-70
        return datetime.strptime(date_string, '%m-%d-%y')
    elif re.match(r"[\d]{4}-[\d]{1,2}-[\d]{1,2} [\d]{2}:[\d]{2}:[\d]{2}", date_string):  # Match 1970-01-31 12:05:10
        return datetime.strptime(date_string, '%Y-%m-%d  %H:%M:%S')
    elif re.match(r"[\d]{4}-[\d]{1,2}-[\d]{1,2}", date_string):  # Match 1970-01-31
        return datetime.strptime(date_string, '%Y-%m-%d')
    elif re.match(r"[\d]{1,2} [A-Z]{1}[a-z]{2} [\d]{4}", date_string):  # Match 31 Jan 1970
        return datetime.strptime(date_string, '%d %b %Y')
    elif re.match(r"[A-Z]{1}[a-z]{2} +[\d]{1,2} [\d]{4} 12:00AM", date_string):  # Match Jan 31 1970 12:00AM
        return datetime.strptime(date_string.replace(" 12:00AM", ""), '%b %d %Y')
    else:
        print("WE HAVE A PROBLEM WITH THIS DATE: ", date_string)
        return None
