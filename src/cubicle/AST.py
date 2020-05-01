"""
Library of AST nodes built by the grammar compiler and walked by the transducer.
This file is an organizational tool as much as anything.
One thing: For a post-parse pass to show errors in context, it's necessary to
pass location information around in all the right places.
"""

from typing import NamedTuple, List, Optional, Union, Tuple

class Name(NamedTuple):
	text: str
	span: Tuple[int, int]

class Constant(NamedTuple):
	value: object
	span: Tuple[int, int]
	kind: str

class Assign(NamedTuple):
	# word is either a formatting or outlining property
	word: Name
	const: Constant

class StyleDef(NamedTuple):
	name: Name
	elts: list

class Marginalia(NamedTuple):
	texts: list
	hint: object # If an integer, then a head-hint. If 'gap', a gap. If a tuple, a function or formula and priority.
	appearance: List[Union[Assign, Name]] # Words shall mean style references.

class Field(NamedTuple):
	name:Name
	shape:object # Marginalia -> Leaf; Name -> named shape; Frame/Menu/Tree: define as such.

class Frame(NamedTuple):
	margin:Marginalia
	key:Union[Name, Constant, None]
	fields:list
	
class Menu(NamedTuple):
	margin:Marginalia
	key:Union[Name, Constant]
	fields:list
	
class Tree(NamedTuple):
	margin:Marginalia
	key:Union[Name, Constant, None]
	within:object
	
class Canvas(NamedTuple):
	name:Name
	across:Name
	down:Name
	items:list

class Friendly(NamedTuple):
	""" Means the enclosed expression is to be converted to friendly-form before being emitted into whatever template. """
	field_name:Name

class Raw(NamedTuple):
	""" The enclosed expression is to be emitted in the internal form. If it's the only element of a template, it may have numeric type. """
	field_name:Name

class SelectSet(NamedTuple):
	fields:List[Name]

class SelectNotSet(NamedTuple):
	fields:List[Name]

class SelectEach(NamedTuple):
	pass
the_each = SelectEach()

class SelectComputed(NamedTuple):
	cookie:Constant

class Criterion(NamedTuple):
	field_name:Name
	predicate:Union[SelectSet, SelectNotSet, SelectEach, SelectComputed]

class Selector(NamedTuple):
	criteria:List[Criterion]

class Formula(NamedTuple):
	fragments:list
