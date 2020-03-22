"""
This module exercises the "core-cubicle" domain-specific language using the
same chess-results records as the spike_chess and back-end examples.
"""

from examples import resources
from cubicle import core

toplevel = core.compile_string("""
victory :frame victory [
	mate 'Checkmate' .left=1
	outoftime 'Time Expired'
	resign 'By Resignation' .right=1
]

draw :frame victory [
	draw 'Drawn' .left=1
	outoftime 'Time Expired' .right=1
]

across :frame _HORIZONTAL [
	label :head 1 .right=1 !width=75
	_ :frame winner [ white :use victory; draw :use draw; black :use victory ]
]

down :frame _VERTICAL [
	uberhead :gap .align=center .border=1 +bold
	head :head 1 .bottom=1
	_ :tree game "[game]"
	sum 'Grand Total' sum(_VERTICAL=_) .top=1 +bold
]

""")

resources.demonstrate(toplevel, 'core_chess')
