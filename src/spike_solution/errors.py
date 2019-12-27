"""
I find it handy to expose all the error/exception classes in one place.
"""

class DataStreamError(Exception):
	pass

class AbsentKeyError(DataStreamError):
	""" args[0] is the missing Identifier. args[1] is the offending point. """

class InvalidOrdinalError(DataStreamError):
	""" args[0] is the axis Identifier, or None. args[1] is the offending ordinal. """


