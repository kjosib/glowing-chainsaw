"""
This module focuses on the transformation from AST to static structure.
There's not really too much magic here, but it's good to have the separation.
It's also completely unusable at the moment; just a parking lot for excised code.
But things will get better...
"""

import collections
from typing import List, Union, Mapping, MutableMapping, NamedTuple, Tuple
from boozetools.support import foundation, failureprone
from . import AST, static, formulae, xl_schema, veneer


class SemanticError(Exception):
	"""Superclass of all semantic errors."""
	def show(self, source:failureprone.SourceText):
		raise NotImplementedError(type(self))


class BogusDefaultError(SemanticError):
	def __init__(self, sigil:AST.Sigil, defsym:AST.Name):
		assert isinstance(sigil, AST.Sigil)
		assert isinstance(defsym, AST.Name)
		self.sigil, self.defsym = sigil, defsym
	
	def show(self, source:failureprone.SourceText):
		source.complain(*self.sigil.name.span, message="This tells me the environment will supply a field name...")
		source.complain(*self.defsym.span, message="Therefore, a 'default' field makes no sense.")


class UndefinedNameError(SemanticError):
	def __init__(self, name:AST.Name, category:str):
		assert isinstance(name, AST.Name)
		assert isinstance(category, str)
		self.name, self.category = name, category
	
	def show(self, source: failureprone.SourceText):
		source.complain(*self.name.span, message="Undefined "+self.category)


class RedefinedNameError(SemanticError):
	def __init__(self, name:AST.Name, original:AST.Name, category:str):
		assert isinstance(name, AST.Name)
		assert isinstance(original, AST.Name)
		assert isinstance(category, str)
		self.name, self.original, self.category = name, original, category

	def show(self, source:failureprone.SourceText):
		source.complain(*self.name.span, message="Redefined "+self.category)
		source.complain(*self.original.span, message="First defined here")


class BadAttributeValue(SemanticError):
	def __init__(self, span, key, description):
		self.span, self.key, self.description = span, key, description
	
	def show(self, source: failureprone.SourceText):
		source.complain(*self.span, message="Value for %s must be %s" % (self.key, self.description))


class NoSuchAttribute(SemanticError):
	
	def show(self, source: failureprone.SourceText):
		source.complain(*self.args[0], message="There is no such formatting attribute")


BLANK_STYLE = collections.ChainMap({
	'_texts':(), '_hint':None,
	'level':0, 'hidden':False, 'collapsed':False,
	'height':None, 'width':None,
})

VOCABULARY = {
	**xl_schema.FORMAT_PROPERTIES,
	**xl_schema.OUTLINE_PROPERTIES,
	**{k: xl_schema.FORMAT_PROPERTIES[v[0]] for k, v in xl_schema.SPECIAL_CASE.items()},
}


class SymbolTable:
	""" I've a sense I'll want a "smart" symbol table object: a bit more than a dictionary. """
	def __init__(self):
		self.__entries = {} # For now entries are just a <Name, object> pair. Keys are strings.
	
	def clear(self):
		self.__entries.clear()
	
	def __contains__(self, item):
		if isinstance(item, str): return item in self.__entries
		if isinstance(item, AST.Name): return item.text in self.__entries
		raise TypeError(item)
	
	def let(self, name:AST.Name, item, kind_text:str):
		""" Enforce single-assignment... """
		assert isinstance(name, AST.Name), type(name)
		key = name.text
		if key in self.__entries: raise RedefinedNameError(name, self.get_declaration(key), kind_text)
		else: self.__entries[key] = (name, item)
	
	def get(self, name:AST.Name):
		try: return self.__entries[name.text][1]
		except KeyError: raise UndefinedNameError(name) from None
	
	def get_declaration(self, key:str) -> AST.Name:
		""" Go find where was the name that declared the symbol. """
		return self.__entries[key][0]
	
	def as_dict(self) -> dict:
		""" Just string keys and semantic items; no location-tracking fluff. """
		return {key: entry[1] for key, entry in self.__entries.items()}
	
	def entries(self): return self.__entries.values()
	

