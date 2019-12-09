"""
Here shall be defined those things necessary to integrate the presentation system
with whatever run-time plug-in computing power.
"""

class Environment:
	"""
	In particular, this is the bit that gets passed around as a sort of "outside-the-global" scope.
	"""
	
	def test_predicate(self, predicate_name, ordinal) -> bool:
		pass
	
	def collation(self, dimension_name):
		""" If desired, return a sort-key function for whatever dimension. """
		pass
