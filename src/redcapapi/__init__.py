"""
REDCap API Calls

A wrapper around the REDCap API, allowing Python code to connect with the API.
"""

__version__ = "1.5.0"
__author__ = "DBMI Team"
__credits__ = str(
    "University of California San Diego"
    + "School of Medicine; Department of Biomedical Informatics"
)

from .redcap_api_interface import DataRequest  # type: ignore[import] # noqa: F401
from .redcap_api_interface import REDCapInterface  # type: ignore[import] # noqa: F401
