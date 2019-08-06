"""
Need a simple example? You've come to the right place.
I'm not bothering with SQL or big-data glop right now.
I've a zipped CSV file containing a bunch of tournament chess game outcomes.
I'd like to see how successful different opening lines are, on average, as white or black.
I'd also like some little illustration some of the hierarchy.
Rather than putting my report definition in another file, I'll just use a here-document.
"""

import os, zipfile, csv, io, xlsxwriter
from cubicle import cradle, layout, streams, symbols

def chess_data():
	"""
	Step one: Get the data!
	This will just yield a data stream as explained in the architecture document.
	"""
	zfile = zipfile.ZipFile(r"../resources/chess.zip")
	byte_data = zfile.read('games.csv')
	text_stream = io.StringIO(byte_data.decode('UTF8'))
	return csv.DictReader(text_stream)


module = cradle.compile(r"../examples/chess.cub")
canvas = module.bindings['chess'].value
assert isinstance(canvas, layout.Canvas)

try:
	for row in chess_data():
		name = row['opening_name'].split(': ')
		point = {
			'winner': row['winner'],
			'victory_status': row['victory_status'],
			'game': name[0],
			'variation': ': '.join(name[1:]),
		}
		canvas.incr(point,1)
except streams.InvalidOrdinalError as e:
	module.text.complain(*e.args[0].span(), message="Invalid ordinal "+repr(e.args[1]))
	
REPORT_PATH = r"..\resources\chess.xlsx"
print("Opening Workbook")
with xlsxwriter.Workbook(REPORT_PATH) as workbook:
	sheet = workbook.add_worksheet()
	print("Calling Plot")
	try: canvas.plot(workbook, sheet, 0, 0)
	except symbols.UndefinedNameError as e:
		module.text.complain(*e.args[0].span(), message="Name isn't (always) defined in this context.")
print("Calling Startfile")
os.startfile(REPORT_PATH)
