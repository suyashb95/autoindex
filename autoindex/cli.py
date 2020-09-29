import click, constants
from . import bookmarks

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
	'--diagnose', '-d',
	default=False,
	is_flag=True,
	help='print the most common font sizes and line starting points to help choose values for fontsize/indent thresholds')
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
@click.pass_context
def cli(
	ctx,
	input,
	output,
	toc_page_numbers,
	offset,
	diagnose,
	nest_using_fontsize,
	nest_using_indents,
	char_margin,
	line_margin,
	header_fontsize_threshold,
	topic_fontsize_threshold,
	header_indent_threshold,
	topic_indent_threshold,
):
	bookmarks.add_bookmarks(
		input,
		output,
		toc_page_numbers,
		offset,
		diagnose,
		nest_using_fontsize,
		nest_using_indents,
		char_margin,
		line_margin,
		header_fontsize_threshold,
		topic_fontsize_threshold,
		header_indent_threshold,
		topic_indent_threshold,
	)
