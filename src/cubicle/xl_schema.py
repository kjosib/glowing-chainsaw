"""
This file tells you what your options and flexibilities are in formatting an XLSX spreadsheet.
It has sections on cell formatting and outline formatting.
"""

import re

class Kind:
	""" This is sort of like a type. But it's allowed to be more specific. """
	def __init__(self, description:str, test):
		self.description = description
		self.test = test

class RangeKind(Kind):
	def __init__(self, lower, upper):
		super().__init__('an integer from %d to %d, inclusive', lambda x:isinstance(x,int) and lower <= x <= upper)

kind_string = Kind('a string', lambda x:isinstance(x,str))
kind_number = Kind('a number', lambda x:isinstance(x,(int, float)))
kind_integer = Kind('a number', lambda x:isinstance(x,int))
kind_boolean = Kind('a true/false flag', lambda x:isinstance(x,bool))
kind_border = RangeKind(0, 13)

COLOR_NAMES = frozenset('black blue brown cyan gray green lime magenta navy orange pink purple red silver white yellow'.split())
kind_color = Kind('a valid color name or #hex code', lambda x:isinstance(x, str) and (x in COLOR_NAMES or re.fullmatch(r'#[0-9A-Fa-f]{6}', x)))

FORMAT_PROPERTIES = {
	'font_name': kind_string,
	'font_size': kind_integer,
	'font_color': kind_string,
	'bold': kind_boolean,
	'italic': kind_boolean,
	'underline': Kind('one of 1=single, 2=double, 33=single-accounting, 34=double-accounting', {None,1,2,33,34}.__contains__),
	'font_strikeout': kind_boolean,
	'font_script': Kind('one of 1=Superscript, 2=Subscript', {1,2}.__contains__), #  -- but these are unlikely.
	'num_format': Kind("a valid format string or numeric code", lambda x:(isinstance(x,int) and 0<=x<=49) or (isinstance(x,str))),
	'locked': kind_boolean,
	'hidden': kind_boolean,
	'align': kind_string,
	'valign': kind_string,
	'rotation': Kind('from -90 to +90 or exactly 270', lambda x: isinstance(x, (int, float)) and ((-90 <= x <= 90) or (x == 270))),
	'text_wrap': kind_boolean,
	'reading_order': Kind('one of 1=left-to-right, like English. 2=right-to-left, like Arabic', {1,2}.__contains__), # .
	'text_justlast': kind_boolean,
	# 'center_across': # use align=center_across instead.
	'indent': kind_integer,
	'shrink': kind_boolean,
	'pattern': RangeKind(0,18), # 0-18, with 1 being a solid fill of the background color.
	'bg_color': kind_color,
	'fg_color': kind_color,
	'border': kind_border,
	'bottom': kind_border,
	'top': kind_border,
	'left': kind_border,
	'right': kind_border,
	'diag_border': kind_border,
	'diag_type': RangeKind(0,3),
	'diag_color': kind_color,
	'border_color': kind_color,
	'bottom_color': kind_color,
	'top_color': kind_color,
	'left_color': kind_color,
	'right_color': kind_color,
}

OUTLINE_PROPERTIES = {
	'height': kind_number,
	'width': kind_number,
	'level': RangeKind(0,7),
	'hidden': kind_boolean,
	'collapsed': kind_boolean,
}

SPECIAL_CASE = {
	'border': ['top', 'left', 'bottom', 'right'],
	'border_color': ['top_color', 'left_color', 'bottom_color', 'right_color'],
}

