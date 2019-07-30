"""
Stuff relating to layout structure.

The AST nodes for layout are mostly in the AST module. This one here does the semantic
transformation to populate the symbol table and participate in actually laying things out.
"""

from typing import NamedTuple, List, Optional, Dict, Type, Union
from . import symbols, streams, AST

GAP = object()

class Frame:
	def __init__(self, axis:streams.AxisReader, scope:symbols.Scope, schedule:List[tuple], style):
		self.axis = axis
		self.scope = scope
		self.schedule = schedule
		self.style = style
		print(style)



class Canvas:
	def __init__(self, down, across):
		pass
