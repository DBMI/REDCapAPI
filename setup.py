from setuptools import setup

setup(
    name='redcap_api',
    version='1.0.0',
    packages=['tests'],
    url='https://github.com/DBMI/REDCap_API_Calls',
    license='',
    author='DBMI Team',
    author_email='kjdelaney@ucsd.edu',
    description='A Python wrapper around the REDCap API.',
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=['pandas >= 1.3.5',
                      'requests >= 2.27.1',
                      ],
)
