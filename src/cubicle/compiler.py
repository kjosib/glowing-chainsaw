"""
Sequencing control for the cubicle compiler.
Basically, it's this module's job to coordinate the activities of
the front and middle ends to produce a loadable static object
which can later be fed to the dynamic module.
"""

from . import frontend, middle

def compile_string(string, *, filename=None):
	parser = frontend.CoreDriver()
	result = parser.parse(string, filename=filename)
	if parser.errors:
		raise ValueError("Unable to compile cubicle module.") from None
	else:
		return middle.make_cub_module(result)

def compile_path(path):
	with open(path) as fh: string = fh.read()
	return compile_string(string, filename=path)


