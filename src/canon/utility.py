"""
Some utility functions and classes that should make life easier everywhere else.
"""
from typing import Iterable
from xlsxwriter.utility import xl_rowcol_to_cell, xl_range

class Visitor:
	"""
	Visitor-pattern in Python, with fall-back to superclasses along the MRO.
	
	Actual visitation-algorithms will inherit from Visitor and then each
	`visit_Foo` method must call `self.visit(host.bar)` as appropriate. This
	is so that your visitation-algorithm is in control of which bits of an
	object-graph that it actually visits, and in what order.
	"""
	def visit(self, host, *args, **kwargs):
		method_name = 'visit_'+host.__class__.__name__
		try: method = getattr(self, method_name)
		except AttributeError:
			# Searching the MRO incurs whatever cost there is to set up an iterator.
			for cls in host.__class__.__mro__:
				fallback = 'visit_'+cls.__name__
				if hasattr(self, fallback):
					method = getattr(self, fallback)
					break
			else: raise
		return method(host, *args, **kwargs)


def make_range(col_run, row_run):
	if isinstance(col_run, int) and isinstance(row_run, int): return xl_rowcol_to_cell(row_run, col_run)
	else:
		if isinstance(col_run, int): left = right = col_run
		else: left, right = col_run
		if isinstance(row_run, int): top = bottom = row_run
		else: top, bottom = row_run
		return xl_range(top, left, bottom, right)


def collapse_runs(entries: Iterable[int]):
	""" Performs a simple run-length encoding. Runs of consecutive integers become <first,last> tuples. """
	
	def stash(): result.append(begin if begin == current else (begin, current))
	
	result = []
	traversal = iter(entries)
	begin = current = next(traversal)
	for k in traversal:
		if k == current + 1: current = k
		else:
			stash()
			begin = current = k
	stash()
	return result

