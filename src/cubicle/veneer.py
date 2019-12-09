"""
This file describes all the formatting instructions that come out of a definition in the
DSL, and how they are reconciled against each other.

It's very deliberately build up from many small cooperating parts.

"""

import operator
from typing import NamedTuple, List, Container
from boozetools.support import foundation
from . import runtime

class Predicate:
	"""
	Participates in the selection of style rules.
	So, four kinds of predicates.
	"""
	
	def __init__(self, cursor_key):
		self.cursor_key = cursor_key
	
	def is_relevant(self, space:Container) -> bool:
		return self.cursor_key in space
	
	def test_predicate(self, cursor:dict, first:Container, last:Container, environment:runtime.Environment) -> bool:
		raise NotImplementedError(type(self))

class FirstPredicate(Predicate):
	def test_predicate(self, cursor: dict, first: Container, last: Container, environment:runtime.Environment) -> bool:
		return self.cursor_key in first


class LastPredicate(Predicate):
	def test_predicate(self, cursor: dict, first: Container, last: Container, environment:runtime.Environment) -> bool:
		return self.cursor_key in last


class CursorEqualsPredicate(Predicate):
	def __init__(self, cursor_key, distinguished_value):
		super().__init__(cursor_key)
		self.distinguished_value = distinguished_value
	
	def test_predicate(self, cursor:dict, first:Container, last:Container, environment:runtime.Environment) -> bool:
		try: return cursor[self.cursor_key] == self.distinguished_value
		except KeyError: return False

class CursorPluginPredicate(Predicate):
	# This ultimately needs to consult some sort of plug-in data...

	def __init__(self, cursor_key, environmental_predicate_name):
		super().__init__(cursor_key)
		self.environmental_predicate_name = environmental_predicate_name
	
	def test_predicate(self, cursor: dict, first: Container, last: Container, environment:runtime.Environment) -> bool:
		try: ordinal = cursor[self.cursor_key]
		except KeyError: return False
		else: return environment.test_predicate(self.environmental_predicate_name, ordinal)
	

class Rule(NamedTuple):
	"""
	Associates zero or more selection criteria (predicates) with styling rules.
	"""
	predicate_list: List[Predicate]
	payload: int # Style or Formula references, appropriately to context.
	def relevant_predicates(self, space:Container) -> List[Predicate]:
		return [p for p in self.predicate_list if p.is_relevant(space)]


class PartialClassifier:
	"""
	In concept, a rule may be guarded by both horizontal and vertical predicates.
	Given a set of rules, this object builds a filter that is sensitive in one direction
	and permissive in the other direction. Whenever both orthogonal directions permit
	the same rule, that rule applies to corresponding cells in a notional grid.
	So the way this works is to number the DISTINCT sets of selected rules in either
	direction, and then the cross product of these distinct sets should be much easier
	to work with than recomputing a format (or formula) for each cell.
	"""
	def __init__(self, space:Container, rules:List[Rule]):
		self._relevant_predicates = [rule.relevant_predicates(space) for rule in rules]
		self._ec = foundation.EquivalenceClassifier()

	def classify(self, environment:runtime.Environment, cursor:dict, first:Container, last:Container):
		def test(ps: List[Predicate]):
			return all(p.test_predicate(cursor, first, last, environment) for p in ps)
		return self._ec.classify(tuple(test(ps) for ps in self._relevant_predicates))

	def mask(self, cls:int) -> frozenset:
		return self._ec.exemplars[cls]

class CrossClassifier:
	"""
	This makes the styling and formula selection algorithms more clear.
	"""
	def __init__(self, rules:List[Rule], hspace:Container, vspace:Container):
		self.across = PartialClassifier(hspace, rules)
		self.down = PartialClassifier(vspace, rules)
	def select(self, col_cls, row_cls):
		mask = map(operator.and_, self.across.mask(col_cls), self.down.mask(row_cls))
		return [i for i,b in enumerate(mask) if b]
