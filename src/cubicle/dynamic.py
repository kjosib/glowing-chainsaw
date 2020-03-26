"""
This file describes the DYNAMIC structure of a fully instantiated object DEFINED in a `.cub` file.
There is a bit of an odd dependency loop here. To resolve it, I think it's necessary to factor out
the common data structure which is a "layout tree".

The general description can be found at .../docs/technote.md
"""

import collections
from typing import Optional, Dict, List, Callable
from canon import utility, errors
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
		fkn = FindKeyNode(point, self.environment)
		return fkn.visit(self.across), fkn.visit(self.down)
	
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
		
		def ops(index):
			level, hidden, collapse = self.toplevel.outlines[index]
			return {'level':level, 'hidden':hidden, 'collapse':collapse}
		
		style_cache = {}
		formula_cache = {}
		skin = veneer.CrossClassifier(self.definition.style_rules, self.across.space, self.down.space)
		patch = veneer.CrossClassifier(self.definition.formula_rules, self.across.space, self.down.space)
		self.across.plan(Cartographer(left_column_index, skin.across, patch.across))
		self.down.plan(Cartographer(top_row_index, skin.down, patch.down))
		cursor = {}
		tour = LeafTour(cursor)
		# Set all the widths etc.
		for col_node in tour.visit(self.across):
			assert isinstance(col_node, org.LeafNode)
			col_margin = col_node.margin
			sheet.set_column(col_node.begin, col_node.begin, col_margin.width, options=ops(col_margin.outline_index))
		
		# Set all the heights etc. and plot all the data.
		for row_node in tour.visit(self.down):
			assert isinstance(row_node, org.LeafNode)
			row_margin = row_node.margin
			sheet.set_row(row_node.begin, row_margin.height, options=ops(row_margin.outline_index))
			
			for col_node in tour.visit(self.across):
				assert isinstance(col_node, org.LeafNode)
				col_margin = col_node.margin
				sheet.write(row_node.begin, col_node.begin, find_formula(), find_format())
			pass
		
		# Plot all merge cells rules. This is done literally in order of merge rules.
		# Formats on the merge cells are computed the same way as those on regular cells.
		for spec in self.definition.merge_specs:
			for row_node in self.down.tour_merge(cursor, spec.down):
				row_margin = row_node.margin
				top,bottom = row_node.begin, row_node.end()
				for col_node in self.across.tour_merge(cursor, spec.across):
					col_margin = col_node.margin
					left,right = col_node.begin, col_node.end()
					if top==bottom and left==right:
						sheet.write(top, left, spec.formula.interpret(cursor, self), find_format())
					else:
						sheet.merge_range(top, left, bottom, right, spec.formula.interpret(cursor, self), find_format())
		pass
	
	def data_range(self, cursor, criteria:Dict[object, static.Selector]):
		"""
		All the DATA cells where all criteria are met, as a list of ranges or cells (or just a zero)
		"""
		columns = self.across.data_index(cursor, criteria)
		rows = self.down.data_index(cursor, criteria)
		if rows and columns:
			return [utility.make_range(c, r) for c in columns for r in rows]
		else:
			return ["0"]

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

	def plan(self, cartographer:"Cartographer"):
		state = veneer.PlanState({}, frozenset(), frozenset(), self.env)
		cartographer.visit(self.shape, self.tree, state)
	
	def data_index(self, cursor, criteria:Dict[object, static.Selector]):
		fd = FindData(cursor, {k:v for k,v in criteria.items() if k in self.space})
		fd.visit(self.shape, self.tree, len(fd.criteria))
		return utility.collapse_runs(sorted(fd.found))
	
	def tour_merge(self, cursor, criteria:Dict[str, static.Selector]):
		return InternalTour(cursor, criteria).visit(self.shape, self.tree, len(criteria))


class FindKeyNode(utility.Visitor):
	""" Go find the appropriate sub-node for a given point, principally for entering magnitude/attribute data. """
	
	def __init__(self, point: dict, env:runtime.Environment):
		self.point = point
		self.env = env
	
	def visit_Direction(self, direction: Direction):
		return self.visit(direction.shape, direction.tree)
	
	def visit_LeafDefinition(self, shape:static.LeafDefinition, node:org.LeafNode) -> org.LeafNode:
		return node
	
	def visit_TreeDefinition(self, shape:static.TreeDefinition, node:org.InternalNode) -> org.LeafNode:
		ordinal = shape.reader.read(self.point, self.env)
		try: branch = node.children[ordinal]
		except KeyError: branch = node.children[ordinal] = shape.within.fresh_node()
		return self.visit(shape.within, branch)
	
	def visit_FrameDefinition(self, shape:static.FrameDefinition, node:org.InternalNode) -> org.LeafNode:
		ordinal = shape.reader.read(self.point, self.env)
		try: branch = node.children[ordinal]
		except KeyError: raise errors.InvalidOrdinalError(shape.cursor_key, ordinal)
		else: return self.visit(shape.fields[ordinal], branch)


	def visit_MenuDefinition(self, shape:static.MenuDefinition, node:org.InternalNode) -> org.LeafNode:
		ordinal = shape.reader.read(self.point, self.env)
		try: within = shape.fields[ordinal]
		except KeyError: raise errors.InvalidOrdinalError(shape.cursor_key, ordinal)
		else:
			try: branch = node.children[ordinal]
			except KeyError: branch = node.children[ordinal] = within.fresh_node()
			return self.visit(within, branch)

