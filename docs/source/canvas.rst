Canvas Definitions
-------------------------------------------

The complete definition for the "skin" of a report is given by
a canvas definition. This is what everything else builds up to.

Main Grammar Pattern
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

	| *name* :code:`:canvas` *across down formatting* :code:`[`
	|   *patch*
	|   ...
	|   *patch*
	| :code:`]`

The given *name* is how you look up the canvas definition in the
compiled *cubicle* module. (See the integration chapter for more.)

The identifiers *across* and *down* refer to (elsewhere-defined)
layout structures.

The *formatting* is zero or more background-level format
attributes. These apply to every cell in the report, but at
the lowest conceivable priority.

Patch Instructions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Patch instructions are how you tweak the skin in ways you can't
express as the intersection of marginalia.

The general idea is that patches take effect as if painted in order
from first to last. (That's not the actual algorithm, but it could be,
and the only distinction would be performance.)

Simple Patches
.....................

A simple patch instruction consists of:

	| *<selector>* :code:`{` *<content> <formatting>* :code:`}`

#. Selector
	a comma-separated list of selection criteria, explained below.

#. Optional Content
	If present, gives content to fill into the selected cells.
	This may be any of:

	* absent, which leaves cell content as-is.
	* a string of any sort (plain, template, or formula) which
	  replaces the content of cells in the usual manner.
	* the :code:`:gap` keyword, which expressly blanks out cells.

#. Formatting
	Any formatting attributes given here apply to all selected cells.
	These follow the same syntax as described in the section on styles.


Merge Patches
..........................

It's common to want to merge a block of cells together. The grammar
for this is the :code:`:merge` keyword in front of a simple patch:

	| :code:`:merge` *<selector>* :code:`{` *<content> <formatting>* :code:`}`

The component parts work exactly as they do for a simple patch,
but the selected cell blocks get merged in the report.

	Hint: Say :code:`something=*` in the selector
	to merge one block for each *something*.

Nesting Patches
................................

New in version 0.8.8

Suppose several successive patch instructions have several
criteria in common: It would be nicer to give the common
subset of criteria, then nested within square brackets, a
subordinate list of (now shorter) patch instructions.

	| *<selector>* :code:`[`
	|   *<patch>*
	|   ...
	|   *<patch>*
	| :code:`]`

To that end, this grammar pattern has been added and made to
work recursively: you can nest selector contexts as deep as
you like, although at some point you run out of things to specify.

