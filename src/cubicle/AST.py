"""
Library of AST nodes built by the grammar compiler and walked by the transducer.
This file is an organizational tool as much as anything.
One thing: For a post-parse pass to show errors in context, it's necessary to
pass location information around in all the right places.
"""

from typing import NamedTuple, List, Union, Tuple
from . import formulae

class Name(NamedTuple):
	text: str
	span: Tuple[int, int]

class Sigil(NamedTuple):
	name: Name
	kind: str

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

GAP_HINT = object()

class Marginalia(NamedTuple):
	texts: list
	hint: object # If an integer, then a head-hint. If GAP_HINT, a gap. If a tuple, a function or formula and priority.
	appearance: List[Union[Assign, Name]] # Words shall mean style references.

class Field(NamedTuple):
	name:Name
	zone:Name
	shape:object # Marginalia -> Leaf; Name -> named shape; Frame/Menu/Tree: define as such.

class Frame(NamedTuple):
	margin:Marginalia
	key:Union[Name, Sigil, None]
	fields:list
	
class Menu(NamedTuple):
	margin:Marginalia
	key:Union[Name, Sigil, None]
	fields:list
	
class Tree(NamedTuple):
	margin:Marginalia
	key:Union[Name, Sigil, None]
	within:object

class LinkRef(NamedTuple):
	margin: Marginalia
	name: Name
	
class Canvas(NamedTuple):
	name:Name
	across:Name
	down:Name
	style_points:list
	patches:list

class Criterion(NamedTuple):
	field_name: Name
	predicate: formulae.Predicate

class Patch(NamedTuple):
	is_merge: bool
	criteria: List[Criterion]
	content: object
	style_points: list

class PatchBlock(NamedTuple):
	criteria: List[Criterion]
	sub_patches: List[Union[Patch, "PatchBlock"]]

class MagicSum(NamedTuple):
	criteria: List[Union[Sigil, Criterion]]

class RawRange(NamedTuple):
	criteria: List[Union[Sigil, Criterion]]
