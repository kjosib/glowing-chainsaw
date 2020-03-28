"""
A couple examples use some of the same resources and/or methods to access it. Let's share code.
"""


import zipfile, csv, io
from cubicle import runtime

def chess_data():
	"""
	Step one: Get the data!
	This will just yield a data stream as explained in the architecture document.
	"""
	zfile = zipfile.ZipFile(r"../resources/chess.zip")
	byte_data = zfile.read('games.csv')
	text_stream = io.StringIO(byte_data.decode('UTF8'))
	return csv.DictReader(text_stream)

class ChessEnvironment(runtime.Environment):
	"""
	This part is considered deeply application-specific.
	"""
	def is_interesting(self, game:str): return game.startswith('Benko')

def demonstrate(toplevel, basename):
	import os, xlsxwriter
	from cubicle import dynamic, static
	assert isinstance(toplevel, static.CubModule), type(toplevel)
	canvas = dynamic.Canvas(toplevel, "chess", ChessEnvironment())
	
	for row in chess_data():
		name = row['opening_name'].split(': ')
		point = {
			'winner': row['winner'],
			'victory': row['victory_status'],
			'game': name[0],
			'variation': ': '.join(name[1:]),
		}
		canvas.incr(point, 1)
	
	REPORT_PATH = r"..\resources\%s.xlsx"%basename
	print("Opening Workbook")
	with xlsxwriter.Workbook(REPORT_PATH) as workbook:
		sheet = workbook.add_worksheet("simple")
		print("Calling Plot")
		canvas.plot(workbook, sheet, 0, 0)
		sheet.freeze_panes(2, 1)
	print("Calling Startfile")
	os.startfile(REPORT_PATH)
