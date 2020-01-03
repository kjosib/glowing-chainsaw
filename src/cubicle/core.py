"""

"""
import os, tempfile, pickle, typing, collections
from boozetools.support import failureprone, runtime as brt, interfaces, foundation
from . import static, dynamic, runtime, veneer, org

class RedefinedNameError(ValueError): pass

FORMAT_PROPERTIES = {
	'font_name': str,
	'font_size': int,
	'font_color': str,
	'bold': bool,
	'italic': bool,
	'underline': int, # 1=single, 2=double, 33=single-accounting, 34=double-accounting
	'font_strikeout': bool,
	'font_script': int, # 1=Superscript, 2=Subscript -- but these are unlikely.
	'num_format': (int, str),
	'locked': bool,
	'hidden': bool,
	'align': str,
	'valign': str,
	'rotation': int,
	'text_wrap': bool,
	'reading_order': int, # 1=left-to-right, like English. 2=right-to-left, like Arabic.
	'text_justlast': bool,
	# 'center_across': # use .align=center_across instead.
	'indent': int,
	'shrink': bool,
	'pattern': int, # 0-18, with 1 being a solid fill of the background color.
	'bg_color': str,
	'fg_color': str,
	'border': int,
	'bottom': int,
	'top': int,
	'left': int,
	'right': int,
	'border_color': str,
	'bottom_color': str,
	'top_color': str,
	'left_color': str,
	'right_color': str,
}

OUTLINE_PROPERTIES = {
	'height': (int, float),
	'width': (int, float),
	'level': int,
	'hidden': bool,
	'collapsed': bool,
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

def compile_string(string): return _compile(failureprone.SourceText(string))
def compile_path(path): _compile(failureprone.SourceText(open(path).read(), filename=path))

def _compile(text:failureprone.SourceText):
	driver = CoreDriver()
	scan = brt.simple_scanner(TABLES, driver)(text.content)
	parse = brt.simple_parser(TABLES, driver)
	try: parse(scan)
	except brt.DriverError as e:
		text.complain(*scan.current_span(), message=str(e.args))
		raise e.__cause__ from None
	except interfaces.ParseError as e:
		text.complain(*scan.current_span(), message="Cubicle parser got confused with "+e.lookahead+".")
	except interfaces.ScanError as e:
		text.complain(scan.current_position(), message="Cubicle scanner doesn't know this mark.")
	else: return driver.make_toplevel()

class CoreDriver:
	VALID_KEYWORDS = {'LEAF', 'FRAME', 'MENU', 'TREE', 'OF', 'STYLE', 'CANVAS', 'GAP'}
	def scan_ignore(self, yy): assert '\n' not in yy.matched_text()
	def scan_token(self, yy, kind): return kind, yy.matched_text()
	def scan_sigil(self, yy, kind): return kind, yy.matched_text()[1:]
	def scan_keyword(self, yy):
		word = yy.matched_text()[1:].upper()
		if word not in CoreDriver.VALID_KEYWORDS: raise interfaces.ScanError(yy.current_span(), "Bad keyword", word)
		return word, None
	def scan_enter(self, yy, dst):
		yy.push(dst)
		return 'BEGIN_'+dst, None
	def scan_leave(self, yy, src):
		yy.pop()
		return 'END_'+src, None
	def scan_delimited(self, yy, what): return what, yy.matched_text()[1:-1]
	def scan_integer(self, yy): return 'INTEGER', int(yy.matched_text())
	def scan_decimal(self, yy): return 'DECIMAL', float(yy.matched_text())
	def scan_punctuation(self, yy):
		it = yy.matched_text()
		return it, it
	def scan_embedded_newline(self, yy): return 'TEXT', '\n'
	def scan_letter_escape(self, yy): return 'TEXT', chr(7+'abtnvfr'.index(yy.matched_text()))
	
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
