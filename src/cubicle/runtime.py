"""
Here shall be defined those things necessary to integrate the presentation system
with whatever run-time plug-in computing power.
"""

from typing import Mapping

class DataStreamError(KeyError):
	pass

class AbsentKeyError(DataStreamError):
	""" args[0] is the missing Identifier. args[1] is the offending point. """

class InvalidOrdinalError(DataStreamError):
	""" args[0] is the axis Identifier, or None. args[1] is the offending ordinal. """



class Environment:
	"""
	In particular, this is the bit that gets passed around as a sort of "outside-the-global" scope.
	"""
	
	def test_predicate(self, predicate_name, ordinal) -> bool:
		method = getattr(self, 'is_'+predicate_name)
		return method(ordinal)
	
	def collation(self, dimension_name):
		""" If desired, return a sort-key function for whatever dimension. """
		return getattr(self, 'collate_'+dimension_name, None)
	
	def read_magic(self, key, point:Mapping):
		method = getattr(self, 'magic_'+key)
		return method(point)

	def plain_text(self, key, value):
		""" This is the part where you'd create special "friendly-text" methods for different things. """
		return str(value)
	