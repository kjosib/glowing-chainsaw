"""
Some utility functions and classes that should make life easier everywhere else.
"""

class Visitor:
	"""
	Visitor-pattern in Python, with fall-back to superclasses along the MRO.
	
	Actual visitation-algorithms will inherit from Visitor and then each
	`visit_Foo` method must call `self.visit(host.bar)` as appropriate. This
	is so that your visitation-algorithm is in control of which bits of an
	object-graph that it actually visits, and in what order.
	"""
	def visit(self, host, *args, **kwargs):
		method_name = 'visit_'+host.__class__.__name__
		try: method = getattr(self, method_name)
		except AttributeError:
			# Searching the MRO incurs whatever cost there is to set up an iterator.
			for cls in host.__class__.__mro__:
				fallback = 'visit_'+cls.__name__
				if hasattr(self, fallback):
					method = getattr(self, fallback)
					break
			else: raise
		return method(host, *args, **kwargs)


