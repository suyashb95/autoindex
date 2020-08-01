from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.high_level import extract_pages
from io import StringIO
from PyPDF2 import PdfFileWriter, PdfFileReader
from typing import List, Dict
from pdfminer.layout import LTChar, LTTextBox
from statistics import mean

import re
import pprint

Bookmark = Dict[LTTextBox, Bookmark]

PAGE_NUMBER_REGEX = r" (\d+)$"

TOC_LA_PARAMS = LAParams(
    char_margin=500.0,
    line_margin=0.15
)

HEADER_FONT_SIZE_THRESHOLD = 0.4
FONT_SIZE_THRESHOLD = 0.095
BACKWARD_INDENT_OFFSET = 0.5


def font_size(line) -> float:
    chars = list(filter(LTChar.__instancecheck__, line))
    return mean(list(map(lambda x: x.height, chars)))

def construct_top_level_bookmarks(bookmarks: List[LTTextBox]) -> Bookmark:
    return {
        bookmark: {} for bookmark in bookmarks
    }

def construct_bookmark_tree_using_fontsize(bookmarks: List[LTTextBox], running_index: int) -> (Bookmark, int):
    current_level_nodes = {}
    while running_index < len(bookmarks) - 1:
        current_node = bookmarks[running_index]
        children = {}
        if font_size(current_node) - font_size(bookmarks[running_index + 1]) >= HEADER_FONT_SIZE_THRESHOLD:
            children, running_index = construct_bookmark_tree_using_fontsize(bookmarks, running_index + 1)
        elif abs(font_size(bookmarks[running_index + 1]) - font_size(current_node)) >= FONT_SIZE_THRESHOLD:
            current_level_nodes[current_node] = {}
            return current_level_nodes, running_index + 1
        else:
            running_index += 1
        current_level_nodes[current_node] = children
    return current_level_nodes, running_index

def add_bookmarks(bookmarks: List, pdf, offset=0, parent=None):
    for bookmark in bookmarks:
        content = re.search(PAGE_NUMBER_REGEX, bookmark.get_text())
        name = content.string[:content.start()].strip()
        location = int(content[0].strip()) + offset          
        new_parent = pdf.addBookmark(name, location, parent=parent)
        add_bookmarks(bookmarks[bookmark], pdf, offset, new_parent)
    return pdf

def add_index(
        input_filename: str, 
        output_filename: str, 
        toc_page_numbers: List[int], 
        offset: int,
        nest_using_fontsize: bool = False) -> None:
    output_file_writer = PdfFileWriter()
    input_file = PdfFileReader(input_filename)
    for page in input_file.pages:
        output_file_writer.addPage(page)

    content_pages = extract_pages(
        pdf_file=input_filename,
        page_numbers=toc_page_numbers,
        laparams=TOC_LA_PARAMS
    )
    content_text = [text_box for page in content_pages for text_box in page]
    content_text = filter(LTTextBox.__instancecheck__, content_text)
    content_lines = [line for content in content_text for line in content]

    content_lines = list(filter(lambda x: re.search(PAGE_NUMBER_REGEX, x.get_text().strip()), content_lines))

    if nest_using_fontsize:
        bookmarks = construct_bookmark_tree_using_fontsize(content_lines, 0)[0]
    else:
        bookmarks = construct_top_level_bookmarks(content_lines)
    
    output_file_writer = add_bookmarks(bookmarks, output_file_writer, offset, None)

    with open(output_filename, 'wb') as output_file:
        output_file_writer.write(output_file)
