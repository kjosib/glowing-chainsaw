"""
The "cradle" is where things get started. Not the simplest thing that might work,
but the simplest thing that does any work whatsoever.
"""
import os, sys, tempfile, pickle, typing, math
from boozetools import failureprone, runtime, interfaces
from boozetools.macroparse import compiler

class Identifier(typing.NamedTuple):
	name:str
	location:int
	def text(self): return self.name

class Qualident(typing.NamedTuple):
	path:typing.List[str]
	location:int
	def text(self): return '.'.join(self.path)

class Attribute(typing.NamedTuple):
	discriminant:str
	name:str
	location:int
	value:object

class SemanticError(Exception):
	def __init__(self, location:int, message:str):
		super().__init__(location, message)
		self.location = location
		self.message = message

def quibble(foobar:(Identifier, Qualident, Attribute), message:str):
	raise SemanticError(foobar.location, foobar.text()+': '+message)

class Environment:
	def compute_axis(self, axis, point): raise NotImplementedError(type(self))
	def friendly(self, axis, value): raise NotImplementedError(type(self))

class AxisReader:
	""" Consults a "point" and gives back a discriminant. """
	
	def __init__(self, axis:Identifier):
		assert isinstance(axis, Identifier), type(axis)
		self.identifier = axis
		self._axis = axis.name
	
	def read_axis(self, point: dict, environment): raise NotImplementedError(type(self))
	
	def read_friendly(self, point: dict, environment) -> str:
		return environment.friendly(self._axis, self.read_axis(point, environment))

class GroundReader(AxisReader):
	""" Reads a value straight out of a point. """
	def read_axis(self, point: dict, environment):
		return point[self._axis]

class ComputedReader(AxisReader):
	""" Rely on a registered function to compute a value from a point. """
	def read_axis(self, point: dict, environment):
		return environment.compute_axis(self._axis, point)


class TemplateElement:
	""" Provides a consistent and SIMPLE polymorphic approach to template substitution. """
	def text(self, point, environment) -> str: raise NotImplementedError(type(self))

class Replacement(TemplateElement):
	""" Provides for simple template replacement in labels. """
	# Anything more complex, like computed attributes or formatting, needs defining a sub-language.
	def __init__(self, reader:AxisReader):
		assert isinstance(reader, AxisReader)
		self.__reader = reader
		
	def text(self, point, environment) -> str:
		return self.__reader.read_friendly(point, environment)

class Literal(TemplateElement):
	""" Provides the literal-text feature in templates. """
	def __init__(self, text:str):
		self.__text = text
	
	def text(self, point, environment) -> str:
		return self.__text

class Heritable:
	GAP = object
	def __init__(self, hint, priority, attributes):
		assert all(isinstance(a, Attribute) for a in attributes)
		self.attributes = attributes
		self.hint = hint
		self.priority = priority or 0

class Scope:
	""" Things that provide a lexical scope of any sort should either be or delegate to this. """
	def __init__(self, parent):
		self.parent = parent
		self.bindings = {}
	def __str__(self): return '{'+', '.join("%s:%s"%I for I in self.bindings.items())+'}'
	def enter(self, identifier:Identifier, referent:object):
		if identifier.name in self.bindings:
			quibble(identifier, "is already defined.")
		else:
			self.bindings[identifier.name] = referent
	def lookup(self, reference:(Identifier, Qualident)):
		if isinstance(reference, Identifier):
			try: return self.__find(reference.name).resolve(reference.name)
			except KeyError: quibble(reference, "is used before it's defined.")
		elif isinstance(reference, Qualident):
			try:
				item = self.__find(reference.path[0])
				for name in reference.path: item = item.resolve(name)
				return item
			except KeyError: quibble(reference, "did not resolve properly.")
	def __find(self, name:str):
		if name in self.bindings: return self
		if self.parent is not None: return self.parent.__find(name)
		raise KeyError(name)
	def resolve(self, name:str): return self.bindings[name]

