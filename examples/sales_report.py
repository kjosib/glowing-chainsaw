"""
# This module is to exercise two new features:
#    template header references
#    template global references
#
# By putting the cubicle-module definition in the doc-string,
# any compile-errors conveniently produce useful location references.

when :frame [
	now "This Period"
	all "Cumulative"
]

across width=12 :frame [
	label :head 1 width=25
	pl "Original\Plan"
	ch "Change\Orders"
	fc "Current\Forecast" @'=[across=pl|ch]'
	actual "Produced" :use when
	invoice "Invoiced" :use when
]

down :frame [
	header border=1 +text_wrap :frame [
		a "Sales Report"
		b "Period: [.period]" :head 1
	]
	_ :tree :axis region "[region] Region"
]

sales :canvas across down [
	down=header [
		:merge across=pl|ch|fc { "[across!1]" }
		:merge across=actual|invoice, header=a  { "[across!1]" }
	]
]

"""

# Begin with the usual complement of imports:
import xlsxwriter, os
from cubicle import compiler, runtime, dynamic

# Customize our "runtime" environment as needed:
class SalesEnvironment(runtime.Environment):
	pass

# Taking advantage of the doc-string for hosting the module definition:
MODULE = compiler.compile_string(__doc__)
canvas = dynamic.Canvas(MODULE, "sales", SalesEnvironment())

# Throwing in just a teeny bit of sample data:
canvas.incr({'region':'North', 'across':'pl'}, 2)
canvas.incr({'region':'South', 'across':'pl'}, 3)
canvas.incr({'region':'North', 'across':'ch'}, 1)

# Now let's get a report generated and on the screen:
with xlsxwriter.Workbook('sales.xlsx') as book:
	canvas.plot(book, book.add_worksheet(), 0, 0, blank=0)
os.startfile('sales.xlsx')
