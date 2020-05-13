"""
This module exercises the "core-cubicle" domain-specific language using the
same chess-results records as the spike_chess and back-end examples.

Need a simple example? You've come to the right place.
I'm not bothering with SQL or big-data glop right now.
I've a zipped CSV file containing a bunch of tournament chess game outcomes.
I'd like to see how successful different opening lines are, on average, as white or black.
I'd also like some little illustration some of the hierarchy.
Rather than putting my report definition in another file, I'll just use a here-document.
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
	head :head 1 bottom=1 +shrink align=center  # The `:head 1` clause stands in place of a formula.
	# An underscore indicates a default field, used if 'down' is not provided:
	_ "[game]" :tree game   # Double quotes surround interpolated templates which may contain replacement parameters.
	sum 'Grand Total' @'sum([down=_])' top=1 +bold   # @'...' becomes a free-form formula. More magic may come later.
]

across :frame [
	label :head 1 right=1 width=75
	# Semicolons separate short inline field lists:
	_ :frame winner [ white :use victory; draw :use draw; black :use victory ]
]

chess :canvas across down num_format='#,##0' [
	# A canvas takes two axial definitions,
	# zero or more global formatting items (attributes or styles),
	# and a block of patch specifications.
	game=@interesting { bg_color='yellow' }
]
"""
cub_module = compiler.compile_string(source_string)

if cub_module is None:
	print("Aborting.")
else:
	resources.demonstrate(cub_module, 'core_chess')