class NameSpace:
	""" This just holds on to declarations until the analysis pass turns it into a lexical scope. """
	def __init__(self, declarations:list):
		self.declarations = declarations
	def analyze(self, parent):
		scope = Scope(parent)
		for identifier, element in self.declarations:
			scope.enter(identifier, element.analyze(scope))
		return scope

class LayoutElement:
	""" Provides for a tree-structured backbone of what some layout might contain. """
	def analyze(self, parent) -> 'LayoutElement': raise NotImplementedError(type(self))

class Leaf(LayoutElement):
	""" Provides for either gaps, headers, detail fields, or computed fields. """
	def __init__(self, template, attributes:Heritable):
		assert isinstance(attributes, Heritable)
		self.template = template
		self.attributes = attributes
	
	def analyze(self, parent) -> 'LayoutElement': return self

class ManifestLayout(LayoutElement):
	""" Provides for fixed-layout structures. Attributes apply to subordinates unless overridden. """
	def __init__(self, attributes:Heritable, fields:list):
		assert isinstance(attributes, Heritable)
		self.attributes = attributes
		self.fields = fields
		self.sequence = []
		self.scope = None
	def analyze(self, parent) -> 'LayoutElement':
		self.scope = Scope(parent)
		for identifier, element in self.fields:
			term = element.analyze(parent)
			if identifier is None:
				self.sequence.append((None, term))
			else:
				self.sequence.append((identifier.name, term))
				self.scope.enter(identifier, term)
		return self
	def resolve(self, name:str): return self.scope.resolve(name)

class FrameLayout(ManifestLayout):
	def __str__(self): return '<Frame %s>'%self.scope

class TreeLayout(LayoutElement):
	""" Provides for arbitrary fan-out to arbitrary other structures. """
	def __init__(self, reader:AxisReader, child:LayoutElement):
		self.__reader = reader
		self.__child = child
	
	def analyze(self, parent) -> 'LayoutElement':
		self.__child = self.__child.analyze(parent)
		return self
	
	def __str__(self): return '<Tree %s>'%self.__child

class MenuLayout(ManifestLayout):
	""" Provides for things that only appear if non-zero. """
	def __init__(self, reader:AxisReader, attributes:list, fields:list):
		self.__reader = reader
		super(MenuLayout, self).__init__(Heritable(None, None, attributes), fields)

class LikeLayout(LayoutElement):
	def __init__(self, reference:Identifier, attributes:Heritable):
		self.__reference = reference
		self.attributes = attributes
		self.prototype = None
	
	def analyze(self, parent) -> 'LayoutElement':
		referent = parent.lookup(self.__reference)
		if isinstance(referent, LayoutElement):
			self.prototype = referent
			return self
		else: quibble(self.__reference, "fails to refer to a layout element.")
	
	def resolve(self, name:str): return self.prototype.resolve(name)

class Field:
	def __init__(self, name:(Identifier, None), elt:LayoutElement):
		self.name = name
		self.elt = elt

class FunctionHint:
	def __init__(self, function_name:Identifier, args:list):
		self.function_name = function_name
		self.args = args

