"""

"""
import operator
from . import symbols, errors

class Axis:
	"""
	Participates in binding data to layout. Some details TBD.
	This is still a bit vague. It presumably stands for certain domain knowledge about a particular
	axis or dimension of data. Things like sort order and how to convert unique IDs to friendly names.
	For now, it will be very simple. These will have to live in an environment, for now.
	"""
	
	def ordinal_from(self, point): raise NotImplementedError(type(self))
	def report_bad_ordinal(self, ordinal): raise NotImplementedError(type(self))
	def key(self): raise NotImplementedError(type(self))

class SimpleAxis(Axis):
	def __init__(self, i:symbols.Identifier):
		self.i = i
		self.name = i.name
		self.sorted = sorted
	def ordinal_from(self, point):
		try: return point[self.name]
		except KeyError: raise errors.AbsentKeyError(self.i, point)
	def report_bad_ordinal(self, ordinal): raise errors.InvalidOrdinalError(self.i, ordinal)
	def key(self): return self.name
	

class DomainSchema:
	"""
	A sort of master data model. Get one of these set up and passed into the transducer.
	Most of th
	"""
