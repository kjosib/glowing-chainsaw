"""
This module exercises the "core-cubicle" domain-specific language using the
same chess-results records as the spike_chess and back-end examples.
"""

from examples import resources
from cubicle import compiler

source_string = """
# Commentary like this.

victory :frame [  # Naming a frame here, but sort of also naming an AST fragment and a default dimension.
	mate 'Checkmate' left=1   # The single-quoted string is a header template.
	outoftime 'Time Expired'
	resign 'By Resignation' right=1   # Things like `right=1` set cell formatting rules.
]

draw :frame victory [  # The "draw" frame should still consult the "victory" dimension.
	draw 'Drawn' left=1
	outoftime 'Time Expired' right=1
]

down :frame [
	uberhead align=center border=1 +bold  # Use `+foo` and `-foo` to turn flags on and off, respectively.
	head :head 1 bottom=1   # The `:head 1` clause stands in place of a formula.
	# An underscore indicates a default field, used if 'down' is not provided:
	_ "[game]" :tree game   # Double quotes surround interpolated templates which may contain replacement parameters.
	sum 'Grand Total' @'=sum([left=_])' top=1 +bold   # @'...' becomes a free-form formula. More magic may come later.
]

across :frame [
	label :head 1 right=1 width=75
	# Semicolons separate short inline field lists:
	_ :frame winner [ white :use victory; draw :use draw; black :use victory ]
]

chess :canvas across down [  # A canvas takes two
]
"""
cub_module = compiler.compile_string(source_string)

if cub_module is None:
	print("Aborting.")
else:
	resources.demonstrate(cub_module, 'core_chess')
