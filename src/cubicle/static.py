"""
This file describes STATIC layout structure AS COMPILED that comes from the last pass of the `.cub` file compiler.
The general description can be found at .../docs/technote.md
"""

from typing import List, Optional, NamedTuple, Dict, Mapping, Iterable, Container
from boozetools.support import foundation
from . import org, veneer, runtime, errors

MARGIN_SCHEMA = {
	# This thing is more for documentary purposes than anything...
	'style_index': int,
	'outline_index': int,
	'templates': list,
	'formula': Optional[object],
	'height': Optional[float],
	'width': Optional[float],
}
OUTLINE_SCHEMA = {
	'level': int,
	'collapse': bool,
	'hidden': bool,
}

class Reader:
	"""
	Abstract base class for -- certain things.
	"""
	def reader_key(self): raise NotImplementedError(type(self))
	def read(self, point:Mapping, env:runtime.Environment): raise NotImplementedError(type(self))

class SimpleReader(Reader):
	"""
	Simplest form of a reader class. Mainly exists as a jumping-off point, to get something going.
	"""
	def __init__(self, field_name):
		self._field_name = field_name
	def reader_key(self): return self._field_name
	def read(self, point:Mapping, env:runtime.Environment): return point[self._field_name]

class MagicReader(Reader):
	"""
	Vital feature: the environment should be able to provide organizational help.
	"""
	def __init__(self, magic_name):
		self._magic_name = magic_name
	def reader_key(self): return self._magic_name # Same namespace as regular fields
	def read(self, point:Mapping, env:runtime.Environment):
		return env.read_magic(self._magic_name, point)

class DefaultReader(Reader):
	"""
	Usable for cosmetic framing; provides '_' if key is absent from point.
	Reader key is self, so make a new object for each cosmetic frame.
	Should not be attached to a tree definition.
	"""
	def reader_key(self): return self
	def read(self, point:Mapping, env:runtime.Environment): return point.get(self, '_')


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


class ShapeDefinition:
	"""
	This is an abstract superclass/interface describing the possible kinds of (static) axis definitions.
	Note this is going to be a recursive data structure and potentially a DAG because of the way that
	partial axis-definitions may be linked symbolically in the source language.
	
	It also must expose methods for operating over org.Node objects consistently with its actual type.
	"""
	
	def fresh_node(self):
		""" Return a fresh org.Node subclass object according to whatever sort of axis definition object this is. """
		raise NotImplementedError(type(self))
	
	def key_node(self, node, point: dict, env:runtime.Environment):
		""" Go find the appropriate sub-node for a given point, principally for entering magnitude/attribute data. """
		raise NotImplementedError(type(self))
	
	def accumulate_key_space(self, space:set):
		""" Help prepare a set of key-space within the purview of this ShapeDefinition. """
		raise NotImplementedError(type(self))

	def plan_leaves(self, node, cursor:dict, first:frozenset, last:frozenset, cartographer:org.Cartographer):
		""" Contribute to the preparation of a properly-ordered list of leaf nodes. """
		# Technical note: passing the result list around means NOT ONLY less garbage, but also fewer mistakes.
		raise NotImplementedError(type(self))
	
	def tour(self, node, cursor:dict):
		""" Walk a tree while keeping that cursor up to date; yield the leaf nodes. """
		raise NotImplementedError(type(self))
	
	def find_data(self, entries:List[int], tree:org.Node, cursor:dict, criteria:Dict[object, Selector], remain:int):
		""" Accumulate a list of matching (usually data) leaf indexes based on criteria. """
		raise NotImplementedError(type(self))

	
# There must be at least four kinds of ShapeDefinition: leaves, trees, frames, and menus. Maybe "records" also?

class LeafDefinition(ShapeDefinition):
	def __init__(self, margin: dict):
		super().__init__()
		self.margin = margin
	
	def fresh_node(self):
		return org.LeafNode(self.margin)
	
	def key_node(self, node, point: dict, env:runtime.Environment):
		return node
	
	def accumulate_key_space(self, space: set):
		pass # Nothing to do here.

	def plan_leaves(self, node:org.LeafNode, cursor:dict, first:frozenset, last:frozenset, cartographer:org.Cartographer):
		cartographer.decorate_leaf(node, cursor, first, last)
	
	def tour(self, node:org.LeafNode, cursor: dict):
		yield node
	
	def find_data(self, entries: List[int], tree: org.LeafNode, cursor: dict, criteria: Dict[object, Selector], remain: int):
		if remain == 0:
			entries.append(tree.begin)


