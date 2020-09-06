from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.high_level import extract_pages
from PyPDF2 import PdfFileWriter, PdfFileReader
from typing import List, Dict
from pdfminer.layout import LTChar, LTTextBox
from collections import Counter
from modules.bookmarks import construct_bookmark_tree
from modules.bookmarks import add_bookmarks, get_fontsize, get_indent

import re
import constants
import click


def output_filename_callback(ctx, param, value):
	if not value:
		return ctx.params['input'].split('.pdf')[0] + '-bookmarked.pdf'
	return value

def toc_page_numbers_callback(ctx, param, value):
	if len(value) is not 2:
		ctx.fail('A range of ToC pages should be specified using --toc or --toc-page-numbers')
	return list(range(value[0], value[1] + 1))



@click.command()
@click.option('--input', '-i', help='input file name', required=True)
@click.option('--output', '-o', 
	help='output file name. If not provided, defaults to the input file name suffixed with "-bookmarked"', 
	required=False, callback=output_filename_callback)
@click.option(
	'--toc-page-numbers', '--toc',
	nargs=2, type=int, callback=toc_page_numbers_callback, required=True,
	help='range of pages from, to having the table of contents')
@click.option(
	'--diagnose', '-d',
	default=False,
	is_flag=True,
	help='print the most common font sizes and line starting points to help choose values for fontsize/indent thresholds')
@click.option(
	'--nest-using-fontsize',
	is_flag=True,
	default=False,
	help='flag to try and figure out nested bookmarks using font sizes')
@click.option(
	'--nest-using-indents', 
	default=False,
	is_flag=True,
	help='flag to try and figure out nested bookmarks using indents')
@click.option('--offset', type=int, default=0, help='offset to add to the page numbers from the table of contents')
@click.option(
	'--char-margin',
	type=float, default=constants.DEFAULT_CHAR_MARGIN,
	help='spacing between characters to be considered as a part of the same line')
@click.option(
	'--line-margin', 
	type=float, default=constants.DEFAULT_LINE_MARGIN,
	help='spacing between lines to be considered as a part of the same text box')
@click.option(
	'--header-fontsize-threshold', 
	type=float, default=constants.DEFAULT_HEADER_FONTSIZE_THRESHOLD,
	help='font size difference for a line to be considered as header')
@click.option(
	'--topic-fontsize-threshold', 
	type=float, default=constants.DEFAULT_TOPIC_FONTSIZE_THRESHOLD,
	help='font size difference for lines to be considered as a part of the same parent header')
@click.option(
	'--header-indent-threshold', 
	type=float, default=constants.DEFAULT_HEADER_INDENT_THRESHOLD,
	help='indent difference for a line to be considered as header')
@click.option(
	'--topic-indent-threshold', 
	type=float, default=constants.DEFAULT_TOPIC_INDENT_THRESHOLD,
	help='indent difference for lines to be considered as a part of the same parent header')
def cli(
		input: str, 
		output: str,  
		toc_page_numbers: List[int],
		offset: int = 0,
		nest_using_fontsize: bool = False,
		nest_using_indents: bool = False,
		char_margin: float = constants.DEFAULT_CHAR_MARGIN,
		line_margin: float = constants.DEFAULT_LINE_MARGIN,
		header_fontsize_threshold: float = constants.DEFAULT_HEADER_FONTSIZE_THRESHOLD,
		topic_fontsize_threshold: float = constants.DEFAULT_TOPIC_FONTSIZE_THRESHOLD,
		header_indent_threshold: float = constants.DEFAULT_HEADER_INDENT_THRESHOLD,
		topic_indent_threshold: float = constants.DEFAULT_TOPIC_INDENT_THRESHOLD,
		diagnose: bool = False
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

	'''
	filter by text boxes only and filter again 
	for lines containing a page number at the end
	'''
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
	
	'''
	Sort by page number, Y co-ordinate because the order 
	of parsing is not reliable 
	'''
	content_lines = sorted(content_lines, key=lambda line: (line.pageid, -line.y0))

	if diagnose:
		print('Common font sizes')
		print(Counter([round(list(line)[0].height, 3) for line in content_lines]).most_common(3))
		print('Common line starting points')
		print(Counter([round(line.x0, 3) for line in content_lines]).most_common(3))
		return

	if nest_using_fontsize:
		bookmarks, bookmarks_processed = construct_bookmark_tree(
			content_lines, 
			header_fontsize_threshold, 
			topic_fontsize_threshold,
			get_fontsize
		)
	elif nest_using_indents:
		bookmarks, bookmarks_processed = construct_bookmark_tree(
			content_lines, 
			header_indent_threshold, 
			topic_indent_threshold,
			get_indent
		)
	else:
		bookmarks, bookmarks_processed = construct_bookmark_tree(content_lines)
	
	output_file_writer = add_bookmarks(bookmarks, output_file_writer, offset, None)

	with open(output, 'wb') as output_file:
		output_file_writer.write(output_file)

if __name__ == '__main__':
	cli()