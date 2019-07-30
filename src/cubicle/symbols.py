"""
Everything to do with the symbol table.
"""
import sys # because intern.
from typing import NamedTuple, List, Optional, Union

#################################################################
## Errors and Exceptions:
#################################################################

class SemanticError(Exception):
	""" Some subclass is raised in the event of a problem. """

class UndefinedNameError(SemanticError):
	""" args[0] is the offending Identifier object. """

class NameClashError(SemanticError):
	""" args[0] and args[1] are a pair of Identifier objects. """

#################################################################
## The structure of symbols:
#################################################################

class Identifier(NamedTuple):
	name:str
	location:int
	@staticmethod
	def from_text(text:str, location:int) -> "Identifier":
		return Identifier(sys.intern(text), location)

class Qualident(NamedTuple):
	parts:List[Identifier]
	@staticmethod
	def from_text(text:str, location:int) -> "Qualident":
		parts = []
		for name in text.split('.'):
			parts.append(Identifier.from_text(name, location))
			location += 1 + len(name)
		return Qualident(parts)

REFERENCE = Union[Identifier, Qualident]


#################################################################
## Implementing the system of scopes in a reasonable way:
#################################################################

class Binding(NamedTuple):
	identifier: Identifier
	value: object

class Scope:
	""" Things that provide a lexical scope must delegate to an instance of this. """
	def __init__(self, parent:Optional["Scope"]):
		self.parent = parent
		self.bindings = {}
		self.scope = self # This way, a Scope object implements everything we need of a namespace.
		
	def define(self, identifier:Identifier, value:object):
		assert isinstance(identifier, Identifier), type(identifier)
		name = identifier.name
		if name in self.bindings: raise NameClashError(identifier, self.bindings[name])
		else: self.bindings[name] = Binding(identifier, value)
	
	def find_reference(self, ref:REFERENCE):
		if isinstance(ref, Identifier): return self.find_identifier(ref)
		elif isinstance(ref, Qualident): return self.find_qualident(ref)
		else: assert False, type(ref)
	
	def find_identifier(self, i:Identifier):
		scope, name = self, i.name
		while scope is not None:
			if name in scope.bindings: return scope.bindings[name].value
			else: scope = scope.parent
		raise UndefinedNameError(i)
	
	def find_qualident(self, qi:Qualident):
		parts = iter(qi.parts)
		target = self.find_identifier(next(parts))
		for i in parts:
			try: target = target.scope.bindings[i.name].value
			except KeyError: raise UndefinedNameError(i)
			except AttributeError: raise
		return target

