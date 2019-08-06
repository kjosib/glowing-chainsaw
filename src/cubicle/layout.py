"""
Stuff relating to layout structure.

The AST nodes for layout are mostly in the AST module. This one here does the semantic
transformation to populate the symbol table and participate in actually laying things out.
"""

import functools
from typing import List, Optional, Dict

from . import symbols, streams, AST

GAP = object() # A special-case hint?

FORMAT_PROPERTIES = {
	'font_name': str,
	'font_size': int,
	'font_color': str,
	'bold': bool,
	'italic': bool,
	'underline': int, # 1=single, 2=double, 33=single-accounting, 34=double-accounting
	'font_strikeout': bool,
	'font_script': int, # 1=Superscript, 2=Subscript -- but these are unlikely.
	'num_format': (int, str),
	'locked': bool,
	'hidden': bool,
	'align': str,
	'valign': str,
	'rotation': int,
	'text_wrap': bool,
	'reading_order': int, # 1=left-to-right, like English. 2=right-to-left, like Arabic.
	'text_justlast': bool,
	# 'center_across': # use .align=center_across instead.
	'indent': int,
	'shrink': bool,
	'pattern': int, # 0-18, with 1 being a solid fill of the background color.
	'bg_color': str,
	'fg_color': str,
	'border': int,
	'bottom': int,
	'top': int,
	'left': int,
	'right': int,
	'border_color': str,
	'bottom_color': str,
	'top_color': str,
	'left_color': str,
	'right_color': str,
}

OUTLINE_PROPERTIES = {
	'height': (int, float),
	'width': (int, float),
	'level': int,
	'hidden': bool,
	'collapsed': bool,
}

class Node:
	""" These collectively describe concrete layout trees. """
	sub:Optional[Dict[object, "Node"]]
	first:Optional[int]
	size:Optional[int] # Zero means -- empty tree, basically.
	__slots__ = ["sub", "first", "size", "style_key"]
	def __init__(self, sub):
		self.sub = sub

class Style:
	ATTRIBUTE_MAP = {
		'.':('fmt',FORMAT_PROPERTIES),
		'!':('head_fmt',FORMAT_PROPERTIES),
		'&':('outline',OUTLINE_PROPERTIES),
	}
	SPECIAL_CASE = {
		'border' : ['top', 'left', 'bottom', 'right'],
		'border_color' : ['top_color', 'left_color', 'bottom_color', 'right_color'],
	}
	
	def __init__(self):
		self.fmt = {}
		self.head_fmt = {}
		self.outline = {}
		self.hint = None # or a pair.
	
	def __bool__(self): return any((self.fmt, self.head_fmt, self.outline, self.hint))
	
	def emulate(self, other:"Style"):
		self.fmt.update(other.fmt)
		self.head_fmt.update(other.head_fmt)
		self.outline.update(other.outline)
		self.hint = other.hint or self.hint
	
	def assign(self, a:AST.Assignment):
		kind = a.property.kind
		name = a.property.ident.name
		value = a.value
		if isinstance(value, symbols.Identifier): value = value.name
		try: attr, cls = Style.ATTRIBUTE_MAP[kind]
		except KeyError: raise symbols.UndefinedNameError(a.property.ident)
		if not isinstance(value, cls[name]): raise symbols.TypeClashError(a.property.ident)
		target = getattr(self, attr)
		if name in Style.SPECIAL_CASE:
			for xkey in Style.SPECIAL_CASE[name]:
				target[xkey] = value
		else: target[name] = value
	
	def declare(self, context: symbols.Scope, items: list):
		for x in items:
			if isinstance(x, AST.Assignment): self.assign(x)
			elif isinstance(x, (symbols.Identifier, symbols.Qualident)):
				source = context.find_reference(x)
				if isinstance(source, Style): self.emulate(source)
				else: raise symbols.TypeClashError(x)
	
THE_NULL_STYLE = Style()

@functools.lru_cache()
def combine_style(a:Style, b:Style) -> Style:
	# This is a pure function once the styles are defined, so take full advantage of memoization.
	assert isinstance(a, Style), type(a)
	assert isinstance(b, Style), type(b)
	if a and b:
		answer = Style()
		answer.emulate(a)
		answer.emulate(b)
		return answer
	else: return a or b
	

