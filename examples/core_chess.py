"""
This module exercises the "core-cubicle" domain-specific language using the
same chess-results records as the spike_chess and back-end examples.
"""

from examples import resources
from cubicle import core

toplevel = core.compile_string("""
""")

resources.demonstrate(toplevel, 'core_chess')
