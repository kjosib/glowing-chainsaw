"""
This file describes all the formatting instructions that come out of a definition in the
DSL, and how they are reconciled against each other.

Small cooperating parts are the order of the day...

"""

import operator
from typing import List, Container, Generic, TypeVar
from boozetools.support import foundation
from . import formulae, runtime

class PlanState(foundation.Visitor):
	def __init__(self, cursor:dict, first:frozenset, last:frozenset, environment:runtime.Environment):
		self.cursor = cursor
		self.first = first
		self.last = last
		self.environment = environment
		
	def prime(self, key, label, is_first, is_last):
		def tweak(some_set, is_member): return some_set | {key} if is_member else frozenset()
		return PlanState({**self.cursor, key:label}, tweak(self.first, is_first), tweak(self.last, is_last), self.environment)
	
	def visit_Selection(self, sel:formulae.Selection) -> bool:
		return all(self.visit(p, k) for k,p in sel.criteria.items())
	
	def visit_IsFirst(self, _, k): return k in self.first
	def visit_IsLast(self, _, k): return k in self.last
	def visit_IsEqual(self, p, k):
		try: return self.cursor[k] == p.distinguished_value
		except KeyError: return False
	def visit_IsInSet(self, p, k):
		try: return self.cursor[k] in p.including
		except KeyError: return False
	def visit_IsNotInSet(self, p, k):
		try: return not self.cursor[k] in p.excluding
		except KeyError: return False
	def visit_IsDefined(self, _, k):
		return k in self.cursor
	def visit_ComputedPredicate(self, p:formulae.ComputedPredicate, k:str):
		try: ordinal = self.cursor[k]
		except KeyError: return False
		else: return self.environment.test_predicate(p.cookie, ordinal, k)

T = TypeVar("T")
class Rule(Generic[T]):
	"""
	Associates zero or more selection criteria with {styling rules, formulae, etc.}.
	"""
	def __init__(self, selection: formulae.Selection, payload: T):
		self.selection = selection
		self.payload = payload


class PartialClassifier:
	"""
	In concept, a rule may be guarded by both horizontal and vertical predicates.
	Given a set of rules, this object builds a filter that is sensitive in one direction
	and permissive in the other direction. Whenever both orthogonal directions permit
	the same rule, that rule applies to corresponding cells in a notional grid.
	So the way this works is to number the DISTINCT sets of selected rules in either
	direction, and then the cross product of these distinct sets should be much easier
	to work with than recomputing a format (or hint) for each cell.
	"""
	def __init__(self, space:Container, rules:List[Rule]):
		self._relevant_predicates = [rule.selection.projection(space) for rule in rules]
		self._ec = foundation.EquivalenceClassifier()

	def classify(self, visitor:PlanState):
		return self._ec.classify(tuple(visitor.visit(ps) for ps in self._relevant_predicates))

	def mask(self, cls:int) -> frozenset:
		return self._ec.exemplars[cls]

class CrossClassifier:
	"""
	This makes the styling and hint selection algorithms more clear.
	"""
	def __init__(self, rules:List[Rule], hspace:Container, vspace:Container):
		self.across = PartialClassifier(hspace, rules)
		self.down = PartialClassifier(vspace, rules)
	def select(self, col_cls, row_cls):
		mask = map(operator.and_, self.across.mask(col_cls), self.down.mask(row_cls))
		return [i for i,b in enumerate(mask) if b]


