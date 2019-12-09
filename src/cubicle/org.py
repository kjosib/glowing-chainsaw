"""
To resolve the tension surrounding the module-split of static/dynamic structure for cubicle objects,
it seems necessary to factor out the topic on which they both seem to depend, which is the tree objects that
organize all the rows and columns.

Thus, this module.

The general description can be found at .../docs/technote.md
"""
from typing import Container
from . import veneer, runtime

class Node:
	""" This is a dynamic layout node, but it's much more a common language for the static and dynamic parts. """

class LeafNode(Node):
	""" Seems a half-decent idea to distinguish... """
	__slots__ = ["margin", "begin", "style_class", "formula_class"]
	def __init__(self, margin: dict):
		self.margin = margin
	def end(self): return self.begin
	def after(self): return self.begin+1

class InternalNode(Node):
	""" This can STILL be empty... """
	__slots__ = ["begin", "size", "children"]
	def __init__(self):
		self.children = {}
	def end(self): return self.begin + self.size - 1
	def after(self): return self.begin + self.size

class Cartographer:
	def __init__(self, begin:int, skin:veneer.PartialClassifier, patch:veneer.PartialClassifier, environment:runtime.Environment):
		self.index = begin
		self.skin = skin
		self.patch = patch
		self.environment = environment
	
	def decorate_leaf(self, node:LeafNode, cursor:dict, first:frozenset, last:frozenset):
		node.begin = self.index
		self.index += 1
		node.style_class = self.skin.classify(self.environment, cursor, first, last)
		node.formula_class = self.patch.classify(self.environment, cursor, first, last)

		
	