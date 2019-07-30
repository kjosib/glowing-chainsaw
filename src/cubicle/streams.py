"""

"""

from . import symbols

class Environment:
	def compute_axis(self, axis, point): raise NotImplementedError(type(self))
	def friendly(self, axis, value): raise NotImplementedError(type(self))

class AxisReader:
	""" Consults a "point" and gives back a discriminant. """
	
	def __init__(self, axis :symbols.Identifier):
		assert isinstance(axis, symbols.Identifier), type(axis)
		self.axis = axis
	
	def read_axis(self, point: dict, environment): raise NotImplementedError(type(self))
	
	def read_friendly(self, point: dict, environment) -> str:
		return environment.friendly(self.axis, self.read_axis(point, environment))

class GroundReader(AxisReader):
	""" Reads a value straight out of a point. """
	def read_axis(self, point: dict, environment):
		return point[self.axis.name]

class ComputedReader(AxisReader):
	""" Rely on a registered function to compute a value from a point. """
	def read_axis(self, point: dict, environment):
		return environment.compute_axis(self.axis.name, point)
