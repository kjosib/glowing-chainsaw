"""
This file describes the DYNAMIC structure of a fully instantiated object DEFINED in a `.cub` file.
There is a bit of an odd dependency loop here. To resolve it, I think it's necessary to factor out
the common data structure which is a "layout tree".

The general description can be found at .../docs/technote.md
"""

import collections
from typing import Optional, Dict, Callable
from boozetools.support import foundation
from . import static, formulae, runtime, veneer, utility


class Node:
	""" This is a dynamic layout node, but it's much more a common language for the static and dynamic parts. """

class LeafNode(Node):
	""" Seems a half-decent idea to distinguish... """
	__slots__ = ["begin", "margin", "style_class", "formula_class"]
	def __init__(self, margin:static.Marginalia):
		self.margin = margin
	def end(self): return self.begin
	def after(self): return self.begin+1

class InternalNode(Node):
	""" This can STILL be empty... """
	__slots__ = ["begin", "margin", "style_class", "formula_class", "children", "size"]
	def __init__(self, margin:static.Marginalia):
		self.margin = margin
		self.children = {}
	def end(self): return self.begin + self.size - 1
	def after(self): return self.begin + self.size


class Canvas:
	"""
	This is the actual object that collects actual data for actual plotting into an actual spreadsheet somewhere.
	It naturally refers back to its definition structure, but also to relevant per-instance data.
	
	Stylistic note: It would be entirely possible to host all functionality within the structure
	and require client code to pass in both but then client code might accidentally get it wrong...
	It's better this way I think. At least for the overall canvas object.
	"""
	def __init__(self, cub_module:static.CubModule, identifier:str, environment:runtime.Environment):
		self.cub_module = cub_module # This turns out to get consulted...
		self.definition = cub_module.canvases[identifier]
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
				styles = self.cub_module.styles
				rules = self.definition.style_rules
				bits = {}
				bits.update(styles[row_style])
				bits.update(styles[col_style])
				for i in skin.select(col_cls, row_cls):
					bits.update(styles[rules[i].payload])
				it = style_cache[fmt_key] = workbook.add_format(bits)
				return it
			pass
		
		def template(index, yon:static.Marginalia):
			if isinstance(index, int):
				them = yon.texts
				if index < len(them): return them[index]
				else: return formulae.THE_NOTHING
		
		def compete(a:Optional[static.Hint], b:Optional[static.Hint]):
			if a is None: return b
			if b is None: return a
			if b.priority > a.priority: return b
			return a
		
		def find_formula():
			"""
			Determining which hint applies is a bit more of a trick.
			First, if there's a patch defined which applies, then it takes priority.
			Otherwise, if a margin's "hint" field contains an integer, that's a
			reference to the OTHER axis's corresponding list of margin templates.
			Next, one margin.hint may supply a specific hint to use (with priority)
			"""
			cf, rf = col_margin.hint, row_margin.hint
			if 'gap' in (cf, rf): return None
			formula = check_patch()
			if formula is None: formula = template(cf, row_margin)
			if formula is None: formula = template(rf, col_margin)
			if formula is None: formula = compete(cf, rf)
			if formula is None: return self.cell_data.get((col_node, row_node), blank)
			return FormulaInterpreter(cursor, self).visit(formula)
		
		def check_patch():
			patch_key = col_node.formula_class, row_node.formula_class
			try: return formula_cache[patch_key]
			except KeyError:
				candidates = patch.select(*patch_key)
				it = formula_cache[patch_key] = candidates[-1] if candidates else None
				return it
		
		def ops(index):
			level, hidden, collapsed = self.cub_module.outlines[index]
			return {'level':level, 'hidden':hidden, 'collapsed':collapsed}
		
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
			assert isinstance(col_node, LeafNode)
			col_margin = col_node.margin
			sheet.set_column(col_node.begin, col_node.begin, col_margin.width, options=ops(col_margin.outline_index))
		
		# Set all the heights etc. and plot all the data.
		for row_node in tour.visit(self.down):
			assert isinstance(row_node, LeafNode)
			row_margin = row_node.margin
			sheet.set_row(row_node.begin, row_margin.height, options=ops(row_margin.outline_index))
			
			for col_node in tour.visit(self.across):
				assert isinstance(col_node, LeafNode)
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
	
	def data_range(self, cursor, criteria:Dict[object, formulae.Selection]):
		"""
		All the DATA cells where all criteria are met, as a list of ranges or cells (or just a zero)
		"""
		columns = self.across.data_index(cursor, criteria)
		rows = self.down.data_index(cursor, criteria)
		if rows and columns:
			return [utility.make_range(c, r) for c in columns for r in rows]
		else:
			return ["0"]

