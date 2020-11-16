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

class LiteralText(NamedTuple):
	text:str

class PlainOrdinal(NamedTuple):
	""" The environment provides for how to make a value "plain" (human-friendly) given both axis-name and value. """
	axis: str

class RawOrdinal(NamedTuple):
	""" In other words, the internal form of whatever ordinal. The environment need not be consulted. """
	axis: str

class Attribute(NamedTuple):
	""" These have got to be computed. The environment must provides the method. """
	axis: str
	method: str

class HeadRef(NamedTuple):
	""" For these to work, the tree-walk needs to keep track of axis header arrays by axis-name. """
	axis: str
	index: int

class Global(NamedTuple):
	""" The environment provides the corresponding (string) value. """
	name: str

# To make the IDE type-checker happy and yet remain compatible with Py3.9:
TextElement = Union[LiteralText, PlainOrdinal, RawOrdinal, Attribute, HeadRef, Global]

class IsFirst: pass
class IsLast: pass
class IsEqual(NamedTuple):
	distinguished_value: object
class IsInSet(NamedTuple):
	including: frozenset
class IsNotInSet(NamedTuple):
	excluding: frozenset
class IsDefined: pass
class ComputedPredicate(NamedTuple):
	cookie:str

Predicate = Union[IsFirst, IsLast, IsEqual, IsInSet, IsNotInSet, IsDefined, ComputedPredicate]

class Selection(NamedTuple):
	criteria: Dict[str, Predicate]
	
	def projection(self, space:Container) -> "Selection":
		return Selection({k:p for (k, p) in self.criteria.items() if k in space})

class Summation(NamedTuple):
	selection:Selection
	def projection(self, space:Container) -> "Summation":
		return Summation(self.selection.projection(space))

class BlankCell: pass
THE_NOTHING = BlankCell()

class Label(NamedTuple):
	bits: List[TextElement]

class Formula(NamedTuple):
	bits: List[Union[Selection]]

class Quotation(NamedTuple):
	""" Appropriate in formula-context containing strings. """
	content: Label

