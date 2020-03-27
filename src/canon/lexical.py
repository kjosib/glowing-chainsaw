"""
I've changed my mind a few times on how the phrase-level syntax should work,
but the basic elements of "word-level" or lexical analysis have stayed mostly
the same throughout. Therefore, the majority of the scanner routines are here.
This also allows some unification with the spike-solution: probably good.
"""

from boozetools.support.interfaces import Scanner

class LexicalAnalyzer:
	KEYWORDS_SPIKE_ONLY = {'NAMESPACE', 'CASE', 'LIKE'}
	KEYWORDS_CUB_ONLY = {'LEAF', 'OF', 'USE'}
	KEYWORDS_IN_COMMON = {'FRAME', 'TREE', 'STYLE', 'MENU',  'GAP', 'CANVAS', 'HEAD'}
	VALID_KEYWORDS = KEYWORDS_IN_COMMON|KEYWORDS_CUB_ONLY|KEYWORDS_SPIKE_ONLY
	
	def scan_ignore(self, yy:Scanner): assert '\n' not in yy.matched_text()
	def scan_token(self, yy:Scanner, kind): yy.token(kind, yy.matched_text())
	def scan_sigil(self, yy:Scanner, kind): yy.token(kind, yy.matched_text()[1:])
	def scan_keyword(self, yy:Scanner):
		word = yy.matched_text()[1:].upper()
		if word not in LexicalAnalyzer.VALID_KEYWORDS: word='$bogus$'
		yy.token(word, None)
	def scan_enter(self, yy:Scanner, dst):
		yy.push(dst)
		yy.token('BEGIN_'+dst, None)
	def scan_leave(self, yy:Scanner, src):
		yy.pop()
		yy.token('END_'+src, None)
	def scan_delimited(self, yy:Scanner, what): yy.token(what, yy.matched_text()[1:-1])
	def scan_integer(self, yy:Scanner): yy.token('INTEGER', int(yy.matched_text()))
	def scan_hex_integer(self, yy:Scanner): yy.token('INTEGER', int(yy.matched_text()[1:], 16))
	def scan_decimal(self, yy:Scanner): yy.token('DECIMAL', float(yy.matched_text()))
	def scan_punctuation(self, yy:Scanner):
		it = yy.matched_text()
		yy.token(it, it)
	def scan_embedded_newline(self, yy:Scanner): yy.token('TEXT', '\n')
	def scan_letter_escape(self, yy:Scanner): yy.token('TEXT', chr(7+'abtnvfr'.index(yy.matched_text())))
	
	# And if I forgot something:
	def default_scan_action(self, message, scanner, param):
		raise TypeError("scan_%s needs to be defined now." % message)

