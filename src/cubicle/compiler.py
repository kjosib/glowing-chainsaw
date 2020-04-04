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
		return middle.Transducer(parser.source).interpret(declarations)

def compile_path(path) -> static.CubModule:
	with open(path) as fh: string = fh.read()
	return compile_string(string, filename=path)

def main():
	import sys, argparse
	print("Not ready for prime time. Check back each Saturday night.", file=sys.stderr)
	exit(1)

if __name__ == "__main__":
	main()
