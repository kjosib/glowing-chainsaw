"""
This module focuses on the transformation from AST to static structure.
There's not really too much magic here, but it's good to have the separation.
It's also completely unusable at the moment; just a parking lot for excised code.
But things will get better...
"""

import collections
from typing import List, Dict, Union, Mapping, MutableMapping
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

VOCABULARY = {
	**xl_schema.FORMAT_PROPERTIES,
	**xl_schema.OUTLINE_PROPERTIES,
	**{k:xl_schema.FORMAT_PROPERTIES[v[0]] for k,v in xl_schema.SPECIAL_CASE.items()},
}


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
		"""
		Build up a named-style as a root-level object and store it in the style namespace.
		At least, that's the happy path. Various things can go wrong. What gets reported
		first is sort of a matter of happenstance: what mistake do we stumble over first?
		At any rate, report definitions should not ever get huge, so reporting an error
		and quitting is probably an OK strategy for now.
		"""
		env = {}
		self.build_style(styledef.elts, env)
		try: self.named_styles.let(styledef.name, env)
		except RedefinedNameError as e:
			self.source.complain(*e.args[0].span, message="Redefined style name")
			self.source.complain(*e.args[1].span, message="First defined here")
			raise
	
	def build_style(self, elts:List, env:MutableMapping):
		"""
		elts are -- style names, activations, deactivations, or attribute assignments.
		This works by mutating an environment you pass in, so the same code therefore works
		regardless of use in creating named-styles or actually-used styles.
		"""
		for item in elts:
			if isinstance(item, AST.Name): env.update(self.named_styles.get(item))
			elif isinstance(item, AST.Assign):
				# We get a word and a constant. The word may refer to one of two special cases,
				# or it must be a properly recognized style property.
				key, value = item.word.text, item.const.value
				if key not in VOCABULARY:
					self.source.complain(*item.word.span, message="There's no such attribute as '%s'."%key)
					raise NoSuchAttrbute(key)
				kind = VOCABULARY[key]
				if not kind.test(value):
					self.source.complain(*item.const.span, message="Value for %s must be %s"%(key, kind.description))
					raise BadAttributeValue(item.const.value)
				if key in xl_schema.SPECIAL_CASE:
					for k in xl_schema.SPECIAL_CASE[key]: env[k] = value
				else: env[key] = value
				pass
			else: assert False, type(item)
	
	def make_numbered_style(self, env:Mapping) -> int:
		digest = sorted((k, v) for k, v in env.items() if k in xl_schema.FORMAT_PROPERTIES)
		return self.numbered_styles.classify(tuple(digest))
	
	def make_numbered_outline(self, env:Mapping) -> int:
		digest = (env['level'], env['hidden'], env['collapse'])
		return self.numbered_outlines.classify(digest)

class FieldBuilder(utility.Visitor):
	"""
	I have this idea that the answer to translating fields is properly recursive only on
	a slightly reduced form of the original problem.
	"""
	def __init__(self, module_builder:Transducer, style_context:collections.ChainMap):
		self.mb = module_builder
		self.sc = style_context.new_child()
	def interpret_margin_notes(self, notes:AST.Marginalia) -> static.Marginalia:
		"""
		Two phases: Update the fields of the style context (self.sc) according to the notes,
		and then capture the result in the appointed structure.
		"""
		if notes.texts is not None: self.sc['_texts'] = notes.texts
		if notes.hint is not None: self.sc['_hint'] = notes.hint
		self.mb.build_style(notes.appearance, self.sc)
		return static.Marginalia(
			style_index=self.mb.make_numbered_style(self.sc),
			outline_index=self.mb.make_numbered_outline(self.sc),
			texts=self.sc['_texts'],
			formula=self.sc['_hint'],
			height=self.sc['height'],
			width=self.sc['width'],
		)
	
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
	
	def make_toplevel(self) -> static.CubModule:
		return static.CubModule(self.canvas_definitions, [dict(x) for x in self.styles.exemplars], self.outlines.exemplars)
		
	def parse_leaf(self, margin):
		return static.LeafDefinition(margin)
	
	def parse_normal_reader(self, word):
		assert isinstance(word, AST.Name)
		return static.SimpleReader(word.text)
	
	def parse_simple_string_template(self, the_string):
		return static.TextTemplateFormula([static.LiteralTextComponent(the_string)])
	
