"""

"""
import os, sys, tempfile, pickle
from boozetools.support import failureprone, runtime as brt, interfaces
from . import static, dynamic, runtime, veneer

def tables() -> dict:
	"""
	Perhaps this routine belies a deficiency in the stack, but the object is to be able to
	compile the grammar only once (or whenever it changes) and use it over and over.
	In a fully-packaged solution a pre-pickled table may seem desirable, but for now
	this adaptive approach is better for hacking on.
	"""
	grammar_path = os.path.join(os.path.split(__file__)[0], 'core_grammar.md')
	cache_path = os.path.join(tempfile.gettempdir(), 'cubicle.pickle')
	if os.path.exists(cache_path) and os.path.getmtime(cache_path) > os.path.getmtime(grammar_path):
		return pickle.load(open(cache_path, 'rb'))
	else:
		from boozetools.macroparse import compiler
		result = compiler.compile_file(grammar_path, method='LR1')
		pickle.dump(result, open(cache_path, 'wb'))
		return result


def compile_string(string): return _compile(failureprone.SourceText(string))
def compile_path(path): _compile(failureprone.SourceText(open(path).read(), filename=path))

def _compile(text:failureprone.SourceText):
	driver = CoreDriver()
	brt.the_simple_case(tables(), driver, driver, interactive=True)
	return driver.toplevel

class CoreDriver:
	VALID_KEYWORDS = {'LEAF', 'FRAME', 'MENU', 'TREE', 'OF', 'STYLE', 'CANVAS', 'GAP'}
	def scan_ignore(self, yy): assert '\n' not in yy.matched_text()
	def scan_token(self, yy, kind): return kind, yy.matched_text()
	def scan_sigil(self, yy, kind): return kind, yy.matched_text()[1:]
	def scan_keyword(self, yy):
		word = yy.matched_text().upper()
		if word not in CoreDriver.VALID_KEYWORDS: raise interfaces.ScanError(yy.current_span(), "Bad keyword")
		return word, None
	def scan_enter(self, yy, dst):
		yy.push(dst)
		return 'BEGIN_'+dst, None
	def scan_leave(self, yy, src):
		yy.pop()
		return 'END_'+src, None
	def scan_delimited(self, yy, what): return what, yy.matched_text()[1:-1]
	def scan_integer(self, yy): return 'INTEGER', int(yy.matched_text())
	def scan_decimal(self, yy): return 'DECIMAL', float(yy.matched_text())
	def scan_punctuation(self, yy):
		it = yy.matched_text()
		return it, it
	def scan_embedded_newline(self, yy): return 'TEXT', '\n'
	def scan_letter_escape(self, yy): return 'TEXT', chr(7+'abtnvfr'.index(yy.matched_text()))
	
	def __init__(self):
		self.current_style = {}
		self.current_outline = {'level': 0, 'hidden': False, 'collapse': False,}
		self.current_dim = {'height':None, 'width':None}
		self.toplevel = static.TopLevel({}, [], [])
	
	
	

