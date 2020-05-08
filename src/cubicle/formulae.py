"""
I face an odd pressure at the moment:

I'd eventually like to support a proper (if simple) expression language for
both label-type templates and formulas. Whatever had been in before was -- wrong.
So here's a static structure JUST FOR THAT MINI-LANGUAGE, independent of the
surrounding language of layout structures.

The structures in here are assumed to be final-form, pre-checked for any
necessary semantic constraints. Also, they are entirely passive data, like
instructions for some other machine to process. The strategy for doing so is
naturally to subclass `Visitor`, given in the boozetools `foundation` module.
"""

from typing import NamedTuple, List, Union, Tuple, Container

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

# class SelectOne(Predicate):
# 	def __init__(self, ordinal):
# 		self.ordinal = ordinal
#
	# def choose_children(self, children: dict):
	# 	if self.ordinal in children: yield (self.ordinal, children[self.ordinal])

# class SelectSet(Predicate):
# 	def __init__(self, elements: Iterable):
# 		self.elements = frozenset(elements)
#
	# def choose_children(self, children: dict):
	# 	for ordinal, child in children.items():
	# 		if ordinal in self.elements:
	# 			yield ordinal, child


class Selection(NamedTuple):
	criteria: List[Tuple[str, Predicate]]
	
	def projection(self, space:Container) -> "Selection":
		return Selection([(k, p) for (k, p) in self.criteria if k in space])


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