class FormulaInterpreter(foundation.Visitor):
	"""
	Not sure if this needs to be its own class or methods on Canvas,
	but this works OK for now.
	"""
	def __init__(self, cursor:dict, canvas:Canvas):
		self.cursor = cursor
		self.canvas = canvas
		self.env = canvas.environment
	
	def visit_BlankCell(self, _:formulae.BlankCell): return None
	
	def visit_Label(self, label:formulae.Label):
		return ''.join(str(self.visit(e)) for e in label.bits)
	
	def visit_LiteralText(self, literal:formulae.LiteralText):
		return literal.text
	
	def visit_PlainOrdinal(self, sub:formulae.PlainOrdinal):
		key = sub.axis
		value = self.cursor[key]
		return self.env.plain_text(key, value)

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
		self.tree = node_factory.visit(self.shape)
		self.space = set()
		shape.accumulate_key_space(self.space)

	def plan(self, cartographer:"Cartographer"):
		state = veneer.PlanState({}, frozenset(), frozenset(), self.env)
		cartographer.visit(self.shape, self.tree, state)
	
	def data_index(self, cursor, criteria:Dict[object, formulae.Selection]):
		fd = FindData(cursor, {k:v for k,v in criteria.items() if k in self.space})
		fd.visit(self.shape, self.tree, len(fd.criteria))
		return utility.collapse_runs(sorted(fd.found))
	
	def tour_merge(self, cursor, criteria:Dict[str, formulae.Selection]):
		return InternalTour(cursor, criteria).visit(self.shape, self.tree, len(criteria))

class FindKeyNode(foundation.Visitor):
	""" Go find the appropriate sub-node for a given point, principally for entering magnitude/attribute data. """
	
	def __init__(self, point: dict, env:runtime.Environment):
		self.point = point
		self.env = env
	
	def visit_Direction(self, direction: Direction):
		return self.visit(direction.shape, direction.tree)
	
	def visit_LeafDefinition(self, shape:static.LeafDefinition, node:LeafNode) -> LeafNode:
		return node
	
	def visit_TreeDefinition(self, shape:static.TreeDefinition, node:InternalNode) -> LeafNode:
		ordinal = self.visit(shape.reader)
		try: branch = node.children[ordinal]
		except KeyError: branch = node.children[ordinal] = node_factory.visit(shape.within)
		return self.visit(shape.within, branch)
	
	def visit_FrameDefinition(self, shape:static.FrameDefinition, node:InternalNode) -> LeafNode:
		ordinal = self.visit(shape.reader)
		try: branch = node.children[ordinal]
		except KeyError: raise runtime.InvalidOrdinalError(shape.cursor_key, ordinal)
		else: return self.visit(shape.fields[ordinal], branch)
	
	def visit_MenuDefinition(self, shape:static.MenuDefinition, node:InternalNode) -> LeafNode:
		ordinal = self.visit(shape.reader)
		try: within = shape.fields[ordinal]
		except KeyError: raise runtime.InvalidOrdinalError(shape.cursor_key, ordinal)
		else:
			try: branch = node.children[ordinal]
			except KeyError: branch = node.children[ordinal] = node_factory.visit(within)
			return self.visit(within, branch)
	
	def visit_SimpleReader(self, r:static.SimpleReader):
		return self.point[r.key]
	
	def visit_ComputedReader(self, r:static.ComputedReader):
		return self.env.read_magic(r.key, self.point)  # Method is up to the environment.
	
	def visit_DefaultReader(self, r:static.DefaultReader):
		return self.point.get(r.key, '_')  # Absent key becomes '_'; for cosmetic frames.

class FindData(foundation.Visitor):
	""" Accumulate a list of matching (usually data) leaf indexes based on criteria. """
	
	def __init__(self, context: dict, criteria: Dict[object, formulae.Selection]):
		self.context = context
		self.criteria = criteria
		self.found = []
	
	def visit_LeafDefinition(self, shape:static.LeafDefinition, node:LeafNode, remain:int):
		if remain == 0:
			self.found.append(node.begin)
	
	def visit_TreeDefinition(self, shape:static.TreeDefinition, node:InternalNode, remain:int):
		if self.common(shape.cursor_key, lambda o:shape.within, node, remain):
			for child in node.children.values():
				self.visit(shape.within, child, remain)

	def visit_FrameDefinition(self, shape:static.FrameDefinition, node:InternalNode, remain:int):
		if self.common(shape.cursor_key, shape.fields.__getitem__, node, remain):
			if '_' in shape.fields:
				self.visit(shape.fields['_'], node.children['_'], remain)
			else:
				raise runtime.AbsentKeyError(shape.cursor_key)
		
	def visit_MenuDefinition(self, shape:static.MenuDefinition, node:InternalNode, remain:int):
		if self.common(shape.cursor_key, shape.fields.__getitem__, node, remain):
			for ordinal, child in node.children.items():
				self.visit(shape.fields[ordinal], child, remain)

	def common(self, key:str, down:Callable[[str], static.ShapeDefinition], node:InternalNode, remain:int) -> bool:
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
	
