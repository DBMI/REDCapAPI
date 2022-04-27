from datetime import datetime
import re


def convert_to_date(date_string):
    # Remove leading/trailing whitespace.
    date_string = date_string.strip()

    # Remove commas so that "Jan 31, 1970" becomes "Jan 31 1970".
    date_string = date_string.replace(",", "")

    if date_string == "" or len(date_string) < 1:
        return None
    elif not re.search(r"\d", date_string):                 # if there are NO digits
        return None
    elif re.match(r"\d{1,2}/\d{1,2}/\d{4}", date_string):  # Match 01/31/1970
        return datetime.strptime(date_string, '%m/%d/%Y')
    elif re.match(r"\d{1,2}/\d{1,2}/\d{2}", date_string):  # Match 01/31/70
        return datetime.strptime(date_string, '%m/%d/%y')
    elif re.match(r"\d{1,2}-\d{1,2}-\d{4}", date_string):  # Match 01-31-1970
        return datetime.strptime(date_string, '%m-%d-%Y')
    elif re.match(r"\d{1,2}-\d{1,2}-\d{2}", date_string):  # Match 01-31-70
        try:
            return datetime.strptime(date_string, '%m-%d-%y')
        except ValueError:
            return datetime.strptime(date_string, '%y-%m-%d')

    elif re.match(r"\d{4}-\d{1,2}-\d{1,2}\s+\d{2}:\d{2}:\d{2}", date_string):  # Match 1970-01-31 12:05:10
        return datetime.strptime(date_string, '%Y-%m-%d  %H:%M:%S')
    elif re.match(r"\d{4}-\d{1,2}-\d{1,2}", date_string):  # Match 1970-01-31
        return datetime.strptime(date_string, '%Y-%m-%d')
    elif re.match(r"\d{1,2}\s+[A-Z][a-z]{2}\s+\d{4}", date_string):  # Match 31 Jan 1970
        return datetime.strptime(date_string, '%d %b %Y')
    elif re.match(r"[A-Z][a-z]{2}\s+\d{1,2}\s+\d{4} 12:00AM", date_string):  # Match Jan 31 1970 12:00AM
        return datetime.strptime(date_string.replace(" 12:00AM", ""), '%b %d %Y')
    elif re.match(r"[A-Z][a-z]{2}\s?\d{1,2}\s+\d{4}", date_string):  # Match Jan 31 1970
        return datetime.strptime(date_string, '%b %d %Y')
    else:
        print(f"WE HAVE A PROBLEM WITH THIS DATE: {date_string}")
        return None
