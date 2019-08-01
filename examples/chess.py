"""
Need a simple example? You've come to the right place.
I'm not bothering with SQL or big-data glop right now.
I've a zipped CSV file containing a bunch of tournament chess game outcomes.
I'd like to see how successful different opening lines are, on average, as white or black.
I'd also like some little illustration some of the hierarchy.
Rather than putting my report definition in another file, I'll just use a here-document.
"""

import os, zipfile, csv
from cubicle import cradle

def chess_data():
	"""
	Step one: Get the data!
	This will just yield a data stream as explained in the architecture document.
	"""
	
cradle.compile(r"../resources/example.cub")

