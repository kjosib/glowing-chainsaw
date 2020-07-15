"""
Cubicle is a high-level language for describing the structure, formatting,
and boilerplate for tabular reports (and perhaps eventually also charts),
combined with an API for populating and emitting these via xlsxwriter.
"""

from . import compiler, dynamic, runtime, version
from .version import __version__, __version_info__
