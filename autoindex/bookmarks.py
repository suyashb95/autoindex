import re


from pdfminer.layout import LTTextBox, LAParams
from pdfminer.high_level import extract_pages
from typing import List, Dict, Callable
from PyPDF2 import PdfFileWriter, PdfFileReader
from collections import Counter
from . import constants

Bookmark = Dict[LTTextBox, 'Bookmark']

def get_fontsize(node: LTTextBox) -> float:
    return list(node)[0].height

def get_indent(node: LTTextBox) -> float:
    return node.x0

def get_contents_from_toc_pages(content_pages):
    content_text = []
    for page in content_pages:
        for text_box in page:
            if isinstance(text_box, LTTextBox):
                text_box.pageid = page.pageid
                content_text.append(text_box)

    content_lines = []
    for content in content_text:
        for line in content:
            if re.search(constants.PAGE_NUMBER_REGEX, line.get_text().strip()):
                line.pageid = content.pageid
                content_lines.append(line)

    return sorted(content_lines, key=lambda line: (line.pageid, -line.y0))	

def create_bookmark_tree(
        bookmarks: List[LTTextBox],
        indent_threshold: float = 1.0,
        indent_tolerance: float = 1.0,
        indent_attribute: Callable = lambda x: 0,
        running_index: int = 0,
        ) -> (Bookmark, int):
    current_level_nodes = {}
    while running_index < len(bookmarks) - 1:
        current_node = bookmarks[running_index]
        children = {}
        if indent_attribute(current_node) - indent_attribute(bookmarks[running_index + 1]) >= indent_threshold:
            children, running_index = create_bookmark_tree(
                bookmarks, 
                indent_threshold, 
                indent_tolerance,
                indent_attribute,
                running_index + 1,
            )
        elif indent_attribute(bookmarks[running_index + 1]) - indent_attribute(current_node) >= indent_tolerance:
            current_level_nodes[current_node] = {}
            return current_level_nodes, running_index + 1
        else:
            running_index += 1
        current_level_nodes[current_node] = children
    return current_level_nodes, running_index

def insert_bookmarks(bookmarks: List, pdf, offset=0, parent=None):
    for bookmark in bookmarks:
        content = re.search(constants.PAGE_NUMBER_REGEX, bookmark.get_text())
        name = content.string[:content.start()].strip()
        name = re.sub(constants.DETECT_SPECIAL_CHARS, '', name)
        location = int(content[0].strip()) + offset
        new_parent = pdf.addBookmark(name, location, parent=parent)
        insert_bookmarks(bookmarks[bookmark], pdf, offset, new_parent)
    return pdf

def add_bookmarks(
        input: str,
        output: str,
        toc_page_numbers: List[int],
        offset: int = 0,
        diagnose: bool = False,
        nest_using_fontsize: bool = False,
        nest_using_indents: bool = False,
        char_margin: float = constants.DEFAULT_CHAR_MARGIN,
        line_margin: float = constants.DEFAULT_LINE_MARGIN,
        header_fontsize_threshold: float = constants.DEFAULT_HEADER_FONTSIZE_THRESHOLD,
        topic_fontsize_threshold: float = constants.DEFAULT_TOPIC_FONTSIZE_THRESHOLD,
        header_indent_threshold: float = constants.DEFAULT_HEADER_INDENT_THRESHOLD,
        topic_indent_threshold: float = constants.DEFAULT_TOPIC_INDENT_THRESHOLD
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

    content_lines = get_contents_from_toc_pages(content_pages)

    if diagnose:
        print('Common font sizes')
        print(Counter([round(list(line)[0].height, 3) for line in content_lines]).most_common(3))
        print('Common line starting points')
        print(Counter([round(line.x0, 3) for line in content_lines]).most_common(3))
        return

    if nest_using_fontsize:
        bookmarks, _ = create_bookmark_tree(
            content_lines,
            header_fontsize_threshold,
            topic_fontsize_threshold,
            get_fontsize
        )
    elif nest_using_indents:
        bookmarks, _ = create_bookmark_tree(
            content_lines,
            header_indent_threshold,
            topic_indent_threshold,
            get_indent
        )
    else:
        bookmarks, _ = create_bookmark_tree(content_lines)

    output_file_writer = insert_bookmarks(bookmarks, output_file_writer, offset, None)

    with open(output, 'wb') as output_file:
        output_file_writer.write(output_file)
