"""
This file describes STATIC layout structure AS COMPILED that comes from the last pass of the `.cub` file compiler.
The general description can be found at .../docs/technote.md
"""

from typing import List, NamedTuple, Dict, Optional, Union
from numbers import Number
from . import veneer, formulae

####################

class Reader:
	"""
	Abstract base class for -- one single (partially-applied) function which
		in particular can be pickled. A bit heavy, but it ain't broke.
	All "sigil" keys get a ComputedReader.
	Rules: If a Frame has an '_' field and a normal-named key, it gets a DefaultReader.
	Other normal-keys get a SimpleReader.
	A menu may not (indeed grammatically cannot) have an '_' field.
	"""
	def __init__(self, key:str):
		assert isinstance(key, str)
		self.key = key

class SimpleReader(Reader): pass
class ComputedReader(Reader): pass
class DefaultReader(Reader): pass

####################

class Hint(NamedTuple):
	boilerplate: Union[formulae.TextElement, formulae.Formula, formulae.BlankCell]
	priority: int

class Marginalia(NamedTuple):
	""" Corresponds to all the ways you can decorate a shape node. """
	style_index:int = 0
	outline_index:int = 0
	texts:Optional[List[object]] = ()
	hint:Union[int, Hint, None] = None # If this is an integer, it means use the perpendicular header text in that slot.
	height:Optional[Number] = None
	width:Optional[Number] = None

####################

class ShapeDefinition:
	"""
	Abstractly, a static definition for part of the extent (either horizontal
	or vertical) of a class of reports. A recursive data structure and
	potentially a DAG because of the way that partial axis-definitions may be
	linked symbolically in the source language.
	"""

	def __init__(self, margin:Marginalia):
		assert isinstance(margin, Marginalia), type(margin)
		self.margin = margin

	def accumulate_key_space(self, space:set):
		""" Help prepare a set of key-space within the purview of this ShapeDefinition. """
		raise NotImplementedError(type(self))

# There must be at least four kinds of ShapeDefinition: leaves, trees, frames, and menus. Maybe "records" also?

class LeafDefinition(ShapeDefinition):
	
	def accumulate_key_space(self, space: set):
		pass # Nothing to do here.


class CompoundShapeDefinition(ShapeDefinition):
	"""
	Call it implementation inheritance if you must, but it's expedient, factored, and not too weird.
	This deals in the generalities common to Tree, Frame, and Menu.
	Perhaps those differences are one day factored into strategy objects, but for now, it's good enough.
	"""
	def __init__(self, reader:Reader, margin:Marginalia):
		super().__init__(margin)
		self.reader = reader
		self.cursor_key = reader.key
	
	def descend(self, label) -> ShapeDefinition:
		""" This plugs into the planning algorithm. """
		raise NotImplementedError(type(self))
	

class TreeDefinition(CompoundShapeDefinition):
	""" This corresponds nicely to the :tree concept in the language. """
	def __init__(self, reader:Reader, within: ShapeDefinition, margin:Marginalia):
		super().__init__(reader, margin)
		self.within = within
	
	def accumulate_key_space(self, space: set):
		space.add(self.cursor_key)
		self.within.accumulate_key_space(space)
	
	def descend(self, label) -> ShapeDefinition:
		return self.within
	

class FrameDefinition(CompoundShapeDefinition):
	""" This corresponds to a :frame in the language. "Cosmetic" frames may have a reader that returns a constant. """
	def __init__(self, reader:Reader, fields:dict, margin:Marginalia):
		super().__init__(reader, margin)
		self.fields = fields
		self.sequence = list(self.fields.keys())
		pass
	
	def accumulate_key_space(self, space: set):
		# OBSERVATION: Same for FrameDefinition and MenuDefinition (AT THIS TIME).
		space.add(self.cursor_key)
		for within in self.fields.values():
			within.accumulate_key_space(space)
	
	def descend(self, label) -> ShapeDefinition:
		return self.fields[label]
	

class MenuDefinition(CompoundShapeDefinition):
	"""
	A :menu in the language. Has some things in common with both Tree and Frame.
	In principle, you could accomplish a similar concept with "shy fields", perhaps more flexibly.
	But for now, this works.
	"""
	def __init__(self, reader:Reader, fields:dict, margin:Marginalia):
		super().__init__(reader, margin)
		self.fields = fields
	
	def accumulate_key_space(self, space: set):
		# OBSERVATION: Same for FrameDefinition and MenuDefinition (AT THIS TIME).
		space.add(self.cursor_key)
		for within in self.fields.values():
			within.accumulate_key_space(space)
	
	def descend(self, label) -> ShapeDefinition:
		return self.fields[label]

####################

class CanvasDefinition(NamedTuple):
	""" Brings together all the defining characteristics of a single report type. """
	horizontal:ShapeDefinition
	vertical:ShapeDefinition
	background_style:int
	style_rules:List[veneer.Rule[int]]
	formula_rules:List[veneer.Rule[formulae.Formula]]
	merge_specs:List[veneer.Rule[formulae.Formula]]
	zones:Dict[str,Dict[str,str]]

class OutlineData(NamedTuple):
	level: int
	hidden: bool
	collapsed: bool

class CubModule(NamedTuple):
	"""
	The uppermost final compiled object: what you expect to get back from "compiling" a `.cub` file.
	You SHOULD be able to pickle one of these objects to avoid repeat-compilation.
	"""
	canvases: Dict[str, CanvasDefinition]
	styles: List[dict]
	outlines: List[OutlineData]

