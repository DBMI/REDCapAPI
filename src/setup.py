from setuptools import setup

setup(
    name="redcap_api",
    version="1.3.7",
    package_dir={"": "src"},
    packages=["redcap_api"],
    url="https://github.com/DBMI/REDCapAPI",
    license="",
    author="DBMI Team",
    author_email="kjdelaney@ucsd.edu",
    description="A Python wrapper around the REDCap API.",
    classifiers=[
        "Programming Language :: Python :: 3.71",
    ],
    install_requires=[
        "pandas >= 1.3.5",
        "requests >= 2.27.1",
    ],
)
