"""

"""
import collections
from typing import Dict
from boozetools.support import runtime as brt, interfaces, foundation
from . import static
from canon import utility, xl_schema, lexical

class RedefinedNameError(ValueError): pass
class BadAttributeValue(ValueError): pass

TABLES = utility.tables(__file__, 'core_grammar.md')

def compile_string(string, *, filename=None):
	parser = CoreDriver()
	result = parser.parse(string, filename=filename)
	if not parser.errors: return parser.make_toplevel()

def compile_path(path):
	with open(path) as fh: string = fh.read()
	return compile_string(string, filename=path)

class CoreDriver(brt.TypicalApplication, lexical.LexicalAnalyzer):
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
		return static.Marginalia(
			style_index=self.styles.classify(tuple(sorted((k, v) for k, v in self.context.items() if k in xl_schema.FORMAT_PROPERTIES))),
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
	def parse_frame(self, margin, gensym, fields):
		reader = static.SimpleReader(gensym)
		return static.FrameDefinition(reader, dict(fields), margin)
	def parse_leaf(self, margin):
		self.pop_context()
		return static.LeafDefinition(margin)
	def parse_define_shape(self, name, shape):
		if name in self.shape_definitions: raise RedefinedNameError(name)
		else: self.shape_definitions[name] = shape
	def parse_named_shape(self, name):
		return self.shape_definitions[name]
	
	@staticmethod
	def test_value(kind_space:Dict[str, xl_schema.Kind], name, value):
		kind=kind_space[name]
		if not kind.test(value):
			raise BadAttributeValue(name + ' must be ' + kind.description)
	
	def parse_assign_attribute(self, name, value):
		self.test_value(xl_schema.FORMAT_PROPERTIES, name, value)
		if name in xl_schema.SPECIAL_CASE:
			for key in xl_schema.SPECIAL_CASE[name]:
				self.context[key] = value
		else: self.context[name] = value
		
	def parse_assign_outline(self, name, value):
		self.test_value(xl_schema.OUTLINE_PROPERTIES, name, value)
		self.context[name] = value
	
	def parse_true(self, x): return True
	def parse_false(self, x): return False
