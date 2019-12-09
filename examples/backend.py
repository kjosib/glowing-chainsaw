"""
This module exists to exercise the (new-style) back-end.
Thus, it bypasses all the convenience of a "compiled" DSL and also gives a glimpse of
what this glop would feel like as an API instead of a DSL.
"""

import os, xlsxwriter
from cubicle import static, dynamic, runtime, veneer
from examples import resources

def label_it(how, style_index=0, outline_index=0):
	component = static.LiteralTextComponent(how)
	formula = static.TextTemplateFormula([component])
	return {'style_index':style_index, 'outline_index':outline_index, 'text':[formula]}

def label_dynamic(how, style_index=0, outline_index=0):
	component = static.RawTextComponent(how)
	formula = static.TextTemplateFormula([component])
	return {'style_index':style_index, 'outline_index':outline_index, 'text':[formula]}

victory = static.FrameDefinition(static.SimpleReader('victory'), {
	'mate': static.LeafDefinition(label_it('Checkmate')),
	'outoftime': static.LeafDefinition(label_it('Time Expired')),
	'resign': static.LeafDefinition(label_it('By Resignation')),
})

drawn = static.FrameDefinition(static.SimpleReader('victory'), {
	'draw': static.LeafDefinition(label_it('Drawn', style_index=4)),
	'outoftime': static.LeafDefinition(label_it('Time Expired (?!)', style_index=4)),
})


horizontal = static.FrameDefinition(static.DefaultReader(), {
	'head': static.LeafDefinition({'outline_index':0, 'style_index':3, 'formula':0, 'width':75}),
	'_': static.FrameDefinition(static.SimpleReader('winner'), {
		'white' : victory,
		'draw': drawn,
		'black': victory,
	})
})

vertical_reader = static.DefaultReader()
vertical = static.FrameDefinition(vertical_reader, {
	'head': static.LeafDefinition({'outline_index':0, 'style_index':1, 'formula':0}),
	'_': static.TreeDefinition(static.SimpleReader('game'), static.LeafDefinition(label_dynamic('game'))),
	'sum': static.LeafDefinition({**label_it('Grand Total', style_index=2), 'formula':static.AutoSumFormula({vertical_reader.reader_key():static.SelectOne('_')})})
})

toplevel = static.TopLevel(
	{"chess": static.CanvasDefinition(horizontal, vertical, [], [])},
	[{}, {'bottom':1}, {'top':1, 'bold':True}, {'right':1}, {'left':1, 'right':1}],
	[{}],
)
canvas = dynamic.Canvas(toplevel, "chess", runtime.Environment())

for row in resources.chess_data():
	name = row['opening_name'].split(': ')
	point = {
		'winner': row['winner'],
		'victory': row['victory_status'],
		'game': name[0],
		'variation': ': '.join(name[1:]),
	}
	canvas.incr(point, 1)

REPORT_PATH = r"..\resources\backend.xlsx"
print("Opening Workbook")
with xlsxwriter.Workbook(REPORT_PATH) as workbook:
	sheet = workbook.add_worksheet("simple")
	print("Calling Plot")
	canvas.plot(workbook, sheet, 0, 0)
	sheet.freeze_panes(1,1)
print("Calling Startfile")
os.startfile(REPORT_PATH)
