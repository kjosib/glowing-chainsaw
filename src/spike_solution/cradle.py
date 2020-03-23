"""
The "cradle" is where things get started. Not the simplest thing that might work,
but the simplest thing that does any work whatsoever. But that's long ago now:
these days the "cradle" is bits that are not yet mature enough to live elsewhere.
"""
import os, sys, tempfile, pickle
from typing import Optional
from boozetools.support import failureprone, runtime, interfaces
from boozetools.macroparse import compiler
from spike_solution import layout, AST, symbols, streams


class Driver(runtime.TypicalApplication):
	def __init__(self):
		super().__init__(tables())
	
	VALID_KEYWORDS = {'NAMESPACE', 'FRAME', 'CASE', 'TREE', 'STYLE', 'MENU', 'LIKE', 'GAP', 'CANVAS', 'HEAD'}
	def scan_ignore(self, yy): assert '\n' not in yy.matched_text()
	def scan_ident(self, yy): yy.token('ID', symbols.Identifier.from_text(yy.matched_text(), yy.current_position()))
	def scan_qualident(self, yy): yy.token('QUAL_ID', symbols.Qualident.from_text(yy.matched_text(), yy.current_position()))
	def scan_match(self, yy, param): yy.token(param, yy.matched_text())
	def scan_token(self, yy, param): yy.token(param, None)
	def scan_reference(self, yy, param): yy.token(param, symbols.Identifier.from_text(yy.matched_text()[1:], yy.current_position() + 1))
	def scan_qref(self, yy, param): yy.token(param, symbols.Qualident.from_text(yy.matched_text()[1:], yy.current_position() + 1))
	def scan_keyword(self, yy):
		it = sys.intern(yy.matched_text()[1:].upper())
		if it in self.VALID_KEYWORDS: yy.token(it, None)
		else: raise interfaces.ScanError('Bad Keyword')
	def scan_begin(self, yy, condition):
		yy.push(condition)
		yy.token('BEGIN_' + condition, None)
	def scan_end(self, yy, condition):
		yy.pop()
		yy.token('END_' + condition, None)
	def scan_punctuation(self, yy): yy.token(yy.matched_text(), None)
	def scan_flag(self, yy):
		match = yy.matched_text()
		ident = symbols.Identifier(match[2:], yy.current_position() + 2)
		attr = AST.Attribute(match[0], ident)
		value = match[1] == '+'
		yy.token('FLAG', AST.Assignment(attr, value))
	def scan_attribute(self, yy):
		match = yy.matched_text()
		ident = symbols.Identifier(match[1:], yy.current_position() + 1)
		yy.token('ATTRIBUTE', AST.Attribute(match[0], ident))
	def scan_integer(self, yy): yy.token('INTEGER', int(yy.matched_text()))
	def scan_decimal(self, yy): yy.token('DECIMAL', float(yy.matched_text()))
	def scan_string(self, yy): yy.token('STRING', yy.matched_text()[1:-1])

	# Template Elements:
	def scan_literal_text(self, yy): yy.token('ELEMENT', yy.matched_text())
	def scan_simple_replacement(self, yy):
		ident = symbols.Identifier.from_text(yy.matched_text()[1:-1], yy.current_position() + 1)
		yy.token('ELEMENT', AST.Replacement(ident, None))
	def scan_formatted_replacement(self, yy):
		axis, view = yy.matched_text()[1:-1].split('.')
		scp = yy.current_position()+1
		yy.token('ELEMENT', AST.Replacement(symbols.Identifier.from_text(axis, scp), symbols.Identifier.from_text(view, scp + 1 + len(axis))))
	def scan_embedded_newline(self, yy): yy.token('ELEMENT', "\n")
	def scan_letter_escape(self, yy): yy.token('ELEMENT', chr(7+"abtnvfr".index(yy.matched_text[-1])))
	
	# And if I forgot something:
	def default_scan_action(self, message, scanner, param):
		raise interfaces.MetaError("scan_%s needs to be defined now."%message)
	
	# Now on to the matter of parse actions:
	# Generic lists and optional-things are common in the grammar. This facilitates:
	def parse_none(self): return None
	def parse_empty(self): return []
	def parse_first(self, element): return [element]
	def parse_append(self, them:list, elt):
		them.append(elt)
		return them
	
	# How to make leaves: A spoon-ful of de-sugar helps the AST go down!
	def parse_leaf(self, template, style): return AST.Leaf(False, template, style)
	def parse_mezzanine(self, template, style): return None, AST.Leaf(False, template, style)
	def parse_semantic_header(self, ident, template, style): return ident, AST.Leaf(True, template, style)
	def parse_overt_gap(self, ident, template, fmt): return ident, AST.Leaf(False, template, (layout.GAP, fmt))
	
	# The remainder of things are just assigned sensibly to AST node types.
	parse_frame = staticmethod(AST.LayoutFrame)
	parse_tree = staticmethod(AST.LayoutTree)
	parse_menu = staticmethod(AST.LayoutMenu)
	parse_likeness = staticmethod(AST.LayoutLike)
	parse_namespace = staticmethod(AST.NameSpace)
	parse_assignment = staticmethod(AST.Assignment)
	parse_function = staticmethod(AST.FunctionCall)
	parse_canvas = staticmethod(AST.Canvas)
	
