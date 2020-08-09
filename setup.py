from setuptools import setup

setup(
    name='autoindex',
    version='0.1.0',
    py_modules=['autoindex'],
    install_requires=[
        'Click',
        'pdfminer.six',
        'PyPDF2'
    ],
    entry_points='''
        [console_scripts]
        autoindex=autoindex:cli
    ''',
)