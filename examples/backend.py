"""
This module exists to exercise the (new-style) back-end.
Thus, it bypasses all the convenience of a "compiled" DSL and also gives a glimpse of
what this glop would feel like as an API instead of a DSL.
"""

from cubicle import static, veneer
from examples import resources

def label_it(how, style_index=0, outline_index=0, formula=None) -> static.Marginalia:
	component = static.LiteralTextComponent(how)
	template = static.TextTemplateFormula([component])
	return static.Marginalia(style_index, outline_index, [template], formula=formula)

def label_dynamic(how, style_index=0, outline_index=0) -> static.Marginalia:
	component = static.RawTextComponent(how)
	template = static.TextTemplateFormula([component])
	return static.Marginalia(style_index, outline_index, [template])

victory = static.FrameDefinition(static.SimpleReader('victory'), {
	'mate': static.LeafDefinition(label_it('Checkmate')),
	'outoftime': static.LeafDefinition(label_it('Time Expired')),
	'resign': static.LeafDefinition(label_it('By Resignation')),
}, static.Marginalia(0, 0, []))

drawn = static.FrameDefinition(static.SimpleReader('victory'), {
	'draw': static.LeafDefinition(label_it('Drawn', style_index=4)),
	'outoftime': static.LeafDefinition(label_it('Time Expired (?!)', style_index=4)),
}, static.Marginalia(0, 0, []))

horizontal = static.FrameDefinition(static.DefaultReader("#HORIZONTAL"), {
	'head': static.LeafDefinition(static.Marginalia(3,0,formula=0,width=75)),
	'_': static.FrameDefinition(static.SimpleReader('winner'), {
		'white' : victory,
		'draw': drawn,
		'black': victory,
	}, static.Marginalia())
}, static.Marginalia())

VSUM_FORMULA = static.AutoSumFormula({'#VERTICAL': static.SelectOne('_')})

vertical = static.FrameDefinition(static.DefaultReader('#VERTICAL'), {
	'uberhead': static.LeafDefinition(static.Marginalia(6,0)),
	'head': static.LeafDefinition(static.Marginalia(1,0, formula=0)),
	'_': static.TreeDefinition(static.SimpleReader('game'), static.LeafDefinition(label_dynamic('game')), static.Marginalia()),
	'sum': static.LeafDefinition(label_it('Grand Total', style_index=2, formula=VSUM_FORMULA)),
}, static.Marginalia())

style_rules = [
	veneer.Rule([veneer.CursorPluginPredicate('game', 'interesting')], 5),
]

formula_rules = []

merge_specs = [
	static.MergeSpec({'winner': static.SelectSet({'white', 'black'}),}, {'#VERTICAL': static.SelectOne('uberhead'),}, static.TextTemplateFormula([
		static.PlainTextComponent('winner'),
		static.LiteralTextComponent(' wins'),
	])),
	static.MergeSpec({'winner': static.SelectOne('draw'),},{'#VERTICAL': static.SelectOne('uberhead'),}, static.TextTemplateFormula([
		static.LiteralTextComponent('Drawn Game'),
	])),
]

toplevel = static.CubModule(
	{"chess": static.CanvasDefinition(horizontal, vertical, style_rules, formula_rules, merge_specs)},
	[{}, {'bottom':1}, {'top':1, 'bold':True}, {'right':1}, {'left':1, 'right':1}, {'bg_color':'yellow'}, {'align':'center', 'left':1, 'right':1, 'bottom':1, 'top':1, 'bold':True}],
	[(0, None, None,),],
)

resources.demonstrate(toplevel, 'backend')

