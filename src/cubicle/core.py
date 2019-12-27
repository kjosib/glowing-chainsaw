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
	return driver.build_toplevel()

class CoreDriver:
	VALID_KEYWORDS = {'LEAF', 'FRAME', 'MENU', 'TREE', 'OF', 'STYLE', 'CANVAS'}
	def scan_ignore(self, scanner): assert '\n' not in scanner.matched_text()