class FindData(utility.Visitor):
	""" Accumulate a list of matching (usually data) leaf indexes based on criteria. """
	
	def __init__(self, context: dict, criteria: Dict[object, static.Selector]):
		self.context = context
		self.criteria = criteria
		self.found = []
	
	def visit_LeafDefinition(self, shape:static.LeafDefinition, node:org.LeafNode, remain:int):
		if remain == 0:
			self.found.append(node.begin)
	
	def visit_TreeDefinition(self, shape:static.TreeDefinition, node:org.InternalNode, remain:int):
		if self.common(shape.cursor_key, lambda o:shape.within, node, remain):
			for child in node.children.values():
				self.visit(shape.within, child, remain)

	def visit_FrameDefinition(self, shape:static.FrameDefinition, node:org.InternalNode, remain:int):
		if self.common(shape.cursor_key, shape.fields.__getitem__, node, remain):
			if '_' in shape.fields:
				self.visit(shape.fields['_'], node.children['_'], remain)
			else:
				raise errors.AbsentKeyError(shape.cursor_key)
		
	def visit_MenuDefinition(self, shape:static.MenuDefinition, node:org.InternalNode, remain:int):
		if self.common(shape.cursor_key, shape.fields.__getitem__, node, remain):
			for ordinal, child in node.children.items():
				self.visit(shape.fields[ordinal], child, remain)

	def common(self, key:str, down:Callable[[str], static.ShapeDefinition], node:org.InternalNode, remain:int) -> bool:
		""" Commonalities among composite-type shapes; returns True if can't help. """
		if key in self.criteria:
			remain -= 1
			for ordinal, child in self.criteria[key].choose_children(node.children):
				self.visit(down(ordinal), child, remain)
		elif key in self.context:
			ordinal = self.context[key]
			child = node.children[ordinal]
			self.visit(down(ordinal), child, remain)
		else: return True
	
class LeafTour(utility.Visitor):
	""" Walk a tree while keeping a cursor up to date; yield the leaf nodes. """
	
	def __init__(self, cursor:dict):
		self.cursor = cursor
	
	def visit_LeafDefinition(self, shape:static.LeafDefinition, node:org.LeafNode):
		yield node
	
	def visit_CompoundShapeDefinition(self, shape:static.CompoundShapeDefinition, node:org.InternalNode):
		for label, child_node in node.children.items():
			self.cursor[shape.cursor_key] = label
			yield from self.visit(shape._descent(label), child_node)
			del self.cursor[shape.cursor_key]
	
	def visit_Direction(self, direction:Direction):
		return self.visit(direction.shape, direction.tree)

class InternalTour(utility.Visitor):
	"""
	Yield matching (internal, if possible) nodes.
	This is useful for merges, for outline specifications,
	and possibly for various other activities.
	"""
	
	def __init__(self, cursor: dict, criteria:Dict[str, static.Selector]):
		self.cursor = cursor
		self.criteria = criteria
	
	def visit_LeafDefinition(self, shape:static.LeafDefinition, node:org.LeafNode, remain:int):
		if remain == 0: yield node
	
	def visit_CompoundShapeDefinition(self, shape:static.CompoundShapeDefinition, node:org.InternalNode, remain:int):
		if remain == 0: yield node
		else:
			if shape.cursor_key in self.criteria:
				items = self.criteria[shape.cursor_key].choose_children(node.children)
				remain -= 1
			else:
				items = node.children.items()
			for ordinal, child in items:
				self.cursor[shape.cursor_key] = ordinal
				yield from self.visit(shape._descent(ordinal), child, remain)
				del self.cursor[shape.cursor_key]
		
	

class Cartographer(utility.Visitor):
	"""
	Contribute to the preparation of a properly-ordered list of leaf nodes.
	Seems to also be responsible for determining formats and formulas,
	collaborating with PlanState
	"""
	def __init__(self, begin:int, skin:veneer.PartialClassifier, patch:veneer.PartialClassifier):
		self.index = begin
		self.skin = skin
		self.patch = patch
	
	def enter_node(self, node:org.Node, state:veneer.PlanState):
		node.begin = self.index
		node.style_class = self.skin.classify(state)
		node.formula_class = self.patch.classify(state)
	
	def leave_node(self, node:org.InternalNode):
		node.size = self.index - node.begin
	
	def visit_LeafDefinition(self, shape: static.LeafDefinition, node: org.LeafNode, state:veneer.PlanState):
		self.enter_node(node, state)
		self.index += 1

	def visit_CompoundShapeDefinition(self, shape:static.CompoundShapeDefinition, node:org.InternalNode, state:veneer.PlanState):
		def enter(label, is_first, is_last):
			prime = state.prime(shape.cursor_key, label, is_first, is_last)
			self.visit(shape._descent(label), node.children[label], prime)
		
		# Begin:
		self.enter_node(node, state)
		schedule = shape._schedule(node.children.keys(), state.environment)
		if len(schedule) == 1:
			# The only element is also the first and last element.
			enter(schedule[0], True, True)
		elif schedule:
			# There's a first, a possibly-empty middle, and a last element.
			enter(schedule[0], True, False)
			for i in range(1, len(schedule) - 1): enter(schedule[i], False, False)
			enter(schedule[-1], False, True)
		self.leave_node(node)