class Layout:
	""" ABC for (runtime) layout definition nodes """
	def as_scope(self) -> symbols.Scope: raise NotImplementedError(type(self))
	def as_style(self) -> Style: raise NotImplementedError(type(self))
	def clone(self, style:Style) -> "Layout": raise NotImplementedError(type(self))
	def vivify(self) -> Node:
		""" produce a minimal set of nodes for a (sub)layout """
		raise NotImplementedError(type(self))
	def key_node(self, tree:Node, point:dict) -> Node:
		""" find the leaf node corresponding to a data point. """
		raise NotImplementedError(type(self))
	def arrange(self, tree:Node, first:int, ):
		""" afterwards tree nodes have "first", "size", and "style_key" set accordingly. """
		raise NotImplementedError(type(self))
	def enum_leaf_hint(self, tree:Node, cursor:dict, style:Style):
		""" Yield <node, Leaf, style> triples in no guaranteed order while the cursor is updated during the yield. """
		# Note that the style combinator is a pure function by the time this is called...
		raise NotImplementedError(type(self))

class Leaf(Layout):
	def __init__(self, is_head:bool, template:list, style:Style):
		self.is_head = is_head
		self.template = template
		self.style = style
	def as_scope(self) -> symbols.Scope: raise KeyError()
	def clone(self, style:Style) -> "Layout": return Leaf(self.is_head, self.template, combine_style(self.style, style))
	def vivify(self) -> Node: return Node(None)
	def key_node(self, tree:Node, point:dict) -> Node: return tree
	def arrange(self, tree:Node, first:int):
		tree.first, tree.size = first, 1
	def enum_leaf_hint(self, tree:Node, cursor:dict, style:Style):
		yield tree, self, combine_style(style, self.style)

class BaseFrame(Layout):
	def __init__(self, scope:symbols.Scope, schedule:List[tuple], style:Style):
		self.scope = scope
		self.schedule = schedule
		self.style = style
	def as_scope(self): return self.scope
	def as_style(self) -> Style: return self.style
	def arrange(self, tree:Node, first:int):
		tree.first = first
		sub = tree.sub
		for label, child_layout in self.schedule:
			if label in sub:
				child_tree = sub[label]
				child_layout.arrange(child_tree, first)
				first += child_tree.size
		tree.size = first - tree.first

class StaticFrame(BaseFrame):
	def clone(self, style:Style) -> "Layout": return StaticFrame(self.scope, self.schedule, combine_style(self.style, style))
	def vivify(self) -> Node: return Node({name:child.vivify() for name,child in self.schedule})
	def key_node(self, tree: Node, point: dict) -> Node:
		label = "_"
		try: child_layout = self.scope.bindings[label].value
		except KeyError: raise streams.InvalidOrdinalError(None, label)
		return child_layout.key_node(tree.sub[label], point)
	def enum_leaf_hint(self, tree:Node, cursor:dict, style:Style):
		assert self not in cursor
		for label, child_layout in self.schedule:
			cursor[self] = label
			yield from child_layout.enum_leaf_hint(tree.sub[label], cursor, combine_style(style, self.style))
		del cursor[self]

class DynamicFrame(BaseFrame):
	def __init__(self, axis:streams.Axis, scope:symbols.Scope, schedule:List[tuple], style:Style, shy:bool):
		super().__init__(scope, schedule, style)
		self.axis = axis
		self.shy = shy # Remember W's ladder: I may see something coming, but YAGNI (yet).
	def clone(self, style:Style) -> "Layout": return DynamicFrame(self.axis, self.scope, self.schedule, combine_style(self.style, style), self.shy)
	def vivify(self) -> Node:
		if self.shy: sub = {}
		else: sub = {name:b.value.vivify() for name,b in self.scope.bindings.items()}
		return Node(sub)
	def key_node(self, tree:Node, point:dict):
		label = self.axis.ordinal_from(point)
		try: child_layout = self.scope.bindings[label].value
		except KeyError: self.axis.report_bad_ordinal(label)
		else:
			sub = tree.sub
			try: child = sub[label]
			except KeyError: child = sub[label] = child_layout.vivify()
			return child_layout.key_node(child, point)
	