class LeafTour(foundation.Visitor):
	""" Walk a tree while keeping a cursor up to date; yield the leaf nodes. """
	
	def __init__(self, cursor:dict):
		self.cursor = cursor
	
	def visit_LeafDefinition(self, shape:static.LeafDefinition, node:LeafNode):
		yield node
	
	def visit_CompoundShapeDefinition(self, shape:static.CompoundShapeDefinition, node:InternalNode):
		for label, child_node in node.children.items():
			self.cursor[shape.cursor_key] = label
			yield from self.visit(shape.descend(label), child_node)
			del self.cursor[shape.cursor_key]
	
	def visit_Direction(self, direction:Direction):
		return self.visit(direction.shape, direction.tree)

class InternalTour(foundation.Visitor):
	"""
	Yield matching (internal, if possible) nodes.
	This is useful for merges, for outline specifications,
	and possibly for various other activities.
	"""
	
	def __init__(self, cursor: dict, criteria:Dict[str, formulae.Selection]):
		self.cursor = cursor
		self.criteria = criteria
	
	def visit_LeafDefinition(self, shape:static.LeafDefinition, node:LeafNode, remain:int):
		if remain == 0: yield node
	
	def visit_CompoundShapeDefinition(self, shape:static.CompoundShapeDefinition, node:InternalNode, remain:int):
		if remain == 0: yield node
		else:
			if shape.cursor_key in self.criteria:
				items = self.criteria[shape.cursor_key].choose_children(node.children)
				remain -= 1
			else:
				items = node.children.items()
			for ordinal, child in items:
				self.cursor[shape.cursor_key] = ordinal
				yield from self.visit(shape.descend(ordinal), child, remain)
				del self.cursor[shape.cursor_key]
		
class Cartographer(foundation.Visitor):
	"""
	Contribute to the preparation of a properly-ordered list of leaf nodes.
	Seems to also be responsible for determining formats and formulas,
	collaborating with PlanState
	"""
	def __init__(self, begin:int, skin:veneer.PartialClassifier, patch:veneer.PartialClassifier):
		self.index = begin
		self.skin = skin
		self.patch = patch
	
	def enter_node(self, node:Node, state:veneer.PlanState):
		node.begin = self.index
		node.style_class = self.skin.classify(state)
		node.formula_class = self.patch.classify(state)
	
	def leave_node(self, node:InternalNode):
		node.size = self.index - node.begin
	
	def visit_LeafDefinition(self, shape: static.LeafDefinition, node: LeafNode, state:veneer.PlanState):
		self.enter_node(node, state)
		self.index += 1

	def _compound(self, shape:static.CompoundShapeDefinition, node:InternalNode, state:veneer.PlanState, schedule):
		def enter(label, is_first, is_last):
			prime = state.prime(shape.cursor_key, label, is_first, is_last)
			self.visit(shape.descend(label), node.children[label], prime)
		
		# Begin:
		self.enter_node(node, state)
		# schedule = shape._schedule(node.children.keys(), state.environment)
		if len(schedule) == 1:
			# The only element is also the first and last element.
			enter(schedule[0], True, True)
		elif schedule:
			# There's a first, a possibly-empty middle, and a last element.
			enter(schedule[0], True, False)
			for i in range(1, len(schedule) - 1): enter(schedule[i], False, False)
			enter(schedule[-1], False, True)
		self.leave_node(node)
	
	def visit_TreeDefinition(self, shape: static.TreeDefinition, node: InternalNode, state: veneer.PlanState):
		schedule = sorted(node.children.keys(), key=state.environment.collation(shape.cursor_key))
		return self._compound(shape, node, state, schedule)
	
	def visit_FrameDefinition(self, shape:static.FrameDefinition, node:InternalNode, state:veneer.PlanState):
		schedule = shape.sequence
		return self._compound(shape, node, state, schedule)
		
	def visit_MenuDefinition(self, shape:static.MenuDefinition, node:InternalNode, state:veneer.PlanState):
		schedule = [k for k in shape.fields if k in node.children]
		return self._compound(shape, node, state, schedule)
		

class FreshNodeFactory(foundation.Visitor):
	"""
	Return a fresh Node subclass object according to whatever
	sort of shape definition we hand it.
	
	This is both visitor and singleton, because it has no particular state.
	However, it's simpler to just reuse the visitor class rather than
	build an overt `MonkeyPatch` class...
	"""
	
	def visit_LeafDefinition(self, shape:static.LeafDefinition):
		return LeafNode(shape.margin)
	
	def visit_CompoundShapeDefinition(self, shape:static.CompoundShapeDefinition):
		return InternalNode(shape.margin)
	
	def visit_FrameDefinition(self, shape:static.FrameDefinition):
		node = InternalNode(shape.margin)
		for label, child in shape.fields.items():
			node.children[label] = self.visit(child)
		return node

node_factory = FreshNodeFactory()
