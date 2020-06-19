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

At the moment, there are three methods considered as part of the public
API for supplying data to fill in a report. They all have a common
signature: each method expects a :code:`point` and a :code:`value`.

As used in the API, :code:`point` parameters are just dictionaries.
You fill in the keys in such manner as to indicate a distinct cell
according to the layout structure for your canvas.

One-at-a-time Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:code:`canvas.incr(point, value)`
	This is probably your most commonly used method. It adds the supplied
	(numeric) value to the value already stored at the layout cell addressed
	by the supplied point. If no such value exists yet, the starting value
	is zero. Also, any :code:`:tree` or :code:`:menu` along the way will
	automatically create any necessary children to make sure that an
	appropriate cell exists

	In the unlikely event you supply an ordinal for a :code:`:frame`
	or :code:`:menu` element which does not match a known field,
	this is considered a bug in the caller and some sort
	of exception will be tossed in your general direction.

:code:`canvas.decr(point, value)`
	This is equivalent to :code:`canvas.incr(point, 0-value)` but may
	express intent a bit more clearly: a decrement rather than an increment.

:code:`canvas.poke(point, value)`
	This sets or replaces the value currently in the cell addressed
	by the supplied point. You can use any value type which :code:`xlsxwriter`
	supports writing out to a spreadsheet: strings, numbers, dates/times,
	even URL objects. If you :code:`.poke(...)` a value which cannot be
	incremented (or decremented) in place, then do please apply common
	sense with respect to the :code:`.incr(...)` and :code:`.decr(...)`
	methods.

Data Stream Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the :code:`for`\ s, Luke.

Using Named Routes
^^^^^^^^^^^^^^^^^^^^^

This part describes a planned feature. It does not work yet.

	In concept, you should be able to ask a :code:`Canvas` object
	to supply a dictionary which represents a defined route as
	known to its layout structures.

	It's not clear how this will sit with computed-axis :code:`:frame`
	or :code:`:menu` structures. Perhaps that won't be valid?

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

The interface between the :code:`dynamic.Canvas` class
and the :code:`runtime.Environment` class seems relatively
future-proof: it might gain another method
or two, but the existing methods won't go away or change
contracts, so you should be safe to experiment with different
designs.

The present *default implementations* of those four methods
provide the API described below, which *MAY BE* subject to at
least some change.

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

For the moment, you can override the :code:`.plain_text(...)` method,
perhaps to grub around for specially-named methods, but longer-term,
the plan is to make something a bit nicer.
