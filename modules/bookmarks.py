import re
import constants

from pdfminer.layout import LTTextBox
from typing import List, Dict


Bookmark = Dict[LTTextBox, 'Bookmark']

def construct_top_level_bookmarks(bookmarks: List[LTTextBox]) -> Bookmark:
	return {
		bookmark: {} for bookmark in bookmarks
	}

def construct_bookmark_tree_using_indents(
		bookmarks: List[LTTextBox], 
		header_indent_threshold: float,
		topic_indent_threshold: float,
		running_index: int = 0,
		) -> (Bookmark, int):
	current_level_nodes = {}
	while running_index < len(bookmarks) - 1:
		current_node = bookmarks[running_index]
		children = {}
		if current_node.x0 - bookmarks[running_index + 1].x0 >= header_indent_threshold:
			children, running_index = construct_bookmark_tree_using_indents(
				bookmarks, 
				header_fontsize_threshold, 
				topic_fontsize_threshold,
				running_index + 1,
			)
		elif bookmarks[running_index + 1].x0 - current_node.x0 >= topic_indent_threshold:
			current_level_nodes[current_node] = {}
			return current_level_nodes, running_index + 1
		else:
			running_index += 1
		current_level_nodes[current_node] = children
	return current_level_nodes, running_index

def construct_bookmark_tree_using_fontsize(
		bookmarks: List[LTTextBox], 
		header_fontsize_threshold: float,
		topic_fontsize_threshold: float,
		running_index: int = 0,
		) -> (Bookmark, int):
	current_level_nodes = {}
	while running_index < len(bookmarks) - 1:
		current_node = bookmarks[running_index]
		children = {}
		if list(current_node)[0].height - list(bookmarks[running_index + 1])[0].height >= header_fontsize_threshold:
			children, running_index = construct_bookmark_tree_using_fontsize(
				bookmarks, 
				header_fontsize_threshold,
				topic_fontsize_threshold,
				running_index + 1				
			)
		elif abs(list(bookmarks[running_index + 1])[0].height - list(current_node)[0].height) >= topic_fontsize_threshold:
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
		name = re.sub(constants.DETECT_SPECIAL_CHARS, '', name)
		location = int(content[0].strip()) + offset
		new_parent = pdf.addBookmark(name, location, parent=parent)
		add_bookmarks(bookmarks[bookmark], pdf, offset, new_parent)
	return pdf