class Driver:
	VALID_KEYWORDS = {'NAMESPACE', 'FRAME', 'CASE', 'TREE', 'STYLE', 'MENU', 'LIKE', 'GAP'}
	def scan_ignore(self, scanner): assert '\n' not in scanner.matched_text()
	def scan_ident(self, scanner): return 'ID', Identifier(sys.intern(scanner.matched_text()), scanner.current_position())
	def scan_qualident(self, scanner): return 'QUAL_ID', Qualident([sys.intern(s) for s in scanner.matched_text().split('.')], scanner.current_position())
	def scan_match(self, scanner, param): return param, scanner.matched_text()
	def scan_token(self, scanner, param): return param, None
	def scan_reference(self, scanner, param): return param, Identifier(sys.intern(scanner.matched_text()[1:]), scanner.current_position())
	def scan_qref(self, scanner, param): return param, Qualident([sys.intern(s) for s in scanner.matched_text()[1:].split('.')], scanner.current_position())
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
		return 'FLAG', Attribute(match[0], match[2:], scanner.current_position(), match[1] == '+')
	def scan_attribute(self, scanner):
		match = scanner.matched_text()
		return 'ATTRIBUTE', (match[0], match[1:], scanner.current_position())
	def scan_integer(self, scanner): return 'INTEGER', int(scanner.matched_text())
	def scan_decimal(self, scanner): return 'DECIMAL', float(scanner.matched_text())
	def scan_literal_text(self, scanner): return 'TEXT', scanner.matched_text()
	def scan_replacement(self, scanner):
		axis = Identifier(sys.intern(scanner.matched_text()[1:-1]), scanner.current_position()+1)
		reader = GroundReader(axis)
		return 'REPL', Replacement(reader)
	def scan_embedded_newline(self, scanner): return 'TEXT', "\n"
	def scan_letter_escape(self, scanner): return 'TEXT', chr(7+"abtnvfr".index(scanner.matched_text[-1]))
	def scan_string(self, scanner): return 'STRING', scanner.matched_text()[1:-1]
	def default_scan_action(self, message, scanner, param):
		raise interfaces.MetaError("scan_%s needs to be defined now."%message)
	
	def parse_none(self): return None
	def parse_empty(self): return []
	def parse_first(self, x): return [x]
	def parse_append(self, l:list, elt): l.append(elt); return l
	def parse_layout_field(self, name, field): return name, field
	def parse_layout_heading(self, template, attributes):
		assert isinstance(attributes, Heritable)
		return None, Leaf(template, attributes)
	def parse_layout_gap(self, attrs): return None, Leaf(None, Heritable(Heritable.GAP, math.inf, attrs))
	def parse_attribute(self, attr, value): return Attribute(*attr, value)
	parse_empty_module = staticmethod(NameSpace)
	parse_leaf = staticmethod(Leaf)
	parse_frame = staticmethod(FrameLayout)
	parse_tree = staticmethod(TreeLayout)
	parse_computed_reader = staticmethod(ComputedReader)
	parse_ground_reader = staticmethod(GroundReader)
	parse_literal = staticmethod(Literal)
	parse_function_hint = staticmethod(FunctionHint)
	parse_heritable = staticmethod(Heritable)
	parse_menu = staticmethod(MenuLayout)
	parse_namespace = staticmethod(NameSpace)
	parse_likeness = staticmethod(LikeLayout)

def tables() -> dict:
	grammar_path = go_get('grammar.md')
	cache_path = os.path.join(tempfile.gettempdir(), 'cubicle.pickle')
	if os.path.exists(cache_path) and os.path.getmtime(cache_path) > os.path.getmtime(grammar_path):
		return pickle.load(open(cache_path, 'rb'))
	else:
		result = compiler.compile_file(grammar_path, method='LR1')
		pickle.dump(result, open(cache_path, 'wb'))
		return result

def go_get(filename): return os.path.join(os.path.split(__file__)[0], filename)

def main():
	tempfile.gettempdir()
	text = failureprone.SourceText(open(go_get(r"../../resources/example.cb")).read(), filename='example.cb')
	driver = Driver()
	parse = runtime.the_simple_case(tables(), driver, driver, interactive=True)
	try: module = parse(text.content)
	except interfaces.ParseError as pe:
		text.complain(parse.scanner.current_position(), message="Parse Error Nearby contemplating:\n\t"+pe.condition())
		print(pe.yylval, file=sys.stderr)
		return
	except:
		text.complain(*parse.scanner.current_span(), message="Exception Thrown")
		raise
	assert isinstance(module, NameSpace)
	try:
		print(str(module.analyze(None)))
	except SemanticError as e:
		text.complain(e.location, message=e.message)
		return
	
main()