class MidStyled(NamedTuple):
	margin: AST.Marginalia
	content: object

class MidCompound(NamedTuple):
	""" A middle-ground between AST and static structure """
	reader: static.Reader
	kind: str # Literal['frame', 'menu', 'tree'] # Literal is new in Python 3.8.
	argument: object # And as appropriate.

class FieldEntry(NamedTuple):
	shape: object
	routes: SymbolTable

class Transducer(foundation.Visitor):
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
		self.named_fields = SymbolTable()
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
		assert field.zone is None, "It would be ungrammatical and probably nonsense."
		rp = RoutingPass(self)
		midway = rp.visit(field.shape, field.name)
		self.named_fields.let(field.name, FieldEntry(midway, rp.routes), "top-level layout shape")

	def visit_Canvas(self, canvas:AST.Canvas):
		""" Build a static.CanvasDefinition and add it to self.named_canvases """
		def mk_style_rule(sel, elts):
			style_rules.append(veneer.Rule(sel, style_index(elts)))
		
		def style_index(elts):
			env = {}
			self.mutate_style(elts, env)
			return self.make_numbered_style(env)
		
		def adopt_routes(these:dict):
			# I'm making a lot of simplifying assumptions here.
			for k, v in these.items():
				if k not in routes: routes[k] = {}
				routes[k].update(v)
		
		style_rules = []
		formula_rules = []
		merge_rules = []
		routes = {}
		
		# Please note: It's necessary to consider the background style before
		# stylizing the structures.
		background_style = style_index(canvas.style_points)
		for is_merge, selector, content, style in canvas.patches:
			assert isinstance(selector, formulae.Selection)
			if style: mk_style_rule(selector, style)
			if is_merge: merge_rules.append(veneer.Rule(selector, content))
			elif content: formula_rules.append(veneer.Rule(selector, content))
		
		h_struct, h_routes = self.get_styled_field(canvas.across)
		v_struct, v_routes = self.get_styled_field(canvas.down)
		
		adopt_routes(h_routes)
		adopt_routes(v_routes)
		
		self.named_canvases.let(canvas.name, static.CanvasDefinition(
			horizontal=h_struct,
			vertical=v_struct,
			background_style=background_style,
			style_rules=style_rules,
			formula_rules=formula_rules,
			merge_specs=merge_rules,
		), "canvas definition")
		pass
	
	def get_styled_field(self, name:AST.Name) -> Tuple[static.ShapeDefinition, dict]:
		stylist = StylingPass(self, BLANK_STYLE)
		fe = self.named_fields.get(name)
		assert isinstance(fe, FieldEntry)
		shape = stylist.visit(fe.shape)
		assert isinstance(shape, static.ShapeDefinition)
		return shape, fe.routes.as_dict()
	
	def visit_StyleDef(self, styledef:AST.StyleDef):
		"""
		Build up a named-style as a root-level object and store it in the style namespace.
		At least, that's the happy path. Various things can go wrong. What gets reported
		first is sort of a matter of happenstance: what mistake do we stumble over first?
		At any rate, report definitions should not ever get huge, so reporting an error
		and quitting is probably an OK strategy for now.
		"""
		env = {}
		self.mutate_style(styledef.elts, env)
		try: self.named_styles.let(styledef.name, env, "Style Definition")
		except RedefinedNameError as e:
			e.show(self.source)
			raise
	
	def mutate_style(self, elts:List, env:MutableMapping):
		"""
		elts are -- style names, activations, deactivations, or attribute assignments.
		This works by mutating an environment you pass in, so the same code therefore works
		regardless of use in creating named-styles or actually-used styles.
		"""
		def try_assign(name:AST.Name, value, value_span):
			"""
			The key must be a properly recognized style property as defined in module `xl_schema`.
			There are two special cases (`border` and `border_color`) which behave as if corresponding
			top, left, bottom, and right properties are all set at once.
			The value must be consistent with the expectations for the property the key names.
			The spans give locations in a source text to complain about if something goes wrong.
			"""
			key = name.text
			if key not in VOCABULARY: raise NoSuchAttribute(name.span)
			kind = VOCABULARY[key]
			if not kind.test(value): raise BadAttributeValue(value_span, key, kind.description)
			if key in xl_schema.SPECIAL_CASE:
				for k in xl_schema.SPECIAL_CASE[key]: env[k] = value
			else: env[key] = value
		
		for item in elts:
			if isinstance(item, AST.Assign):
				try_assign(item.word, item.const.value, item.const.span)
			elif isinstance(item, AST.Sigil):
				if item.kind == 'ACTIVATE': try_assign(item.name, True, item.name.span)
				elif item.kind == 'DEACTIVATE': try_assign(item.name, False, item.name.span)
				elif item.kind == 'STYLE_NAME': env.update(self.named_styles.get(item.name))
			else: assert False, item
	
	def make_numbered_style(self, env:Mapping) -> int:
		digest = sorted((k, v) for k, v in env.items() if k in xl_schema.FORMAT_PROPERTIES)
		return self.numbered_styles.classify(tuple(digest))
	
	def make_numbered_outline(self, env:Mapping) -> int:
		digest = (env['level'], env['hidden'], env['collapsed'])
		return self.numbered_outlines.classify(digest)

