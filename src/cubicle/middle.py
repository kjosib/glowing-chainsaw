"""
This module focuses on the transformation from AST to static structure.
There's not really too much magic here, but it's good to have the separation.
It's also completely unusable at the moment; just a parking lot for excised code.
But things will get better...
"""

import collections
from typing import List, Dict, Union
from boozetools.support import foundation
from canon import xl_schema, utility
from . import AST, static


class RedefinedNameError(ValueError): pass
class BadAttributeValue(ValueError): pass

class Transducer(utility.Visitor):
	"""
	A form of interpreter: not from source lines of code, but from a list of
	AST nodes for top-level declarations. It can also be considered a kind of
	tree-transducer, if you squint.
	
	Someone will object that this should not be written as an object (I pun)
	but the alternative (a nest of procedures) gets ugly fast.
	"""
	def __init__(self):
		self.named_styles = {}
		self.named_shapes = {}
		self.named_canvases = {}
		
		self.numbered_styles = foundation.EquivalenceClassifier()
		self.numbered_outlines = foundation.EquivalenceClassifier()
	
	def interpret(self, declarations:List[Union[AST.StyleDef, AST.Field, AST.Canvas]]) -> static.CubModule:
		for d in declarations: self.visit(d)
		return static.CubModule(
			self.named_canvases,
			self.numbered_styles.exemplars,
			self.numbered_outlines.exemplars,
		)
	
	def visit_Field(self, field:AST.Field):
		pass

	def visit_Canvas(self, canvas:AST.Canvas):
		pass

	def visit_StyleDef(self, field:AST.StyleDef):
		pass


class x_Transducer(utility.Visitor):
	"""
	Idea: Let the parse-driver focus on producing a simple AST.
	Structure here is surely wrong: It should be a nest of procedures or collection of several visitors.
	Let this object transform that simple AST into the form needed
	for the backend -- which by-the-way is presumably optimal for pickling.
	"""
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
	
	def push_context(self): self.context.maps.insert(0, {})
	def pop_context(self): self.context.maps.pop(0)
	
	def visit_Marginalia(self, m:AST.Marginalia):
		""" Convert AST.Marginalia to static.Marginalia by interpretation and equivalence. """
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

	# def parse_begin_margin_style(self): self.context.maps.insert(0, {})
	
	def make_toplevel(self) -> static.CubModule:
		return static.CubModule(self.canvas_definitions, [dict(x) for x in self.styles.exemplars], self.outlines.exemplars)
		
	def parse_leaf(self, margin):
		return static.LeafDefinition(margin)
	
	def parse_normal_reader(self, word):
		assert isinstance(word, AST.Name)
		return static.SimpleReader(word.text)
	
	def parse_simple_string_template(self, the_string):
		return static.TextTemplateFormula([static.LiteralTextComponent(the_string)])
	
	@staticmethod
	def test_value(kind_space: Dict[str, xl_schema.Kind], name, value):
		kind = kind_space[name]
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