class CompoundShapeDefinition(ShapeDefinition):
	"""
	Call it implementation inheritance if you must, but it's expedient, factored, and not too weird.
	This deals in the generalities common to Tree, Frame, and Menu.
	Perhaps those differences are one day factored into strategy objects, but for now, it's good enough.
	"""
	def __init__(self, reader:Reader):
		super().__init__()
		self.reader = reader
		self.cursor_key = reader.reader_key()
	
	def _descent(self, label) -> ShapeDefinition:
		""" This plugs into the planning algorithm. """
		raise NotImplementedError(type(self))
	
	def _schedule(self, ordinals, env:runtime.Environment) -> list:
		""" This plugs into the planning algorithm. """
		raise NotImplementedError(type(self))

	def plan_leaves(self, node:org.InternalNode, cursor: dict, first: frozenset, last: frozenset, cartographer:org.Cartographer):
		def enter(label, first_prime, last_prime):
			cursor[self.cursor_key] = label
			within = self._descent(label)
			within.plan_leaves(node.children[label], cursor, first_prime, last_prime, cartographer)
			del cursor[self.cursor_key]
		# Begin:
		node.first = cartographer.index
		schedule = self._schedule(node.children.keys(), cartographer.environment)
		if len(schedule) == 1:
			# The only element is also the first and last element.
			enter(schedule[0], first|{self.cursor_key}, last|{self.cursor_key})
		elif schedule:
			# There's a first, a possibly-empty middle, and a last element.
			enter(schedule[0], first|{self.cursor_key}, frozenset())
			for i in range(1,len(schedule)-1): enter(schedule[i], frozenset(), frozenset())
			enter(schedule[-1], frozenset(), last|{self.cursor_key})
		node.size = cartographer.index - node.first
	
	def tour(self, node:org.InternalNode, cursor: dict):
		for label, child_node in node.children.items():
			cursor[self.cursor_key] = label
			yield from self._descent(label).tour(child_node, cursor)
			del cursor[self.cursor_key]

	def find_data(self, entries: List[int], tree:org.InternalNode, cursor: dict, criteria: Dict[object, Selector], remain: int):
		if self.cursor_key in criteria:
			for ordinal, child in criteria[self.cursor_key].choose_children(tree.children):
				self._descent(ordinal).find_data(entries, child, cursor, criteria, remain-1)
		elif self.cursor_key in cursor:
			ordinal = cursor[self.cursor_key]
			self._descent(ordinal).find_data(entries, tree.children[ordinal], cursor, criteria, remain)
		else:
			for ordinal, child in tree.children.items():
				self._descent(ordinal).find_data(entries, child, cursor, criteria, remain)
				



class TreeDefinition(CompoundShapeDefinition):
	""" This corresponds nicely to the :tree concept in the language. """
	def __init__(self, reader:Reader, within: ShapeDefinition):
		super().__init__(reader)
		self.within = within
	
	def fresh_node(self):
		return org.InternalNode()
	
	def key_node(self, node, point: dict, env:runtime.Environment):
		ordinal = self.reader.read(point, env)
		try: branch = node.children[ordinal]
		except KeyError: branch = node.children[ordinal] = self.within.fresh_node()
		return self.within.key_node(branch, point, env)
	
	def accumulate_key_space(self, space: set):
		space.add(self.cursor_key)
		self.within.accumulate_key_space(space)
	
	def _descent(self, label) -> ShapeDefinition:
		return self.within
	
	def _schedule(self, ordinals, env:runtime.Environment) -> list:
		return sorted(ordinals, key=env.collation(self.cursor_key))
	

class FrameDefinition(CompoundShapeDefinition):
	""" This corresponds to a :frame in the language. "Cosmetic" frames may have a reader that returns a constant. """
	def __init__(self, reader:Reader, fields:dict):
		super().__init__(reader)
		self.fields = fields
		self.sequence = list(self.fields.keys())
		pass
	
	def fresh_node(self):
		node = org.InternalNode()
		for label, child in self.fields.items():
			node.children[label] = child.fresh_node()
		return node
	
	def key_node(self, node, point: dict, env:runtime.Environment):
		ordinal = self.reader.read(point, env)
		try: branch = node.children[ordinal]
		except KeyError: raise errors.InvalidOrdinalError(self.cursor_key, ordinal)
		else: return self.fields[ordinal].key_node(branch, point, env)
	
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
	A :menu in the language. Some in common with both Tree and Frame.
	In principle, you could accomplish a similar concept with "shy fields", perhaps more flexibly.
	But for now, this works.
	"""
	def __init__(self, reader:Reader, fields:dict):
		super().__init__(reader)
		self.fields = fields
		self.__order = {f:i for i,f in enumerate(fields.keys())}
	
	def fresh_node(self):
		return org.InternalNode()
	
	def key_node(self, node, point: dict, env:runtime.Environment):
		ordinal = self.reader.read(point, env)
		try: within = self.fields[ordinal]
		except KeyError: raise errors.InvalidOrdinalError(self.cursor_key, ordinal)
		else:
			try: branch = node.children[ordinal]
			except KeyError: branch = node.children[ordinal] = within.fresh_node()
			return within.key_node(branch, point)

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

class TopLevel(NamedTuple):
	"""
	The uppermost final compiled object: what you expect to get back from "compiling" a `.cub` file.
	You SHOULD be able to pickle one of these objects to avoid repeat-compilation.
	"""
	canvases: Dict[str, CanvasDefinition]
	styles: List[dict]
	outlines: List[dict]

