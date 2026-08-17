from setuptools import setup

setup(
    name="redcapapi",
    version="1.6.4",
    package_dir={"": "src"},
    packages=["redcapapi"],
    url="https://github.com/DBMI/REDCapAPI",
    license="",
    author="DBMI Team",
    author_email="kjdelaney@ucsd.edu",
    description="A Python wrapper around the REDCap API.",
    classifiers=[
        "Programming Language :: Python :: 3.12",
    ],
    install_requires=[
        "pandas >= 2.2.0",
        "requests >= 2.31.0",
    ],
)
