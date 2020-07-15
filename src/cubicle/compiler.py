"""
Sequencing control for the cubicle compiler.
Basically, it's this module's job to coordinate the activities of
the front and middle ends to produce a loadable static object
which can later be fed to the dynamic module.
"""

from . import frontend, middle, static

def compile_string(string, *, filename=None) -> static.CubModule:
	parser = frontend.CoreDriver()
	declarations = parser.parse(string, filename=filename)
	if parser.errors:
		raise ValueError("Unable to compile cubicle module.") from None
	else:
		try: return middle.Transducer(parser.source).interpret(declarations)
		except middle.SemanticError as e:
			e.show(parser.source)
			raise e from None

def compile_path(path) -> static.CubModule:
	with open(path) as fh: string = fh.read()
	return compile_string(string, filename=path)

def main():
	"""
	Compile cubicle module definitions into pickle files. Eventually.
	Incidentally, it would be nice to make the packaging system expose
	this sub-module as a script.
	"""
	import sys, argparse
	print("Not ready for prime time. Check back each Saturday night.", file=sys.stderr)
	exit(1)

if __name__ == "__main__":
	main()
