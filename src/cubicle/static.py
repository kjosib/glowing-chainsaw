"""
This file describes STATIC layout structure AS COMPILED that comes from the last pass of the `.cub` file compiler.
The general description can be found at .../docs/technote.md
"""

from typing import List, NamedTuple, Dict, Mapping, Iterable
from . import org, veneer, runtime

OUTLINE_SCHEMA = {
	'level': int,
	'collapse': bool,
	'hidden': bool,
}

class Reader:
	"""
	Abstract base class for -- certain things.
	"""
	def __init__(self, key:str):
		assert isinstance(key, str)
		self.key = key
	def read(self, point:Mapping, env:runtime.Environment): raise NotImplementedError(type(self))

class SimpleReader(Reader):
	"""
	Simplest form of a reader class. Mainly exists as a jumping-off point, to get something going.
	"""
	def read(self, point:Mapping, env:runtime.Environment): return point[self.key]

class MagicReader(Reader):
	"""
	Vital feature: the environment should be able to provide organizational help.
	"""
	def read(self, point:Mapping, env:runtime.Environment):
		return env.read_magic(self.key, point)

class DefaultReader(SimpleReader):
	"""
	Usable for cosmetic framing; provides '_' if key is absent from point.
	Reader key is self, so make a new object for each cosmetic frame.
	Should not be attached to a tree definition.
	"""
	def read(self, point:Mapping, env:runtime.Environment): return point.get(self.key, '_')


class TextComponent:
	"""
	Can you smell a GOF "interpreter pattern" here? I do.
	"""
	def text(self, cursor:dict, env:runtime.Environment) -> str:
		raise NotImplementedError(type(self))

class LiteralTextComponent(TextComponent):
	def __init__(self, content:str):
		self.content = content
	
	def text(self, cursor: dict, env: runtime.Environment) -> str:
		return self.content

class FieldTextComponent(TextComponent):
	def __init__(self, reader_key:str):
		self.reader_key = reader_key

class RawTextComponent(FieldTextComponent):
	def text(self, cursor:dict, env:runtime.Environment) -> str:
		return str(cursor[self.reader_key])

class PlainTextComponent(FieldTextComponent):
	def text(self, cursor: dict, env: runtime.Environment) -> str:
		return env.plain_text(self.reader_key, cursor[self.reader_key])
	
class AttributeComponent(TextComponent):
	def __init__(self, reader_key:str, attribute:str):
		self.reader_key = reader_key
		self.attribute = attribute
	
	def text(self, cursor: dict, env: runtime.Environment) -> str:
		return env.object_attribute(self.reader_key, self.attribute, cursor['reader_key'])

class Selector:
	"""
	ABC for selecting data zones for applying formulas.
	"""
	def choose_children(self, children:dict):
		raise NotImplementedError(type(self))


class SelectOne(Selector):
	def __init__(self, ordinal):
		self.ordinal = ordinal
	
	def choose_children(self, children:dict):
		if self.ordinal in children: yield (self.ordinal, children[self.ordinal])

class SelectSet(Selector):
	def __init__(self, elements:Iterable):
		self.elements = frozenset(elements)
	
	def choose_children(self, children: dict):
		for ordinal, child in children.items():
			if ordinal in self.elements:
				yield ordinal, child


class Formula:
	"""
	ABC for every sort of thing computed instead of raw data.
	Subclasses implement templates, summations, etc.
	"""
	
	def priority(self) -> int:
		"""
		Formula priority resolves row/column conflicts.
		In general, products and quotients outweigh differences, which outweigh sums.
		"""
		raise NotImplementedError(type(self))
	
	def interpret(self, cursor, plan) -> str:
		raise NotImplementedError(type(self))

class NothingFormula(Formula):
	
	def priority(self) -> int:
		return 900
	
	def interpret(self, cursor, plan) -> str:
		pass

THE_NOTHING = NothingFormula()

class TextTemplateFormula(Formula):
	def __init__(self, components:Iterable[TextComponent]):
		self.components = tuple(components)
	
	def priority(self) -> int:
		return 999
	
	def interpret(self, cursor, plan) -> str:
		return ''.join(c.text(cursor, plan.environment) for c in self.components)

class AutoSumFormula(Formula):
	def __init__(self, criteria:Dict[str, Selector]):
		self.criteria = criteria
		
	def priority(self) -> int:
		return 0

	def interpret(self, cursor, plan) -> str:
		selection = ','.join(plan.data_range(cursor, self.criteria))
		return '=sum('+selection+')'

class MergeSpec:
	def __init__(self, across:Dict[str, Selector], down:Dict[str, Selector], formula:Formula):
		self.across = across
		self.down = down
		self.formula = formula

class ShapeDefinition:
	"""
	This is an abstract superclass/interface describing the possible kinds of (static) axis definitions.
	Note this is going to be a recursive data structure and potentially a DAG because of the way that
	partial axis-definitions may be linked symbolically in the source language.
	
	It also must expose methods for operating over org.Node objects consistently with its actual type.
	"""
	
	def fresh_node(self) -> org.Node:
		""" Return a fresh org.Node subclass object according to whatever sort of axis definition object this is. """
		raise NotImplementedError(type(self))
	
	def accumulate_key_space(self, space:set):
		""" Help prepare a set of key-space within the purview of this ShapeDefinition. """
		raise NotImplementedError(type(self))

	def find_data(self, entries:List[int], tree:org.Node, cursor:dict, criteria:Dict[object, Selector], remain:int):
		""" Accumulate a list of matching (usually data) leaf indexes based on criteria. """
		raise NotImplementedError(type(self))

	def yield_internal(self, tree:org.Node, cursor:dict, criteria:Dict[object, Selector], remain:int):
		""" Yield matching (internal, if possible) nodes. """
		raise NotImplementedError(type(self))

