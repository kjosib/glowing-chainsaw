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
	uberhead :gap align=center border=1 +bold  # Use `+foo` and `-foo` to turn flags on and off, respectively.
	head :head 1 bottom=1 +shrink align=center  # The `:head 1` clause stands in place of a formula.
	
	_ "[game]" :tree game
	# An underscore indicates a default field, used for data if the axis (in this case "down") is not provided:
	# Double quotes surround interpolated templates which may contain replacement parameters.
	
	x :gap  bg_color=#cccccc height=6
	# A gap suppresses row/column formulas, but you can still style it.
	# For now you must provide a field name (here "x"). Maybe in future it won't be necessary.
	
	sum 'Grand Total' @'sum([down=_])' top=1 +bold
	# @'...' becomes a free-form formula. More magic may come later.
	# The part inside square brackets is a data selection. Elements not specified are taken
	# from context, so you get corresponding column sums (mostly; see later).
]

across :frame [
	label :head 1 right=1 width=75
	
	# Semicolons separate short inline field lists:
	_ :frame winner [ white :use victory; draw :use draw; black :use victory ]
	
	score 'Sample Score' @'sum([across=_,winner=white,victory=*])/sum(1,[across=_,winner=white|black,victory=*])' num_format='0.0%' +bold width=15 align=center
	# That's a pretty long line of source. I may wind up crafting some syntax to split long specifications
	# across lines, but for now it is what it is. Note that column formulas (like this one) normally take
	# precedence over row formulas (like the summation at down.sum), so you'll see a weighted average score
	# in the bottom row of the report.
	
	# I'd also like to see the total number of games of each type played.
	# Note that, since the `winner` and `victory` dimensions are `:frame` but not in context at this
	# formula, they need a specification. The asterisk (`*`) means "all possible ordinals".
	pop 'Popularity' @'sum([across=_,winner=*,victory=*])'
]

chess :canvas across down num_format='#,##0' [
	# A canvas takes two axial definitions,
	# zero or more global formatting items (attributes or styles) which have least priority,
	# and a block of patch specifications.
	
	game=@interesting { bg_color='yellow' }
	# A patch specification begins with a set of criteria, and then the intended effect inside curly braces.
	# This criteria uses the `@` sigil, which is called a "computed criterion", about which more later.
	# For now, just realize it lets you delegate the hairy bits out to (application-level) Python code.
	
	# You can merge ranges by prefixing a patch specification with the `:merge` keyword:
	:merge down=uberhead, winner=draw { 'Drawn Game' bg_color=#ffccff }
	:merge down=uberhead, winner=black|white { "[winner] Wins" }
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
	def plain_text(self, key, value):
		if key=='winner': return value.title()
		else: return super().plain_text(key, value)

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
		sheet.autofilter(1,0,1, canvas.across.tree.end() )
	# Open the resulting report so you can see it worked.
	print("Calling Startfile")
	os.startfile(report_path)


main()

