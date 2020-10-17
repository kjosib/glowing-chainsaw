"""
Here shall be defined those things necessary to integrate the presentation system
with whatever run-time plug-in computing power.
"""

from typing import Mapping, Callable, Dict

class DataStreamError(KeyError):
	pass

class AbsentKeyError(DataStreamError):
	""" args[0] is the missing Identifier. args[1] is the offending point. """

class InvalidOrdinalError(DataStreamError):
	""" args[0] is the axis Identifier, or None. args[1] is the offending ordinal. """



class Environment:
	"""
	(Some subclass of) this gets passed around as a sort of global/built-in scope for an
	entire report/canvas. This is the "abstract" version. See `class Env` for the common case.
	"""
	
	def test_predicate(self, predicate_name, ordinal, key:str) -> bool:
		method = getattr(self, 'is_'+predicate_name)
		return method(ordinal)
	
	def collation(self, dimension_name):
		""" If desired, return a sort-key function for whatever dimension. """
		return getattr(self, 'collate_'+dimension_name, None)
	
	def read_computed_key(self, key, point:Mapping):
		method = getattr(self, 'magic_'+key)
		return method(point)

	def plain_text(self, key, value):
		""" This is the part where you'd create special "friendly-text" methods for different things. """
		return str(value)
	
	def get_global(self, name:str):
		""" Whatever this returns must be allowable in a spreadsheet as-is. """
		raise NotImplementedError(type(self))

class Dimension:
	"""
	Subclasses collaborate with `Env` to provide other-than-default behavior
	*conveniently* along particular (named) axes within the canvases/reports
	controlled by those `Env` objects.
	"""
	sort_key : Callable[[object], object] = None
	def as_text(self, value) -> str: return str(value)
	def attribute(self, value, attr:str):
		try: return getattr(value, attr)
		except AttributeError: return "[-."+attr+": not found-]"
		except TypeError: return "[-."+attr+": bad type-]"
	def indexed(self, value, idx:int): return "[-index-]"

class Env(Environment):
	"""
	This should be your common-case environment object for a canvas or report.
	The current design idea is you'll have an easy interface to setting up
	common use cases.
	"""
	
	def __init__(self, *, env:dict=None, dims:Dict[str, Dimension]=None):
		self.dims = {} if dims is None else dims
		self.default = Dimension()
		self.env = {} if env is None else env
	
	def __dim(self, key) -> Dimension: return self.dims.get(key, self.default)
	
	def plain_text(self, key, value): return self.__dim(key).as_text(value)
	
	def collation(self, key): return self.__dim(key).sort_key
	
	def get_global(self, name: str):
		try: return self.env[name]
		except KeyError: return "[.%s: missing global]"%name
	