"""
The "cradle" is where things get started. Not the simplest thing that might work,
but the simplest thing that does any work whatsoever. But that's long ago now:
these days the "cradle" is bits that are not yet mature enough to live elsewhere.
"""
import os, sys, tempfile, pickle
from typing import Optional
from boozetools.support import failureprone, runtime, interfaces
from boozetools.macroparse import compiler
from . import symbols, AST, layout, streams

class Driver:
	VALID_KEYWORDS = {'NAMESPACE', 'FRAME', 'CASE', 'TREE', 'STYLE', 'MENU', 'LIKE', 'GAP', 'GRID', 'HEAD'}
	def scan_ignore(self, scanner): assert '\n' not in scanner.matched_text()
	def scan_ident(self, scanner): return 'ID', symbols.Identifier.from_text(scanner.matched_text(), scanner.current_position())
	def scan_qualident(self, scanner): return 'QUAL_ID', symbols.Qualident.from_text(scanner.matched_text(), scanner.current_position())
	def scan_match(self, scanner, param): return param, scanner.matched_text()
	def scan_token(self, scanner, param): return param, None
	def scan_reference(self, scanner, param): return param, symbols.Identifier.from_text(scanner.matched_text()[1:], scanner.current_position()+1)
	def scan_qref(self, scanner, param): return param, symbols.Qualident.from_text(scanner.matched_text()[1:], scanner.current_position()+1)
	def scan_keyword(self, scanner):
		it = sys.intern(scanner.matched_text()[1:].upper())
		if it in self.VALID_KEYWORDS: return it, None
		else: raise interfaces.ScanError('Bad Keyword')
	def scan_begin(self, scanner, condition):
		scanner.push(condition)
		return 'BEGIN_' + condition, None
	def scan_end(self, scanner, condition):
		scanner.pop()
		return 'END_' + condition, None
	def scan_punctuation(self, scanner): return scanner.matched_text(), None
	def scan_flag(self, scanner):
		match = scanner.matched_text()
		ident = symbols.Identifier(match[2:], scanner.current_position()+2)
		attr = AST.Attribute(match[0], ident)
		value = match[1] == '+'
		return 'FLAG', AST.Assignment(attr, value)
	def scan_attribute(self, scanner):
		match = scanner.matched_text()
		ident = symbols.Identifier(match[1:], scanner.current_position()+1)
		return 'ATTRIBUTE', AST.Attribute(match[0], ident)
	def scan_integer(self, scanner): return 'INTEGER', int(scanner.matched_text())
	def scan_decimal(self, scanner): return 'DECIMAL', float(scanner.matched_text())
	def scan_string(self, scanner): return 'STRING', scanner.matched_text()[1:-1]

	# Template Elements:
	def scan_literal_text(self, scanner): return 'ELEMENT', scanner.matched_text()
	def scan_simple_replacement(self, scanner):
		ident = symbols.Identifier.from_text(scanner.matched_text()[1:-1], scanner.current_position()+1)
		return 'ELEMENT', AST.Replacement(ident, None)
	def scan_formatted_replacement(self, scanner):
		axis, view = scanner.matched_text()[1:-1].split('.')
		scp = scanner.current_position()+1
		return 'ELEMENT', AST.Replacement(symbols.Identifier.from_text(axis, scp), symbols.Identifier.from_text(view, scp+1+len(axis)))
	def scan_embedded_newline(self, scanner): return 'ELEMENT', "\n"
	def scan_letter_escape(self, scanner): return 'ELEMENT', chr(7+"abtnvfr".index(scanner.matched_text[-1]))
	
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
	def parse_leaf(self, template, hint, style): return AST.Leaf(False, template, hint, style)
	def parse_mezzanine(self, template, hint, style): return None, AST.Leaf(False, template, hint, style)
	def parse_semantic_header(self, ident, template, hint, style): return ident, AST.Leaf(True, template, hint, style)
	def parse_overt_gap(self, ident, template, style): return ident, AST.Leaf(False, template, layout.GAP, style)
	
	parse_frame = staticmethod(AST.LayoutFrame)
	parse_tree = staticmethod(AST.LayoutTree)
	parse_menu = staticmethod(AST.LayoutMenu)
	parse_likeness = staticmethod(AST.LayoutLike)
	parse_namespace = staticmethod(AST.NameSpace)
	parse_assignment = staticmethod(AST.Assignment)
	parse_function = staticmethod(AST.FunctionCall)
	
	parse_ground_axis = staticmethod(streams.GroundReader)
	parse_computed_axis = staticmethod(streams.ComputedReader)

def transduce(x, context:Optional[symbols.Scope]):
	"""
	:param x: some sort of AST node -- normally a namespace in the outermost call, and recursive.
	:return: An appropriate contribution to a symbol table.
	
	In particular, the global namespace will be converted directly to a symbol table.
	"""
	if isinstance(x, AST.NameSpace):
		scope = symbols.Scope(context)
		for identifier, child_node in x.declarations:
			scope.define(identifier, transduce(child_node, scope))
		return scope

	if isinstance(x, AST.LayoutFrame):
		scope = symbols.Scope(context)
		schedule = []
		for identifier, child_node in x.fields:
			child_value = transduce(child_node, scope)
			if identifier is not None:
				scope.define(identifier, child_value)
				schedule.append((identifier.name, child_value))
			else: schedule.append((None, child_value))
		return layout.Frame(x.axis, scope, schedule, x.style)
	
	assert False, type(x)
	

def tables() -> dict:
	grammar_path = os.path.join(os.path.split(__file__)[0], 'grammar.md')
	cache_path = os.path.join(tempfile.gettempdir(), 'cubicle.pickle')
	if os.path.exists(cache_path) and os.path.getmtime(cache_path) > os.path.getmtime(grammar_path):
		return pickle.load(open(cache_path, 'rb'))
	else:
		result = compiler.compile_file(grammar_path, method='LR1')
		pickle.dump(result, open(cache_path, 'wb'))
		return result



def main(path):
	text = failureprone.SourceText(open(path).read(), filename=path)
	driver = Driver()
	parse = runtime.the_simple_case(tables(), driver, driver, interactive=True)
	try: module = parse(text.content)
	except interfaces.ParseError as pe:
		text.complain(*parse.scanner.current_span(), message="Parse Error Nearby contemplating:\n\t"+pe.condition())
		print(pe.yylval, file=sys.stderr)
		return
	except interfaces.ScanError as e:
		text.complain(parse.scanner.current_position(), message="Scan error: "+str(e.args[0]))
		return
	except runtime.DriverError as e:
		text.complain(*parse.scanner.current_span(), message=str(e.args))
		raise e.__cause__ from None
	assert isinstance(module, AST.NameSpace)
	return transduce(module, None)