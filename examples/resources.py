"""
A couple examples use some of the same resources and/or methods to access it. Let's share code.
"""


import zipfile, csv, io

def chess_data():
	"""
	Step one: Get the data!
	This will just yield a data stream as explained in the architecture document.
	"""
	zfile = zipfile.ZipFile(r"../resources/chess.zip")
	byte_data = zfile.read('games.csv')
	text_stream = io.StringIO(byte_data.decode('UTF8'))
	return csv.DictReader(text_stream)

