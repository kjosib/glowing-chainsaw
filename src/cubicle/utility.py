"""
Some utility functions and classes that should make life easier everywhere else.
"""
import pathlib, tempfile, pickle
from typing import Iterable
from xlsxwriter.utility import xl_rowcol_to_cell, xl_range


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
	try: begin = current = next(traversal)
	except StopIteration: return result
	for k in traversal:
		if k == current + 1: current = k
		else:
			stash()
			begin = current = k
	stash()
	return result

def tables(basis, doc) -> dict:
	"""
	Perhaps this routine belies a deficiency in the stack, but the object is to be able to
	compile the grammar only once (or whenever it changes) and use it over and over.
	In a fully-packaged solution a pre-pickled table may seem desirable, but for now
	this adaptive approach is better for hacking on.
	"""
	grammar_path = pathlib.Path(basis).parent/doc
	cache_path = pathlib.Path(tempfile.gettempdir())/(doc+'.pickle')
	if cache_path.exists() and cache_path.stat().st_mtime > grammar_path.stat().st_mtime:
		return pickle.load(open(cache_path, 'rb'))
	else:
		from boozetools.macroparse import compiler
		result = compiler.compile_file(grammar_path, method='LR1')
		pickle.dump(result, open(cache_path, 'wb'))
		return result
