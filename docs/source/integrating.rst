Integrating with Cubicle
===================================

This document shows you how to tie all the bits together
and generate full-featured reports using a minimum of code.

Quick Start
---------------------

Here's a minimal complete report generation program:

.. code-block:: python

	import xlsxwriter, os
	from cubicle import compiler, dynamic, runtime

	module = compiler.compile_path("path/to/quickstart.cubicle")
	env = runtime.Environment()
	canvas = dynamic.Canvas(module, 'example', env)

	for point, value in data_source(): # You define data_source().
		canvas.incr(point, value)

	with xlsxwriter.Workbook('quickstart.xlsx') as book:
		sheet = book.add_worksheet()
		canvas.plot(book, sheet, 0, 0, 'blank')

	os.startfile('quickstart.xlsx')

What is going on here?

* Import the bits you need.
* Build the cubicle module corresponding to the report you want to format.
* Supply a "runtime environment" which connects your business layer.
* Instantate a :code:`Canvas` object.
* Fill data into said :code:`Canvas` object.
* Plot the canvas into a suitable workbook/worksheet pair.
* Open the resulting file for the end-user.

You can learn the :code:`cubicle` language from the `language` chapter.
You can substitute :code:`compile_string(...)` if you prefer your report
definition inline with the report program, although if you have a sizable
suite of reports you maintain, you probably want to put them all in a
common external file and pull out the specific canvas you need.

Supplying Data
---------------------

etc. etc. etc.


Business Logic and Domain Knowledge
------------------------------------------

You'll normally extend :code:`runtime.Environment` class and supply
your own instance instead of using the completely generic version.
It comes pre-built with some bits to simplify plugging predicates,
collations, and inferences appropriate to your application domain.

.. code-block:: python

	class MyEnv(runtime.Environment):
		... Application-specific customization goes here ...

	... and then later ...

	env = MyEnv()
	canvas = dynamic.Canvas(module, 'example', env)


Computed Predicates
^^^^^^^^^^^^^^^^^^^^^^^^

You can implement a method like this:

.. code-block:: python

	class MyEnv(runtime.Environment):
		...
		def is_interesting(self, game: str):
			return game.startswith('Benko')
		...

With that in place, you can use :code:`game=@interesting` anywhere a
field predicate is called for in the cubicle module.

Computed Axes (e.g. Default Categories)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Suppose you report on groceries, and you frequently
group them by "produce / meats / dry-goods" categorization.
Maybe you call that "department". So most of your data sources
will supply a food ID, and most of your reports need to know the
department. You don't want to have to modify the data sources.
Instead, make your reports use a computed axis :code:`@department`,
and then implement as follows:

.. code-block:: python

	FOOD_DEPARTMENT = {...}  # Maybe query a database ahead of time.

	class MyEnv(runtime.Environment):
		...
		def magic_department(self, point:dict):
			food = point['food']
			return FOOD_DEPARTMENT[food]
		...

Now any time a report has a :code:`:tree`, :code:`:frame`,
or :code:`:menu` with the axis specified as :code:`@department`
instead of :code:`department`, then Project Cubicle will consult
this method instead of expecting to find the department passed along
in the data stream.

Why the :code:`magic_` prefix? No reason. It's magic.

Custom Collation
^^^^^^^^^^^^^^^^^^^^^^^^

Going back to the groceries example, perhaps you've got a dozen
departments with a conventional order in which these should always
appear within reports, but you don't want to spell this out explicitly
all over the place. In that case:

.. code-block:: python

	class MyEnv(runtime.Environment):
		...
		def collate_department(self, department):
			return ... a comparison key ...
		...

Now when you use :code:`... :tree department ...`
(or :code:`... :tree @department ...`) in your cubicle definition,
the layout will respect the collation order you've defined here.

"Friendly Names"
^^^^^^^^^^^^^^^^^^^^^^^

Consider again the groceries. Everything in the store has a SKU number.
(That's "stock-keeping unit" for the uninitiated.) Everything in the
store's database is keyed to these numbers. But nobody thinks of
SKU #1405. Unless you've been working the check stands all summer,
you think of red bell peppers.

We'd like to be able to hand a SKU number to the canvas and know that,
in presentation, it will appear in plain English. Except that sometimes,
you actually do need to see the SKU.

This part isn't mature yet, but in concept the runtime environment object
you supply should also facilitate this kind of idea.