def transduce(x, context:Optional[symbols.Scope]):
	"""
	:param x: some sort of AST node -- normally a namespace in the outermost call, and recursive.
	:return: An appropriate contribution to a symbol table.
	
	In particular, the global namespace will be converted directly to a symbol table.
	"""
	def make_namespace(declarations):
		scope = symbols.Scope(context)
		for identifier, child_node in declarations:
			scope.define(identifier, transduce(child_node, scope))
		return scope
	
	def make_style(pair):
		if pair is None or not any(pair): return layout.THE_NULL_STYLE
		style = layout.Style()
		style.hint, items = pair
		style.declare(context, items)
		return style
	
	def make_frame(shy:bool):
		scope = symbols.Scope(context)
		schedule = []
		for identifier, child_node in x.fields:
			child_layout = transduce(child_node, scope)
			if identifier is not None:
				scope.define(identifier, child_layout)
				schedule.append((identifier.name, child_layout))
			else: schedule.append((object(), child_layout))
		style = make_style(x.style)
		if x.axis is None: return layout.StaticFrame(scope, schedule, style)
		else: return layout.DynamicFrame(axis_reader(x.axis), scope, schedule, style, shy)
	
	def axis_reader(ref: symbols.REFERENCE):
		if ref is None: return None
		# TODO: This is where to adjust for a data dictionary in the application environment.
		if isinstance(ref, symbols.Identifier): return streams.SimpleAxis(ref)
		if isinstance(ref, symbols.Qualident): raise symbols.UnfinishedProjectError(ref, "Qualified Axis Identifiers are not yet implemented.")
		assert False, type(ref)

	if isinstance(x, AST.NameSpace): return make_namespace(x.declarations)
	if isinstance(x, AST.Leaf): return layout.Leaf(x.is_head, x.template, make_style(x.style))
	if isinstance(x, AST.LayoutFrame): return make_frame(False)
	if isinstance(x, AST.LayoutMenu): return make_frame(True)
	if isinstance(x, AST.LayoutTree): return layout.Tree(axis_reader(x.axis), transduce(x.child, context))
	if isinstance(x, AST.LayoutLike):
		referent = context.find_reference(x.reference)
		if isinstance(referent, layout.Layout):
			clone = referent.clone(make_style(x.style))
			return clone
		else: raise symbols.TypeClashError(x.reference)
	
	if isinstance(x, AST.Canvas):
		return layout.Canvas(context.find_reference(x.down), context.find_reference(x.across),
			make_style((None, x.format)))
	
	assert False, type(x)

def tables() -> dict:
	grammar_path = os.path.join(os.path.split(__file__)[0], 'grammar.md')
	cache_path = os.path.join(tempfile.gettempdir(), 'cradle.pickle')
	if os.path.exists(cache_path) and os.path.getmtime(cache_path) > os.path.getmtime(grammar_path):
		return pickle.load(open(cache_path, 'rb'))
	else:
		result = compiler.compile_file(grammar_path, method='LR1')
		pickle.dump(result, open(cache_path, 'wb'))
		return result

def compile(path) -> symbols.Scope:
	"""
	Given a path to a .cub file, this function reads the file and translates it into a symbol table.
	:param path: string or path-like object
	:return: symbols.Scope with bindings
	"""
	driver = Driver()
	syntax_tree = driver.parse(open(path).read(), filename=path)
	try:
		assert isinstance(syntax_tree, AST.NameSpace)
		module = transduce(syntax_tree, None)
		return module
	except symbols.TypeClashError as e:
		driver.source.complain(*e.args[0].span(), message="This symbol refers to the wrong kind of value for how it's used here.")
	except symbols.NameClashError as e:
		driver.source.complain(*e.args[0].span(), message="This symbol is defined here, but...")
		driver.source.complain(*e.args[1].span(), message="Later on re-defined here, in the same scope, which is no bueno.")
	except symbols.UndefinedNameError as e:
		driver.source.complain(*e.args[0].span(), message="This symbol has no valid definition in the context of its use.")
	except symbols.UnfinishedProjectError as e:
		driver.source.complain(*e.args[0].span(), message=e.args[1])
	exit(1)
