"""
This module focuses on the transformation from AST to static structure.
There's not really too much magic here, but it's good to have the separation.
It's also completely unusable at the moment; just a parking lot for excised code.
But things will get better...
"""

import collections
from typing import List, Dict, Union, NamedTuple
from boozetools.support import foundation, failureprone
from canon import xl_schema, utility
from . import AST, static


class UndefinedNameError(KeyError): pass
class RedefinedNameError(KeyError): pass
class BadAttributeValue(ValueError): pass
class NoSuchAttrbute(KeyError): pass

BLANK_STYLE = collections.ChainMap({
	'_texts':(), '_formula':None,
	'level':0, 'hidden':False, 'collapse':False,
	'height':None, 'width':None,
})

class SymbolTable:
	""" I've a sense I'll want a "smart" symbol table object: a bit more than a dictionary. """
	def __init__(self):
		self.__entries = {} # For now entries are just a <Name, object> pair. Keys are strings.
	
	def let(self, name:AST.Name, item):
		""" Enforce single-assignment... """
		key = name.text
		if key in self.__entries: raise RedefinedNameError(name, self.__entries[key][0])
		else: self.__entries[key] = (name, item)
	
	def get(self, name:AST.Name):
		try: return self.__entries[name.text][1]
		except KeyError: raise UndefinedNameError(name) from None
	
	def as_dict(self) -> dict:
		""" Just string keys and semantic items; no location-tracking fluff. """
		return {key: entry[1] for key, entry in self.__entries.items()}
	

class Transducer(utility.Visitor):
	"""
	A form of interpreter: not from source lines of code, but from a list of
	AST nodes for top-level declarations. It can also be considered a kind of
	tree-transducer, if you squint.
	
	Someone will object that this should not be written as an object (I pun)
	but the alternative (a nest of procedures) gets ugly fast.
	"""
	def __init__(self, source:failureprone.SourceText):
		self.source = source
		
		self.named_styles = SymbolTable()
		self.named_shapes = SymbolTable()
		self.named_canvases = SymbolTable()
		
		self.numbered_styles = foundation.EquivalenceClassifier()
		self.numbered_outlines = foundation.EquivalenceClassifier()
	
	def interpret(self, declarations:List[Union[AST.StyleDef, AST.Field, AST.Canvas]]) -> static.CubModule:
		for d in declarations: self.visit(d)
		return static.CubModule(
			self.named_canvases.as_dict(),
			self.numbered_styles.exemplars,
			self.numbered_outlines.exemplars,
		)
	
	def visit_Field(self, field:AST.Field):
		""" Needs to add the (transformed) field to self.named_shapes """
		self.named_shapes.let(field.name, FieldBuilder(self, BLANK_STYLE).visit(field.shape))

	def visit_Canvas(self, canvas:AST.Canvas):
		""" Build a static.CanvasDefinition and add it to self.named_canvases """
		pass

	def visit_StyleDef(self, styledef:AST.StyleDef):
		# This one SHOULD be easy:
		try: self.named_styles.let(styledef.name, self.build_style(styledef.elts))
		except RedefinedNameError as e:
			self.source.complain(*e.args[0].span, message="Redefined style name")
			self.source.complain(*e.args[1].span, message="First defined here")
			raise
	
	def build_style(self, elts:List):
		""" elts are -- style names, activations, deactivations, or attribute assignments. """
		pass

class FieldBuilder(utility.Visitor):
	"""
	I have this idea that the answer to translating fields is properly recursive only on
	a slightly reduced form of the original problem.
	"""
	def __init__(self, module_builder:Transducer, style_context:collections.ChainMap):
		self.mb = module_builder
		self.sc = style_context
	def interpret_margin_notes(self, notes:AST.Marginalia) -> static.Marginalia:
		print("FIXME: interpret_margin_notes")
		pass
	
	def visit_Marginalia(self, notes:AST.Marginalia) -> static.LeafDefinition:
		return static.LeafDefinition(self.interpret_margin_notes(notes))
	
	def visit_Name(self, name:AST.Name) -> static.ShapeDefinition:
		return self.mb.named_shapes.get(name)
	
	def visit_Tree(self, tree:AST.Tree) -> static.TreeDefinition:
		print("FIXME: Tree")
		pass
	
	def visit_Frame(self, tree:AST.Frame) -> static.FrameDefinition:
		print("FIXME: Frame")
		pass
	
	def visit_Menu(self, menu:AST.Menu) -> static.MenuDefinition:
		print("FIXME: Menu")
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


