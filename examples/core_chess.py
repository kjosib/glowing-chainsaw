"""
Need a simple example? You've come to the right place.

This module exercises the "project-cubicle" domain-specific language using
tournament chess game result records I pulled off kaggle.com (with permission).

I'd like to see how successful different opening lines are, on average, as white or black.
I'd also like some little illustration some of the hierarchy.
Rather than putting my report definition in another file, I'll just use a here-document.
"""

import zipfile, csv, io, os, xlsxwriter
from cubicle import compiler, runtime, dynamic

# Because it's the main point, let's begin by compiling a report structure definition:

def cubicle_module(): return compiler.compile_string("""
# Commentary begins with a hash mark and extends to the end of the line.
# There is one exception, which is that a hash-mark followed by six hexadecimal digits
# actually represents a color code.

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
""")

# (If performance is a concern, you can certainly pre-compile from a file and pickle
# the resulting static data structure.)

# Any decent report needs some underlying data.
# I've enclosed some chess match statistics in a zip file:
def chess_data():
	zfile = zipfile.ZipFile(r"../resources/chess.zip")
	byte_data = zfile.read('games.csv')
	text_stream = io.StringIO(byte_data.decode('UTF8'))
	return csv.DictReader(text_stream)

# A report definition is allowed to reference various computed properties and predicates.
# This is how we make that happen:
class ChessEnvironment(runtime.Environment):
	"""
	This part is considered deeply application-specific.
	"""
	def is_interesting(self, game: str): return game.startswith('Benko')

# And finally:
def main():
	""" A simple driver for the chess statistics demonstration. """
	
	# Begin by constructing a canvas, by reference to the compiled cubicle module.
	canvas = dynamic.Canvas(cubicle_module(), "chess", ChessEnvironment())
	
	# Shove some data into the canvas.
	for row in chess_data():
		name = row['opening_name'].split(': ')
		point = {
			'winner': row['winner'],
			'victory': row['victory_status'],
			'game': name[0],
			'variation': ': '.join(name[1:]),
		}
		canvas.incr(point, 1)
	
	# Emit the fully formed and formatted report into an excel spreadsheet.
	report_path = r"..\resources\core_chess.xlsx"
	print("Opening Workbook")
	with xlsxwriter.Workbook(report_path) as workbook:
		sheet = workbook.add_worksheet("simple")
		print("Calling Plot")
		canvas.plot(workbook, sheet, 0, 0)
		sheet.freeze_panes(2, 1)
	
	# Open the resulting report so you can see it worked.
	print("Calling Startfile")
	os.startfile(report_path)


main()

