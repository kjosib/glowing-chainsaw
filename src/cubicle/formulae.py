"""
This file began as a sort of "mini-AST" to a simple expression-language
for both label-type templates and formulas, independent of the surrounding
language of layout structures.

The structures in here are assumed to be final-form, pre-checked for any
necessary semantic constraints. Also, they are entirely passive data, like
instructions for some other machine to process. The strategy for doing so is
naturally to subclass `Visitor`, given in the boozetools `foundation` module.

FIXME: Unfortunately, such semantic checks aren't all done and some few might
 not even be possible until runtime, so some debug-trace fields would not hurt.
 That implies the ability to HANDLE a run-time error...
"""

from typing import NamedTuple, List, Union, Dict, Container

class TextElement:
	""" ABC for things that can appear in EITHER a label OR a formula """

class LiteralText(TextElement, NamedTuple):
	text:str

class PlainOrdinal(TextElement, NamedTuple):
	""" The environment provides for how to make a value "plain" (human-friendly) given both axis-name and value. """
	axis: str

class RawOrdinal(TextElement, NamedTuple):
	""" In other words, the internal form of whatever ordinal. The environment need not be consulted. """
	axis: str

class Attribute(TextElement, NamedTuple):
	""" These have got to be computed. The environment must provides the method. """
	axis: str
	method: str

class HeadRef(TextElement, NamedTuple):
	""" For these to work, the tree-walk needs to keep track of axis header arrays by axis-name. """
	axis: str
	index: int

class Global(TextElement, NamedTuple):
	""" The environment provides the corresponding (string) value. """
	name: str


class Predicate:
	""" ABC for things we know how to test... """

class IsFirst(Predicate): pass
class IsLast(Predicate): pass
class IsEqual(Predicate, NamedTuple):
	distinguished_value: object
class IsInSet(Predicate, NamedTuple):
	including: frozenset
class IsNotInSet(Predicate, NamedTuple):
	excluding: frozenset
class IsDefined(Predicate): pass
class ComputedPredicate(Predicate, NamedTuple):
	cookie:str


class Selection(NamedTuple):
	criteria: Dict[str, Predicate]
	
	def projection(self, space:Container) -> "Selection":
		return Selection({k:p for (k, p) in self.criteria.items() if k in space})

class Summation(NamedTuple):
	selection:Selection
	def projection(self, space:Container) -> "Summation":
		return Summation(self.selection.projection(space))

class Boilerplate:
	""" ABC for things the language can specify for a cell. """

class BlankCell(Boilerplate): pass
THE_NOTHING = BlankCell()

class RawCell(Boilerplate, NamedTuple):
	axis:str

class Label(Boilerplate, NamedTuple):
	bits: List[TextElement]

class Formula(Boilerplate, NamedTuple):
	bits: List[Union[TextElement, Selection]]

class Quotation(TextElement, NamedTuple):
	""" Appropriate in formula-context containing strings. """
	content: Label

