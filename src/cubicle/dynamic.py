"""
This file describes the DYNAMIC structure of a fully instantiated object DEFINED in a `.cub` file.
There is a bit of an odd dependency loop here. To resolve it, I think it's necessary to factor out
the common data structure which is a "layout tree".

The general description can be found at .../docs/technote.md
"""

import collections
from typing import Optional, Dict, Iterable
from xlsxwriter.utility import xl_rowcol_to_cell, xl_range
from . import static, runtime, org, veneer

class Canvas:
	"""
	This is the actual object that collects actual data for actual plotting into an actual spreadsheet somewhere.
	It naturally refers back to its definition structure, but also to relevant per-instance data.
	
	Stylistic note: It would be entirely possible to host all functionality within the structure
	and require client code to pass in both but then client code might accidentally get it wrong...
	It's better this way I think. At least for the overall canvas object.
	"""
	def __init__(self, toplevel:static.TopLevel, identifier:str, environment:runtime.Environment):
		self.toplevel = toplevel # This turns out to get consulted...
		self.definition = toplevel.canvases[identifier]
		self.environment = environment
		self.cell_data = collections.defaultdict(int)
		self.across = Direction(self.definition.horizontal, environment)
		self.down = Direction(self.definition.vertical, environment)
		intersection = self.across.space & self.down.space
		assert not intersection, intersection
		
	# A few routines for plugging data into a grid:
	
	def poke(self, point, value):
		self.cell_data[self.key_pair(point)] = value
	
	def incr(self, point, value):
		self.cell_data[self.key_pair(point)] += value
	
	def decr(self, point, value):
		self.cell_data[self.key_pair(point)] -= value
	
	def key_pair(self, point):
		return self.across.key_node(point), self.down.key_node(point)
	
	# It's sometimes necessary to remove rows and/or columns that are, for instance, all zero or nearly so.
	# The relevant
	
	# Since all the cosmetic surgery is performed in the language, it's therefore all represented in
	# the .definition object, and thus we can proceed on to plotting.
	
	def plot(self, workbook, sheet, top_row_index:int, left_column_index:int, blank=None):
		""" Argument order (row/column) is here consistent with xlsxwriter. """
		
		def find_format():
			"""
			For styling, the concept is simple enough: You take the margin styles as a background and then overlay
			that with any extra bits that are specified in the canvas definition as style rules.
			"""
			col_style = col_margin.style_index
			row_style = row_margin.style_index
			col_cls = col_node.style_class
			row_cls = row_node.style_class
			fmt_key = col_style, row_style, col_cls, row_cls
			try: return style_cache[fmt_key]
			except:
				styles = self.toplevel.styles
				rules = self.definition.style_rules
				bits = [styles[col_style], styles[row_style]]
				for i in skin.select(col_cls, row_cls): bits.append(styles[rules[i].payload])
				bits.reverse()
				it = style_cache[fmt_key] = workbook.add_format(collections.ChainMap(*bits))
				return it
			pass
		
		def template(index, yon):
			if isinstance(index, int):
				them = yon.texts
				if index < len(them):
					it = them[index]
					assert isinstance(it, static.Formula)
					return it
				else: return static.THE_NOTHING
		
		def compete(a:Optional[static.Formula], b:Optional[static.Formula]):
			if a is None: return b
			if b is None: return a
			if b.priority() > a.priority(): return b
			return a
		
		def find_formula():
			"""
			Determining which formula applies is a bit more of a trick.
			"""
			cf, rf = col_margin.formula, row_margin.formula
			if 'gap' in (cf, rf): return None
			formula = check_patch()
			if formula is None: formula = template(cf, row_margin)
			if formula is None: formula = template(rf, col_margin)
			if formula is None: formula = compete(cf, rf)
			return self.cell_data.get((col_node, row_node), blank) if formula is None else formula.interpret(cursor, self)
		
		def check_patch():
			patch_key = col_node.formula_class, row_node.formula_class
			try: return formula_cache[patch_key]
			except KeyError:
				candidates = patch.select(*patch_key)
				it = formula_cache[patch_key] = candidates[-1] if candidates else None
				return it
		
		style_cache = {}
		formula_cache = {}
		skin = veneer.CrossClassifier(self.definition.style_rules, self.across.space, self.down.space)
		patch = veneer.CrossClassifier(self.definition.formula_rules, self.across.space, self.down.space)
		self.across.plan(org.Cartographer(left_column_index, skin.across, patch.across))
		self.down.plan(org.Cartographer(top_row_index, skin.down, patch.down))
		cursor = {}
		# Set all the widths etc.
		for col_node in self.across.tour(cursor):
			assert isinstance(col_node, org.LeafNode)
			col_margin = col_node.margin
			outline = self.toplevel.outlines[col_margin.outline_index]
			sheet.set_column(col_node.begin, col_node.begin, col_margin.width, outline)
		
		# Set all the heights etc. and plot all the data.
		for row_node in self.down.tour(cursor):
			assert isinstance(row_node, org.LeafNode)
			row_margin = row_node.margin
			outline = self.toplevel.outlines[row_margin.outline_index]
			sheet.set_row(row_node.begin, row_margin.height, outline)
			
			for col_node in self.across.tour(cursor):
				assert isinstance(col_node, org.LeafNode)
				col_margin = col_node.margin
				sheet.write(row_node.begin, col_node.begin, find_formula(), find_format())
			pass
		
		# Plot all merge cells rules. This is done literally in order of merge rules.
		# Formats on the merge cells are computed the same way as those on regular cells.
		for spec in self.definition.merge_specs:
			for row_node in self.down.tour_merge(cursor, spec.down):
				row_margin = row_node.margin
				t,b = row_node.begin, row_node.end()
				for col_node in self.across.tour_merge(cursor, spec.across):
					col_margin = col_node.margin
					l,r = col_node.begin, col_node.end()
					if t==b and l==r:
						sheet.write(t, l, spec.formula.interpret(cursor, self), find_format())
					else:
						sheet.merge_range(t, l, b, r, spec.formula.interpret(cursor, self), find_format())
		pass
	
	def data_range(self, cursor, criteria:Dict[object, static.Selector]):
		"""
		All the DATA cells where all criteria are met.
		"""
		columns = self.across.data_index(cursor, criteria)
		rows = self.down.data_index(cursor, criteria)
		if len(columns) == 0 or len(rows) == 0: return ["0"]
		return list(make_range(c, r) for c in columns for r in rows)