class RoutingPass(foundation.Visitor):
	"""
	This pass's job is to get the proper data-routing and axis
	association bits properly associated with composite structures.
	It replaces the composite AST nodes by MidShape objects,
	but leaves leaf nodes (here, marginalia) untouched.
	In the process it wires up all the named-routes.
	"""
	def __init__(self, mb:Transducer):
		self.mb = mb
		self.space = set()
		self.cursor = {}
		self.routes = SymbolTable()
	
	def visit_Frame(self, frame:AST.Frame, name:AST.Name) -> MidStyled:
		computed, key_text, span = self.__figure_key(frame.key or name)
		children = self.__children(frame.fields, key_text)
		if computed:
			if '_' in children: raise BogusDefaultError(frame.key, children.get_declaration('_'))
			else: reader = static.ComputedReader(key_text)
		elif '_' in children: reader = static.DefaultReader(key_text)
		else: reader = static.SimpleReader(key_text)
		return MidStyled(frame.margin, MidCompound(reader, 'frame', children.as_dict()))
	
	def visit_Menu(self, menu:AST.Menu, name:AST.Name) -> MidStyled:
		computed, key_text, span = self.__figure_key(menu.key or name)
		children = self.__children(menu.fields, key_text)
		assert '_' not in children, "This is grammatically impossible!"
		if computed: reader = static.ComputedReader(key_text)
		else: reader = static.SimpleReader(key_text)
		return MidStyled(menu.margin, MidCompound(reader, 'menu', children.as_dict()))
	
	def visit_Tree(self, tree:AST.Tree, name:AST.Name) -> MidStyled:
		computed, key_text, span = self.__figure_key(tree.key or name)
		if computed: reader = static.ComputedReader(key_text)
		else: reader = static.SimpleReader(key_text)
		pseudo_symbol = AST.Name('per_'+key_text, span)
		within = self.visit(tree.within, pseudo_symbol)
		return MidStyled(tree.margin, MidCompound(reader, 'tree', within))
	
	def visit_Marginalia(self, item:AST.Marginalia, _:AST.Name) -> MidStyled:
		return MidStyled(item, None)
	
	def visit_LinkRef(self, link:AST.LinkRef, _:AST.Name) -> MidStyled:
		fe = self.mb.named_fields.get(link.name)
		assert isinstance(fe, FieldEntry)
		# FIXME: Make sure the space of the shape is acceptable here...
		for k,v in fe.routes.entries():
			self.routes.let(k, v, "Indirectly-named route "+k.text)
		return MidStyled(link.margin, fe.shape)
	
	def __figure_key(self, key):
		# There are three possible key types for Frame and Menu AST nodes: name, sigil, and None.
		if isinstance(key, AST.Name): return False, key.text, key.span
		elif isinstance(key, AST.Sigil):
			assert key.kind == 'COMPUTED', key.kind
			return True, key.name.text, key.name.span
		else:
			assert False, type(key)

	def __children(self, fields:list, key_text:str) -> SymbolTable:
		# Recursion on the children should be a useful trick...
		cursor = self.cursor
		assert key_text not in cursor # Caused by nesting frames with the same axis key. Don't do that.
		children = SymbolTable()
		for field_symbol, zone_symbol, definition in fields:
			cursor[key_text] = field_symbol.text
			if zone_symbol is not None:
				self.routes.let(zone_symbol, cursor.copy(), "named route (within top-level field)")
			children.let(field_symbol, self.visit(definition, field_symbol), "sub-field")
		if fields: del cursor[key_text]
		return children



