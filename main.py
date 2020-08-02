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
import constants
import click

Bookmark = Dict[LTTextBox, 'Bookmark']

def toc_page_numbers_callback(ctx, param, value):
    return list(range(value[0], value[1] + 1))

def font_size(line: LTTextBox) -> float:
    chars = list(filter(LTChar.__instancecheck__, line))
    return mean(list(map(lambda x: x.height, chars)))

def construct_top_level_bookmarks(bookmarks: List[LTTextBox]) -> Bookmark:
    return {
        bookmark: {} for bookmark in bookmarks
    }

def construct_bookmark_tree_using_fontsize(
        bookmarks: List[LTTextBox], 
        running_index: int,
        header_fontsize_threshold: float,
        topic_fontsize_threshold: float
        ) -> (Bookmark, int):
    current_level_nodes = {}
    while running_index < len(bookmarks) - 1:
        current_node = bookmarks[running_index]
        children = {}
        if font_size(current_node) - font_size(bookmarks[running_index + 1]) >= header_fontsize_threshold:
            children, running_index = construct_bookmark_tree_using_fontsize(
                bookmarks, 
                running_index + 1,
                header_fontsize_threshold, 
                topic_fontsize_threshold
            )
        elif abs(font_size(bookmarks[running_index + 1]) - font_size(current_node)) >= topic_fontsize_threshold:
            current_level_nodes[current_node] = {}
            return current_level_nodes, running_index + 1
        else:
            running_index += 1
        current_level_nodes[current_node] = children
    return current_level_nodes, running_index

def add_bookmarks(bookmarks: List, pdf, offset=0, parent=None):
    for bookmark in bookmarks:
        content = re.search(constants.PAGE_NUMBER_REGEX, bookmark.get_text())
        name = content.string[:content.start()].strip()
        location = int(content[0].strip()) + offset          
        new_parent = pdf.addBookmark(name, location, parent=parent)
        add_bookmarks(bookmarks[bookmark], pdf, offset, new_parent)
    return pdf


@click.command()
@click.option('--input', '-i', help='input file name')
@click.option('--output', '-o', help='output file name')
@click.option(
    '--toc-page-numbers', '--toc',
    nargs=2, type=int, callback=toc_page_numbers_callback,
    help='range of pages (from, to) having the table of contents'
)
@click.option(
    '--nest-using-fontsize', 
    type=bool, default=False,
    help='flag to try and figure out nested bookmarks using font sizes'
)
@click.option('--offset', type=int, default=0, help='offset to add to the page numbers from the table of contents')
@click.option(
    '--char-margin', 
    type=float, default=constants.DEFAULT_CHAR_MARGIN,
    help='spacing between characters to be considered as a part of the same line'
)
@click.option(
    '--line-margin', 
    type=float, default=constants.DEFAULT_LINE_MARGIN,
    help='spacing between lines to be considered as a part of the same text box'
)
@click.option(
    '--header-fontsize-threshold', 
    type=float, default=constants.DEFAULT_HEADER_FONTSIZE_THREADHOLD,
    help='minimum difference between font sizes for a line to be considered as header'
)
@click.option(
    '--topic-fontsize-delta', 
    type=float, default=constants.DEFAULT_FONTSIZE_THRESHOLD,
    help='font size delta for lines to be considered as a part of the same parent header'
)
def add_index(
        input: str, 
        output: str, 
        toc_page_numbers: List[int], 
        offset: int = 0,
        nest_using_fontsize: bool = False,
        char_margin: float = constants.DEFAULT_CHAR_MARGIN,
        line_margin: float = constants.DEFAULT_LINE_MARGIN,
        header_fontsize_threshold: float = constants.DEFAULT_HEADER_FONTSIZE_THREADHOLD,
        topic_fontsize_delta: float = constants.DEFAULT_FONTSIZE_THRESHOLD
        ) -> None:

    la_params = LAParams(
        char_margin=char_margin,
        line_margin=line_margin
    )

    output_file_writer = PdfFileWriter()
    input_file = PdfFileReader(input)
    for page in input_file.pages:
        output_file_writer.addPage(page)

    content_pages = extract_pages(
        pdf_file=input,
        page_numbers=toc_page_numbers,
        laparams=la_params
    )

    content_text = [text_box for page in content_pages for text_box in page]
    content_text = filter(LTTextBox.__instancecheck__, content_text)
    content_lines = [line for content in content_text for line in content]

    content_lines = list(filter(lambda x: re.search(constants.PAGE_NUMBER_REGEX, x.get_text().strip()), content_lines))

    if nest_using_fontsize:
        bookmarks = construct_bookmark_tree_using_fontsize(content_lines, 0, header_fontsize_threshold, topic_fontsize_delta)[0]
    else:
        bookmarks = construct_top_level_bookmarks(content_lines)
    
    output_file_writer = add_bookmarks(bookmarks, output_file_writer, offset, None)

    with open(output, 'wb') as output_file:
        output_file_writer.write(output_file)

if __name__ == '__main__':
    add_index()
