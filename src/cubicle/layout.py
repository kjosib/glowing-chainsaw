"""
Stuff relating to layout structure.

The AST nodes for layout are mostly in the AST module. This one here does the semantic
transformation to populate the symbol table and participate in actually laying things out.
"""

from typing import NamedTuple, List, Optional, Dict, Type, Union
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
	
	def emulate(self, other:"Style"):
		self.fmt.update(other.fmt)
		self.head_fmt.update(other.head_fmt)
		self.outline.update(other.outline)
		if self.hint is None: self.hint = other.hint
	
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
	
	def clone(self) -> "Style":
		other = Style()
		other.emulate(self)
		return other

class Layout:
	""" ABC for (runtime) layout definition nodes """
	def as_scope(self) -> symbols.Scope: raise NotImplementedError(type(self))
	def as_style(self) -> Style: raise NotImplementedError(type(self))
	def clone(self) -> "Layout": raise NotImplementedError(type(self))

class Leaf(Layout):
	def __init__(self, is_head:bool, template:list, style:Style):
		self.is_head = is_head
		self.template = template
		self.style = style
	def as_scope(self) -> symbols.Scope: raise KeyError()
	def as_style(self) -> Style: return self.style
	def clone(self) -> "Layout": return Leaf(self.is_head, self.template, self.style.clone())

class Frame(Layout):
	def __init__(self, axis:streams.AxisReader, scope:symbols.Scope, schedule:List[tuple], style:Style, shy:bool):
		self.axis = axis
		self.scope = scope
		self.schedule = schedule
		self.style = style
		self.shy = shy # Remember W's ladder: I may see something coming, but YAGNI (yet).
	def as_scope(self): return self.scope
	def as_style(self) -> Style: return self.style
	def clone(self) -> "Layout": return Frame(self.axis, self.scope, self.schedule, self.style.clone(), self.shy)

class Tree(Layout):
	def __init__(self, axis:streams.AxisReader, child:Layout):
		self.axis = axis
		self.child = child
	def as_scope(self): return self.child.as_scope()
	def as_style(self) -> Style: return self.child.as_style()
	def clone(self) -> "Layout": return Tree(self.axis, self.child.clone())


class Canvas:
	def __init__(self, down, across):
		pass
