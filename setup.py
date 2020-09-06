from setuptools import setup

with open('readme.md', 'r') as readme:
  long_desc = readme.read()

setup(
    name='autoindex',
    version='0.3.0',
    py_modules=['autoindex'],
    packages = ['', 'modules'],
    install_requires=[
        'Click',
        'pdfminer.six',
        'PyPDF2'
    ],
    description = 'A cli tool to automatically add bookmarks to PDFs',
    long_description = long_desc,
    long_description_content_type='text/markdown',
    author = 'Suyash Behera',
    author_email = 'sne9x@outlook.com',
    url = 'https://github.com/Suyash458/autoindex',
    download_url = 'https://github.com/Suyash458/autoindex/archive/master.zip',
    keywords = ['PDF', 'PyPDF', 'pdfminer', 'bookmarks', 'cli'],
    entry_points='''
        [console_scripts]
        autoindex=autoindex:cli
    ''',
)