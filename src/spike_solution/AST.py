"""
Don't expect to see every kind of AST node in this file.

Most of the AST nodes are just NamedTuple classes, possibly with a few extra methods
where it makes sense. Some portion of the semantic interpretation happens during the
parse (in cradle.py, class Driver) but not all.

The AST is built bottom-up, but symbol scopes need a link to parent scope, which is
an inherited (not synthesized) attribute. Therefore, the first thing you do with an
AST is a big tree-walk to collect definitions into a proper symbol table.
"""
from typing import NamedTuple, List, Optional, Union
from spike_solution import symbols


#################################################################
## Styles:
#################################################################

class Attribute(NamedTuple):
	kind: str
	ident: symbols.Identifier

class Assignment(NamedTuple):
	property: Attribute
	value: object

FORMAT_ELEMENT = Union[Assignment, symbols.REFERENCE]

class Style(NamedTuple):
	elements: List[FORMAT_ELEMENT]

#################################################################
## Labels (Templates) and Formulas:
#################################################################

# A template is just a list of elements, either text or replacements.
# Text is just a string.

class Replacement(NamedTuple):
	axis: symbols.Identifier
	view: Optional[symbols.Identifier]

class FunctionCall(NamedTuple):
	stem: symbols.Identifier
	args: List[symbols.REFERENCE]


#################################################################
## Layout:
#################################################################

class Leaf(NamedTuple):
	"""
	This is your garden-variety data definition node. It stands for a leaf definition
	in a .cub file. There are several kinds, and rather than having several different,
	but very similar, kinds of object, it makes more sense to configure one kind of
	object with different specific strategies. The parse driver de-sugars the syntax.
	"""
	is_head: bool
	template: Optional[list]
	style: Optional[tuple] # the pair (hint, format) to be interpreted in context.


class LayoutTree(NamedTuple):
	""" Provides for ordinary data-driven fan-out to homogeneous subordinate layout structures. """
	axis: symbols.REFERENCE
	child: object


class LayoutFrame(NamedTuple):
	""" Provides for fixed-layout structures. Styles apply to subordinates unless overridden. """
	axis: Optional[symbols.REFERENCE]  # If an axis appears, it routes data. Otherwise, route to the underscore-key by default.
	style: Optional[Style]
	fields: list


class LayoutMenu(NamedTuple):
	""" A hybrid between tree and frame layout: A field only appears if its name appears as an ordinal in the data. """
	axis: symbols.REFERENCE
	style: Optional[Style]
	fields: list


class LayoutLike(NamedTuple):
	reference: symbols.REFERENCE
	style: Optional[Style]


#################################################################
## Overall .cub Module Structure:
#################################################################

class NameSpace(NamedTuple):
	declarations: list

class Canvas(NamedTuple):
	down: symbols.REFERENCE
	across: symbols.REFERENCE
	format: List[FORMAT_ELEMENT]