class Tree(Layout):
	def __init__(self, axis:streams.Axis, child:Layout):
		self.axis = axis
		self.child_layout = child
	def as_scope(self): return self.child_layout.as_scope()
	def clone(self, style:Style) -> "Layout": return Tree(self.axis, self.child_layout.clone(style))
	def vivify(self) -> Node: return Node({})
	def key_node(self, tree: Node, point: dict) -> Node:
		label = self.axis.ordinal_from(point)
		child_layout = self.child_layout
		sub = tree.sub
		try: child = sub[label]
		except KeyError: child = sub[label] = child_layout.vivify()
		return child_layout.key_node(child, point)
	def arrange(self, tree:Node, first:int):
		tree.first = first
		sub = tree.sub
		# for label in self.axis.sorted(sub.keys()):
		for label in sorted(sub.keys()):
			self.child_layout.arrange(sub[label], first)
			first += sub[label].size
		tree.size = first - tree.first
	def enum_leaf_hint(self, tree:Node, cursor:dict, style:Style):
		key = self.axis.key()
		assert key not in cursor
		for label, subtree in tree.sub.items():
			cursor[key] = label
			yield from self.child_layout.enum_leaf_hint(subtree, cursor, style)
		del cursor[key]

class Canvas:
	def __init__(self, down: Layout, across: Layout, style):
		self.down = down
		self.across = across
		self.style = style
		self.row_tree = self.down.vivify()
		self.col_tree = self.across.vivify()
		self.detail = {}
	def key(self, point:dict):
		row = self.down.key_node(self.row_tree, point)
		col = self.across.key_node(self.col_tree, point)
		return row, col
	def poke(self, point:dict, value): self.detail[self.key(point)] = value
	def incr(self, point:dict, value):
		if value:
			key = self.key(point)
			self.detail[key] = self.detail.get(key,0) + value
	def plot(self, workbook, sheet, top:int, left:int):
		
		@functools.lru_cache()
		def mk_format(row_style:Style, col_style:Style, row_is_head:bool, col_is_head:bool):
			fmt = dict(row_style.fmt)
			fmt.update(col_style.fmt)
			if row_is_head: fmt.update(col_style.head_fmt)
			if col_is_head: fmt.update(row_style.head_fmt)
			return workbook.add_format(fmt)
		
		self.down.arrange(self.row_tree, top)
		self.across.arrange(self.col_tree, left)
		
		cursor = {}
		
		for col_node, col_leaf, col_style in self.across.enum_leaf_hint(self.col_tree, cursor, THE_NULL_STYLE):
			col = col_node.first
			if col_style.outline:
				sheet.set_column(col, col, col_style.outline.get('width'), options=col_style.outline)
			sheet.write_comment(0, col, str({k:v for k,v in cursor.items() if isinstance(k,str)}))
			
		for row_node, row_leaf, row_style in self.down.enum_leaf_hint(self.row_tree, cursor, THE_NULL_STYLE):
			assert isinstance(row_leaf, Leaf)
			row = row_node.first
			if row_style.outline:
				sheet.set_row(row, row_style.outline.get('height'), options=row_style.outline)
			for col_node, col_leaf, col_style in self.across.enum_leaf_hint(self.col_tree, cursor, THE_NULL_STYLE):
				col = col_node.first
				key = row_node, col_node
				try: item = self.detail[key]
				except KeyError:
					rh, ch = row_style.hint, col_style.hint
					if GAP in (rh, ch) or (rh is None and ch is None): item = None
					elif rh and ch:
						item = "(Both/Choose)"
					elif ch:
						"Don't know yet. One thing at a time."
						hint, prio = ch
						assert isinstance(hint, AST.FunctionCall)
						if hint.stem.name == 'head':
							item = template_substitute(row_leaf, cursor)
						else:
							item = hint.stem.name
					elif rh:
						""" Probably this part gets turned into some kind of pre-built callable later on. """
						hint, prio = rh
						assert isinstance(hint, AST.FunctionCall)
						if hint.stem.name == 'head':
							item = template_substitute(col_leaf, cursor)
						else:
							item = hint.stem.name
						
				sheet.write(row, col, item, mk_format(row_style, col_style, row_leaf.is_head, col_leaf.is_head))
				# sheet.write_comment(row, col, str({k:v for k,v in cursor.items() if isinstance(k,str)}))

def template_substitute(leaf:Leaf, cursor:dict) -> str:
	def munge(elt) -> str:
		if isinstance(elt, str): return elt
		elif isinstance(elt, AST.Replacement):
			try: value = cursor[elt.axis.name]
			except KeyError: raise symbols.UndefinedNameError(elt.axis)
			if elt.view is not None: raise NotImplementedError("Not yet, anyway.")
			return str(value)
	return ''.join(map(munge, leaf.template))