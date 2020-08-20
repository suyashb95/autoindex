import re
import constants

from pdfminer.layout import LTTextBox
from typing import List, Dict, Callable


Bookmark = Dict[LTTextBox, 'Bookmark']

def get_fontsize(node: LTTextBox) -> float:
	return list(node)[0].height

def get_indent(node: LTTextBox) -> float:
	return node.x0

def construct_bookmark_tree(
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
			children, running_index = construct_bookmark_tree(
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

def add_bookmarks(bookmarks: List, pdf, offset=0, parent=None):
	for bookmark in bookmarks:
		content = re.search(constants.PAGE_NUMBER_REGEX, bookmark.get_text())
		name = content.string[:content.start()].strip()
		name = re.sub(constants.DETECT_SPECIAL_CHARS, '', name)
		location = int(content[0].strip()) + offset
		new_parent = pdf.addBookmark(name, location, parent=parent)
		add_bookmarks(bookmarks[bookmark], pdf, offset, new_parent)
	return pdf