# There must be at least four kinds of ShapeDefinition: leaves, trees, frames, and menus. Maybe "records" also?

class LeafDefinition(ShapeDefinition):
	def __init__(self, margin:org.Marginalia):
		super().__init__()
		assert isinstance(margin, org.Marginalia)
		self.margin = margin
	
	def fresh_node(self):
		return org.LeafNode(self.margin)
	
	def accumulate_key_space(self, space: set):
		pass # Nothing to do here.

	def find_data(self, entries: List[int], tree: org.LeafNode, cursor: dict, criteria: Dict[object, Selector], remain: int):
		if remain == 0:
			entries.append(tree.begin)
	
	def yield_internal(self, tree: org.Node, cursor: dict, criteria: Dict[object, Selector], remain: int):
		if remain == 0: yield tree


class CompoundShapeDefinition(ShapeDefinition):
	"""
	Call it implementation inheritance if you must, but it's expedient, factored, and not too weird.
	This deals in the generalities common to Tree, Frame, and Menu.
	Perhaps those differences are one day factored into strategy objects, but for now, it's good enough.
	"""
	def __init__(self, reader:Reader, margin:org.Marginalia):
		super().__init__()
		self.reader = reader
		self.cursor_key = reader.key
		self.margin = margin
	
	def _descent(self, label) -> ShapeDefinition:
		""" This plugs into the planning algorithm. """
		raise NotImplementedError(type(self))
	
	def _schedule(self, ordinals, env:runtime.Environment) -> list:
		""" This plugs into the planning algorithm. """
		raise NotImplementedError(type(self))

	def fresh_node(self):
		return org.InternalNode(self.margin)
	
	def yield_internal(self, tree: org.InternalNode, cursor: dict, criteria: Dict[object, Selector], remain: int):
		if remain == 0: yield tree
		else:
			if self.cursor_key in criteria:
				items = criteria[self.cursor_key].choose_children(tree.children)
				remain -= 1
			else:
				items = tree.children.items()
			for ordinal, child in items:
				cursor[self.cursor_key] = ordinal
				yield from self._descent(ordinal).yield_internal(child, cursor, criteria, remain)
				del cursor[self.cursor_key]
		
			

class TreeDefinition(CompoundShapeDefinition):
	""" This corresponds nicely to the :tree concept in the language. """
	def __init__(self, reader:Reader, within: ShapeDefinition, margin:org.Marginalia):
		super().__init__(reader, margin)
		self.within = within
	
	def accumulate_key_space(self, space: set):
		space.add(self.cursor_key)
		self.within.accumulate_key_space(space)
	
	def _descent(self, label) -> ShapeDefinition:
		return self.within
	
	def _schedule(self, ordinals, env:runtime.Environment) -> list:
		return sorted(ordinals, key=env.collation(self.cursor_key))
	

class FrameDefinition(CompoundShapeDefinition):
	""" This corresponds to a :frame in the language. "Cosmetic" frames may have a reader that returns a constant. """
	def __init__(self, reader:Reader, fields:dict, margin:org.Marginalia):
		super().__init__(reader, margin)
		self.fields = fields
		self.sequence = list(self.fields.keys())
		pass
	
	def fresh_node(self):
		node = super().fresh_node()
		for label, child in self.fields.items():
			node.children[label] = child.fresh_node()
		return node
	
	def accumulate_key_space(self, space: set):
		# OBSERVATION: Same for FrameDefinition and MenuDefinition (AT THIS TIME).
		space.add(self.cursor_key)
		for within in self.fields.values():
			within.accumulate_key_space(space)
	
	def _descent(self, label) -> ShapeDefinition:
		return self.fields[label]
	
	def _schedule(self, ordinals, env:runtime.Environment) -> list:
		return self.sequence
	

class MenuDefinition(CompoundShapeDefinition):
	"""
	A :menu in the language. Has some things in common with both Tree and Frame.
	In principle, you could accomplish a similar concept with "shy fields", perhaps more flexibly.
	But for now, this works.
	"""
	def __init__(self, reader:Reader, fields:dict, margin:org.Marginalia):
		super().__init__(reader, margin)
		self.fields = fields
		self.__order = {f:i for i,f in enumerate(fields.keys())}
	
	def accumulate_key_space(self, space: set):
		# OBSERVATION: Same for FrameDefinition and MenuDefinition (AT THIS TIME).
		space.add(self.cursor_key)
		for within in self.fields.values():
			within.accumulate_key_space(space)
	
	def _descent(self, label) -> ShapeDefinition:
		return self.fields[label]
	
	def _schedule(self, ordinals, env:runtime.Environment) -> list:
		return sorted(ordinals, key=self.__order.__getitem__)



class CanvasDefinition(NamedTuple):
	"""
	Brings together all the defining characteristics of a single report type.
	"""
	horizontal:ShapeDefinition
	vertical:ShapeDefinition
	style_rules:List[veneer.Rule]
	formula_rules:List[veneer.Rule]
	merge_specs:List[MergeSpec]

class TopLevel(NamedTuple):
	"""
	The uppermost final compiled object: what you expect to get back from "compiling" a `.cub` file.
	You SHOULD be able to pickle one of these objects to avoid repeat-compilation.
	"""
	canvases: Dict[str, CanvasDefinition]
	styles: List[dict]
	outlines: List[tuple]

