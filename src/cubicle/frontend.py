from typing import List, Tuple
from boozetools.support import runtime as brt
from boozetools.support.interfaces import Scanner
from . import AST, formulae, utility

TABLES = utility.tables(__file__, 'core.md')

class CoreDriver(brt.TypicalApplication):
	VALID_KEYWORDS = frozenset('AXIS CANVAS FRAME GAP HEAD LEAF MENU MERGE STYLE TREE USE ZONE'.split())
	
	def default_scan_action(self, message, scanner, param):
		# Just in case I forgot something:
		raise TypeError("scan_%s needs to be defined now." % message)
	
	def scan_ignore(self, yy:Scanner):
		assert '\n' not in yy.matched_text()
	
	def scan_keyword(self, yy:Scanner):
		word = yy.matched_text()[1:].upper()
		if word not in self.VALID_KEYWORDS: word='$bogus$'
		yy.token(word, None)
	
	def scan_enter(self, yy:Scanner, dst):
		yy.push(dst)
		yy.token('BEGIN_'+dst, None)
	
	def scan_leave(self, yy:Scanner, src):
		yy.pop()
		yy.token('END_'+src, None)
	
	def scan_punctuation(self, yy:Scanner):
		it = yy.matched_text()
		yy.token(it, it)
	
	def scan_embedded_newline(self, yy:Scanner):
		yy.token('TEXT', AST.Constant('\n', yy.current_span(), 'TEXT'))
		
	def scan_letter_escape(self, yy:Scanner):
		letter = yy.matched_text()[1]
		codepoint = 7+'abtnvfr'.index(letter)
		yy.token('TEXT', AST.Constant(chr(codepoint), yy.current_span(), 'TEXT'))
	
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
	
	def scan_escape_literal(self, yy:Scanner):
		yy.token('TEXT', AST.Constant(yy.matched_text()[1:], yy.current_span(), 'TEXT'))
	
	def scan_sigil(self, yy:Scanner, kind:str):
		# Like scan_string but removes the first char from the semantic value.
		name = AST.Name(yy.matched_text()[1:], yy.current_span())
		yy.token(kind, AST.Sigil(name, kind))
	
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
	def parse_true(self, *args): return True
	def parse_false(self, *args): return False
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
	
	def parse_define_shape(self, name, shape):
		return self.parse_field(name, None, shape)
	
	def parse_field(self, name, zone, shape):
		assert isinstance(name, AST.Name), type(name)
		assert zone is None or isinstance(zone, AST.Name), type(zone)
		assert isinstance(shape, (AST.Marginalia, AST.Frame, AST.Menu, AST.Tree, AST.LinkRef)), type(shape)
		return AST.Field(name, zone, shape)
	
	def parse_frame(self, margin, key, fields): return AST.Frame(margin, key, fields)
	def parse_menu(self, margin, key, fields): return AST.Menu(margin, key, fields)
	def parse_tree(self, margin, key, within): return AST.Tree(margin, key, within)
	
	def parse_assignment(self, name, value):
		assert isinstance(name, AST.Name)
		if isinstance(value, AST.Name): value = AST.Constant(*value, 'STRING')
		assert isinstance(value, AST.Constant)
		return AST.Assign(name, value)
	
	def parse_define_canvas(self, name:AST.Name, across:AST.Name, down:AST.Name, style_points:list, patches:list):
		return AST.Canvas(name, across, down, style_points, patches)
	
	def parse_patch_plain(self, criteria:List[AST.Criterion], content, style_points:list):
		return AST.Patch(False, criteria, content, style_points)
	
	def parse_patch_merge(self, criteria:List[AST.Criterion], content, style_points:list):
		return AST.Patch(True, criteria, content, style_points)
	
	def parse_patch_block(self, criteria:List[AST.Criterion], sub_patches:list):
		return AST.PatchBlock(criteria, sub_patches)
	
	def parse_label_interpolated(self, items) -> formulae.TextElement:
		return items[0] if len(items) == 1 else formulae.Label(items)
	
	def parse_label_constant(self, text:AST.Constant) -> formulae.Label:
		assert text.kind == 'STRING'
		assert isinstance(text.value, str)
		return formulae.Label([formulae.LiteralText(text.value)])
	
	def parse_literal_text(self, text:AST.Constant):
		assert text.kind == 'TEXT'
		return formulae.LiteralText(text.value)
	
	def parse_tpl_plaintext(self, name:AST.Name): return formulae.PlainOrdinal(name.text)
	def parse_tpl_raw(self, sigil:AST.Sigil):
		assert sigil.kind == 'COMPUTED', sigil.kind
		return formulae.RawOrdinal(sigil.name.text)
	def parse_tpl_attribute(self, axis:AST.Name, method:AST.Name): return formulae.Attribute(axis.text, method.text)
	def parse_tpl_head_ref(self, axis:AST.Name, index:AST.Constant):
		assert isinstance(index.value, int)
		return formulae.HeadRef(axis.text, index.value)
	def parse_tpl_global_ref(self, axis:AST.Name): return formulae.Global(axis.text)
	
	def parse_quote_label(self, label:formulae.TextElement):
		return formulae.Quotation(label)
	def parse_select_set(self, fields:List[AST.Name]) -> formulae.Predicate:
		if len(fields) == 1: return formulae.IsEqual(fields[0].text)
		else: return formulae.IsInSet(frozenset(f.text for f in fields))
	def parse_select_not_set(self, fields:List[AST.Name]) -> formulae.Predicate:
		return formulae.IsNotInSet(frozenset(f.text for f in fields))
	def parse_select_computed(self, computed:AST.Sigil) -> formulae.ComputedPredicate :
		assert isinstance(computed, AST.Sigil)
		assert computed.kind == 'COMPUTED', computed.kind
		return formulae.ComputedPredicate(computed.name.text)
	def parse_select_each(self) -> formulae.IsDefined:
		return formulae.IsDefined()
	def parse_criterion(self, field_name:AST.Name, predicate:formulae.Predicate) -> AST.Criterion:
		return AST.Criterion(field_name, predicate)
	def parse_gap_hint(self): return AST.GAP_HINT
	def parse_blank_cell(self): return formulae.THE_NOTHING
	def parse_linkref(self, marginalia:AST.Marginalia, name:AST.Name):
		return AST.LinkRef(marginalia, name)
	
	parse_magic_sum = staticmethod(AST.MagicSum)
	parse_raw_range = staticmethod(AST.RawRange)