class StylingPass(foundation.Visitor):
	"""
	Produces the final form of static.ShapeDefinition objects from the
	intermediate form which the RoutingPass computed earlier.
	"""
	def __init__(self, module_builder:Transducer, style_context:collections.ChainMap):
		self.mb = module_builder
		self.sc = style_context
	
	def __static_marginalia(self) -> static.Marginalia:
		return static.Marginalia(
			style_index=self.mb.make_numbered_style(self.sc),
			outline_index=self.mb.make_numbered_outline(self.sc),
			texts=self.sc['_texts'],
			hint=self.sc['_hint'],
			height=self.sc['height'],
			width=self.sc['width'],
		)
	
	def __interpret_hint(self, hint:object):
		if hint is AST.GAP_HINT: return static.Hint(formulae.THE_NOTHING, 999)
		if isinstance(hint, AST.Constant) and hint.kind == 'INT':
			# It's a reference to a perpendicular text. It has precedence above marginal formulas.
			assert isinstance(hint.value, int), hint
			assert hint.value > 0, hint.value
			return hint.value - 1
		boilerplate, prio_spec = hint
		if prio_spec is None: priority = 0
		elif isinstance(prio_spec, AST.Constant):
			assert prio_spec.kind == 'INT'
			priority = prio_spec.value
		else: assert False, type(prio_spec)
		assert isinstance(priority, int)
		return static.Hint(boilerplate, priority)
	
	def visit_NoneType(self, _) -> static.LeafDefinition:
		return static.LeafDefinition(self.__static_marginalia())
	
	def visit_MidStyled(self, ms:MidStyled):
		mb, notes = self.mb, ms.margin
		sub = StylingPass(mb, self.sc.new_child())
		if notes.texts is not None:
			sub.sc['_texts'] = notes.texts
		if notes.hint is not None:
			sub.sc['_hint'] = sub.__interpret_hint(notes.hint)
		mb.mutate_style(notes.appearance, sub.sc)
		return sub.visit(ms.content)
	
	def visit_MidCompound(self, mc:MidCompound) -> static.CompoundShapeDefinition:
		marginalia = self.__static_marginalia()
		if   mc.kind == 'frame':
			return static.FrameDefinition(mc.reader, self.visit(mc.argument), marginalia)
		elif mc.kind == 'menu':
			return static.MenuDefinition(mc.reader, self.visit(mc.argument), marginalia)
		elif mc.kind == 'tree':
			return static.TreeDefinition(mc.reader, self.visit(mc.argument), marginalia)
		else:
			assert False, mc.kind
	
	def visit_dict(self, d:dict) -> dict:
		return {k: self.visit(v) for k,v in d.items()}
	
