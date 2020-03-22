"""

"""
import os, tempfile, pickle, collections, re
from typing import Dict
from boozetools.support import runtime as brt, interfaces, foundation
from . import static, dynamic, runtime, veneer, org

class RedefinedNameError(ValueError): pass
class BadAttributeValue(ValueError): pass

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
	# 'center_across': # use .align=center_across instead.
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


def tables() -> dict:
	"""
	Perhaps this routine belies a deficiency in the stack, but the object is to be able to
	compile the grammar only once (or whenever it changes) and use it over and over.
	In a fully-packaged solution a pre-pickled table may seem desirable, but for now
	this adaptive approach is better for hacking on.
	"""
	grammar_path = os.path.join(os.path.split(__file__)[0], 'core_grammar.md')
	cache_path = os.path.join(tempfile.gettempdir(), 'cubicle.pickle')
	if os.path.exists(cache_path) and os.path.getmtime(cache_path) > os.path.getmtime(grammar_path):
		return pickle.load(open(cache_path, 'rb'))
	else:
		from boozetools.macroparse import compiler
		result = compiler.compile_file(grammar_path, method='LR1')
		pickle.dump(result, open(cache_path, 'wb'))
		return result
TABLES = tables()

def compile_string(string, *, filename=None):
	parser = CoreDriver()
	result = parser.parse(string, filename=filename)
	if not parser.errors: return parser.make_toplevel()

def compile_path(path):
	with open(path) as fh: string = fh.read()
	return compile_string(string, filename=path)

class CoreDriver(brt.TypicalApplication):
	
	VALID_KEYWORDS = {'LEAF', 'FRAME', 'MENU', 'TREE', 'OF', 'STYLE', 'CANVAS', 'GAP', 'USE', 'HEAD'}
	def scan_ignore(self, yy): assert '\n' not in yy.matched_text()
	def scan_token(self, yy, kind): yy.token(kind, yy.matched_text())
	def scan_sigil(self, yy, kind): yy.token(kind, yy.matched_text()[1:])
	def scan_keyword(self, yy):
		word = yy.matched_text()[1:].upper()
		if word not in CoreDriver.VALID_KEYWORDS: word='$bogus$'
		yy.token(word, None)
	def scan_enter(self, yy, dst):
		yy.push(dst)
		yy.token('BEGIN_'+dst, None)
	def scan_leave(self, yy, src):
		yy.pop()
		yy.token('END_'+src, None)
	def scan_delimited(self, yy, what): yy.token(what, yy.matched_text()[1:-1])
	def scan_integer(self, yy): yy.token('INTEGER', int(yy.matched_text()))
	def scan_hex_integer(self, yy): yy.token('INTEGER', int(yy.matched_text()[1:], 16))
	def scan_decimal(self, yy): yy.token('DECIMAL', float(yy.matched_text()))
	def scan_punctuation(self, yy):
		it = yy.matched_text()
		yy.token(it, it)
	def scan_embedded_newline(self, yy): yy.token('TEXT', '\n')
	def scan_letter_escape(self, yy): yy.token('TEXT', chr(7+'abtnvfr'.index(yy.matched_text())))
	
	def __init__(self):
		self.context = collections.ChainMap({
			'_texts':(), '_formula':None,
			'level':0, 'hidden':False, 'collapse':False,
			'height':None, 'width':None,
		})
		self.styles = foundation.EquivalenceClassifier()
		self.outlines = foundation.EquivalenceClassifier()
		self.shape_definitions = {}
		self.canvas_definitions = {}
		self.errors=0
		super().__init__(TABLES)
	
	def unexpected_token(self, kind, semantic, pds):
		self.errors += 1
		super().unexpected_token(kind, semantic, pds)
	
	def make_toplevel(self) -> static.TopLevel:
		return static.TopLevel(self.canvas_definitions, [dict(x) for x in self.styles.exemplars], self.outlines.exemplars)
		
	def parse_none(self): return None
	def parse_empty(self): return []
	def parse_normal_reader(self, name): return static.SimpleReader(name)
	def parse_begin_margin_style(self): self.context.maps.insert(0, {})
	def pop_context(self): self.context.maps.pop(0)
	def parse_marginalia(self, texts, formula):
		if texts is not None: self.context['_texts'] = texts
		if formula is not None: self.context['_formula'] = formula
		return org.Marginalia(
			style_index=self.styles.classify(tuple(sorted((k, v) for k, v in self.context.items() if k in FORMAT_PROPERTIES))),
			outline_index=self.outlines.classify(tuple(self.context[k] for k in ('level', 'hidden', 'collapse'))),
			texts=self.context['_texts'],
			formula=self.context['_formula'],
			height=self.context['height'],
			width=self.context['width'],
		)
	def parse_simple_string_template(self, the_string):
		return static.TextTemplateFormula([static.LiteralTextComponent(the_string)])
	def parse_singleton(self, item): return [item]
	def parse_append(self, them, item):
		them.append(item)
		return them
	def parse_record(self, margin, reader, fields):
		return static.FrameDefinition(reader, dict(fields), margin)
	def parse_leaf(self, margin):
		self.pop_context()
		return static.LeafDefinition(margin)
	def parse_define_shape(self, name, shape):
		if name in self.shape_definitions: raise RedefinedNameError(name)
		else: self.shape_definitions[name] = shape
	
	@staticmethod
	def test_value(kind_space:Dict[str, Kind], name, value):
		kind=kind_space[name]
		if not kind.test(value):
			raise BadAttributeValue(name + ' must be ' + kind.description)
	
	def parse_assign_attribute(self, name, value):
		self.test_value(FORMAT_PROPERTIES, name, value)
		if name in SPECIAL_CASE:
			for key in SPECIAL_CASE[name]:
				self.context[key] = value
		else: self.context[name] = value
		
	def parse_assign_outline(self, name, value):
		self.test_value(OUTLINE_PROPERTIES, name, value)
		self.context[name] = value
