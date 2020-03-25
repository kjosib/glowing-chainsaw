"""
To resolve the tension surrounding the module-split of static/dynamic structure for cubicle objects,
it seems necessary to factor out the topic on which they both seem to depend, which is the tree objects that
organize all the rows and columns.

Thus, this module.

The general description can be found at .../docs/technote.md
"""
from typing import NamedTuple, List, Optional
from numbers import Number
from . import veneer

class Marginalia(NamedTuple):
	""" Corresponds to all the ways you can decorate a shape node. """
	style_index:int = 0
	outline_index:int = 0
	texts:Optional[List[object]] = ()
	formula:Optional[object] = None
	height:Optional[Number] = None
	width:Optional[Number] = None

class Node:
	""" This is a dynamic layout node, but it's much more a common language for the static and dynamic parts. """

class LeafNode(Node):
	""" Seems a half-decent idea to distinguish... """
	__slots__ = ["begin", "margin", "style_class", "formula_class"]
	def __init__(self, margin: Marginalia):
		self.margin = margin
	def end(self): return self.begin
	def after(self): return self.begin+1

class InternalNode(Node):
	""" This can STILL be empty... """
	__slots__ = ["begin", "margin", "style_class", "formula_class", "children", "size"]
	def __init__(self, margin: Marginalia):
		self.margin = margin
		self.children = {}
	def end(self): return self.begin + self.size - 1
	def after(self): return self.begin + self.size