def make_range(col_run, row_run):
	if isinstance(col_run, int) and isinstance(row_run, int): return xl_rowcol_to_cell(row_run, col_run)
	else:
		if isinstance(col_run, int): left = right = col_run
		else: left, right = col_run
		if isinstance(row_run, int): top = bottom = row_run
		else: top, bottom = row_run
		return xl_range(top, left, bottom, right)


class Direction:
	"""
	Turns out there's a whole bunch of stuff where you have to keep the right dynamic tree with the right
	static definition. There are two of each for any given grid. Thus, rather than have a whole mess of
	correspondences where I can accidentally get it wrong, I'll embody that correspondence as a single
	unit of meaning in the form of this class.
	"""
	def __init__(self, shape:static.ShapeDefinition, env:runtime.Environment):
		self.shape = shape
		self.env = env
		self.tree = self.shape.fresh_node()
		self.space = set()
		shape.accumulate_key_space(self.space)

	def key_node(self, point):
		return self.shape.key_node(self.tree, point, self.env)
	
	def plan(self, cartographer:org.Cartographer):
		visitor = veneer.NodeVisitor({}, frozenset(), frozenset(), self.env)
		self.shape.plan_leaves(self.tree, visitor, cartographer)
	
	def tour(self, cursor:dict):
		return self.shape.tour(self.tree, cursor)

	def data_index(self, cursor, criteria:Dict[object, static.Selector]):
		entries = []
		relevant = {k:v for k,v in criteria.items() if k in self.space}
		self.shape.find_data(entries, self.tree, cursor, relevant, len(relevant))
		return collapse_runs(sorted(entries)) if entries else []
	
	def tour_merge(self, cursor, criteria:Dict[object, static.Selector]):
		return self.shape.yield_internal(self.tree, cursor, criteria, len(criteria))

def collapse_runs(entries:Iterable[int]):
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
	
