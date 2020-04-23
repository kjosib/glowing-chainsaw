import collections
from typing import Dict, NamedTuple
from boozetools.support import runtime as brt
from boozetools.support.interfaces import Scanner
from . import AST
from canon import utility, lexical

TABLES = utility.tables(__file__, 'core.md')

class CoreDriver(brt.TypicalApplication, lexical.LexicalAnalyzer):
	
	def scan_token(self, yy:Scanner, kind):
		# Concrete tokens that won't contribute to the AST
		yy.token(kind, yy.matched_text())
	
	def scan_name(self, yy:Scanner, kind):
		# sort of like an identifier: We need to capture the span in case of semantic error.
		yy.token(kind, AST.Name(yy.matched_text(), yy.current_span()))
	
	def scan_string(self, yy:Scanner, kind):
		# Pick up the token as a constant of string type, not an identifier.
		# Like a bareword in ancient perl?
		yy.token(kind, AST.Constant(yy.matched_text(), yy.current_span(), kind))
	
	def scan_sigil(self, yy:Scanner, kind:str):
		# Like scan_string but removes the first char from the semantic value.
		yy.token(kind, AST.Constant(yy.matched_text()[1:], yy.current_span(), kind))
	
	def scan_integer(self, yy:Scanner):
		yy.token('INTEGER', AST.Constant(int(yy.matched_text()), yy.current_span(), 'INT'))
	
	def scan_hex_integer(self, yy:Scanner):
		yy.token('INTEGER', AST.Constant(int(yy.matched_text()[1:], 16), yy.current_span(), 'HEX'))
	
	def scan_decimal(self, yy:Scanner):
		yy.token('DECIMAL', AST.Constant(float(yy.matched_text()), yy.current_span(), 'DEC'))

	def scan_delimited(self, yy:Scanner, kind):
		yy.token(kind, AST.Constant(yy.matched_text()[1:-1], yy.current_span(), 'STRING'))

	def __init__(self):
		self.errors=0
		super().__init__(TABLES)
	
	def unexpected_token(self, kind, semantic, pds):
		self.errors += 1
		print("in scan state:", self.yy.current_condition())
		breadcrumbs = TABLES['parser']['breadcrumbs']
		t = TABLES['parser']['terminals']
		nt = TABLES['parser']['nonterminals']
		def bc(q):
			x = breadcrumbs[q]
			if x < len(t): return t[x]
			else: return nt[x-len(t)]
		stack_symbols = list(map(bc, list(pds.path_from_root())[1:]))
		print("Parse Stack:", *stack_symbols)
		super().unexpected_token(kind, semantic, pds)
	
	def parse_none(self): return None
	def parse_empty(self): return []
	def parse_singleton(self, item): return [item]
	def parse_append(self, them, item):
		them.append(item)
		return them
	
	def parse_define_style(self, name:AST.Name, elts:list):
		assert isinstance(name, AST.Name), type(name)
		return AST.StyleDef(name, elts)
	
	def parse_marginalia(self, texts, hint, appearance):
		return AST.Marginalia(texts, hint, appearance)
	
	def parse_field(self, name, shape):
		assert isinstance(name, AST.Name), type(name)
		assert isinstance(shape, (AST.Marginalia, AST.Name, AST.Frame, AST.Menu, AST.Tree)), type(shape)
		return AST.Field(name, shape)
	
	def parse_frame(self, margin, key, fields):
		return AST.Frame(margin, key, fields)
	
	def parse_menu(self, margin, key, fields):
		return AST.Menu(margin, key, fields)
	
	def parse_tree(self, margin, key, within):
		return AST.Tree(margin, key, within)
	
	def parse_assignment(self, name, value):
		assert isinstance(name, AST.Name)
		if isinstance(value, AST.Name): value = AST.Constant(*value, 'STRING')
		assert isinstance(value, AST.Constant)
		return AST.Assign(name, value)
	
	def parse_define_canvas(self, name:AST.Name, across:AST.Name, down:AST.Name, items:list):
		return AST.Canvas(name, across, down, items)
	
