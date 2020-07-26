from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO
from PyPDF2 import PdfFileWriter, PdfFileReader
from typing import List

import re


PAGE_NUMBER_REGEX = r"(\d+)$"

TOC_LA_PARAMS = LAParams(
    char_margin=500.0
)

def add_index(filename: str, output_filename: str, toc_page_numbers: List[int], offset: int) -> None:
    resource_manager = PDFResourceManager()
    codec = 'utf-8'

    with open(filename, 'rb') as pdf:
        output_file_writer = PdfFileWriter()
        input_file = PdfFileReader(pdf)
        for page in input_file.pages:
            output_file_writer.addPage(page)

        pages = list(PDFPage.get_pages(pdf))
        toc_pages = [(toc_index, pages[toc_index]) for toc_index in toc_page_numbers]

        with open(output_filename, 'wb') as output_file:
            for index, (toc_page_num, toc_page) in enumerate(toc_pages):
                buffer = StringIO()
                device = TextConverter(resource_manager, buffer, codec=codec, laparams=TOC_LA_PARAMS)
                interpreter = PDFPageInterpreter(resource_manager, device)
                interpreter.process_page(toc_page)
                toc_contents = buffer.getvalue().split('\n\n')
                contents = list(map(lambda x: re.search(PAGE_NUMBER_REGEX, x), toc_contents))
                contents = list(filter(None.__ne__, contents))
                for content in contents:
                    name = content.string[:content.start()].strip()
                    location = int(content[0].strip()) + offset
                    output_file_writer.addBookmark(name, location, parent=None)
            output_file_writer.write(output_file)