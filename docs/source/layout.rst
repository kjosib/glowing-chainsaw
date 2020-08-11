Layout Structures
-------------------------------------------

Layout structures declare the general idea of how a report
should be laid out. Any given report will have one horizontal
and one vertical layout structure. The structures come in
several varieties which can be mixed and matched to form
whatever layout you need.

A *cubicle* module can contain arbitrarily many layout structure
definitions. The nesting structure of layout elements is normally
given literally (in-place) but may instead refer back to
previously-defined structures whenever that suits you.

The "marginalia" concept
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Any given bit of layout is associated with various bits of
information about boilerplate and formatting. Collectively,
these data are called "marginalia". Think of them as notes
scrawled in the margins. All of these notes are optional,
but in the prescribed order of their appearance, they are:

#. Header Text(s):
	Either a string, a template, or a collection of these
	inside of parenthesis. These will be used according to
	formula hints on the perpendicular -- explained later.

#. Formula Hint
	This may be any of:

	* A formula-string :code:`@'like this'` which gives a
	  formula to appear in the data cells along this row
	  or column. This may optionally be followed by
	  a priority specification, which a :code:`@` followed by
	  integer to breaks ties between row and column formulas.

		If row and column both specify a formula, the higher
		priority number wins. The default priority is zero.
		If row and column formulas are tied for priority,
		the column formula wins. You can also apply formulas
		to patches declared inside a canvas definition, and these
		take precedence over everything else.

	* :code:`:gap` prevents most text from being written to this
	  row or column, even by formula hints from the perpendicular.
	  (However, header text prevails if supplied for this node.)

	* :code:`:head 1` populates the row or column with the
	  first (if any) header text drawn from the perpendicular
	  marginalia. If those marginalia have multiple header texts,
	  replace the :code:`1` with the appropriate index.

	  Headers called forth in this manner take precedence over
	  formula strings.

#. Formatting attributes and/or style references
	These are as described in the section on styles, above.

		Where row and column formats set different values on
		the same attribute, the column formatting prevails.
		You can also apply formats to patches declared inside
		a canvas definition, and these again take precedence.

Layout definitions have somewhat of a tree structure to them.
Marginalia established at a parent node automatically applies
to all child nodes unless a child expressly changes something.

Leaf Nodes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Leaf nodes are the smallest (atomic) unit of layout. They represent
either a single row or column without any dependence on data.
They can carry the full complement of marginalia.

Inside larger structures
..........................

Inside larger structures, the presence of a leaf node is implied
by not overtly declaring the use of some other kind of sub-structure.
You would instead simply supply the appropriate marginalia
(as described above) wherever the syntax calls for a subordinate
structure definition, and *cubicle* will do the right thing.

Stand-alone (named) leaves
..........................

There are a couple reasons you might wish to define a leaf
node as a top-level named structure. One idea is when
you want to emit a one-dimensional report -- that is, a
report with either a single row or a single column. No matter:
your reasons are your own. If you want to do it, *cubicle* makes
it possible.

To name a leaf-node as a module-level structure, give:

#. name of the structure,
#. keyword :code:`:leaf`
#. whatever marginalia applies, as described above
#. newline

Composite Structures:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The composite structures are :code:`:frame`, :code:`:tree`,
and :code:`:menu`. They all split layout into parts according
to a slightly different philosophy.

The Characteristic Axis
.............................

Composite structures split layout into parts. How shall
the system determine which part we're addressing when?

When you're feeding data to a report, you supply *<point, magnitude>*
pairs. The *point* is a dictionary (or mapping).

A composite structure's *reader* tells how to get the ordinal from
whatever *point* is passed into the system. A reader also has a
characteristic axis name.

A normal reader just uses the characteristic axis name as
a key in the *point* dictionary: the corresponding value provides
the ordinal used by the layout. A computed reader gets the ordinal
values in a more roundabout way, explained in detail in the
chapter on integration with Python.

It's possible to supply a *reader* in three ways. The reader is:

* By default,
	| normal, with the name of the corresponding layout structure.
	| Example: :code:`foo :tree` then :code:`foo` is the
	  reader for the tree called :code:`foo`.
	| But see the note on tree subordinates, later on.

* :code:`:axis` <name>
	| the reader is exactly the given name.
	| Example: :code:`foo :tree :axis bar` then :code:`bar` is the
	  reader for the tree called :code:`foo`.

* :code:`:axis` <computed-sigil>
	| computed, with name equal to the bare name of the sigil.
	| Example: :code:`foo :tree :axis @bar` then the characteristic
	  axis is :code:`bar` but the system expects the runtime integration
	  to supply a special method for computing :code:`bar` ordinals
	  from whatever *point* dictionaries get passed along in data streams.

Frames
................................

	| *name* :code:`:frame` *[reader] marginalia* :code:`[`
	|   *field*
	|   ...
	|   *field*
	| :code:`]`

OR:

	| *name* :code:`:frame` *[reader] marginalia* :code:`[` *field* :code:`;` ... :code:`;` *field* :code:`]`

A frame splits layout into a fixed set of parts in exactly the
order given. To route data among the parts, most normally you
would supply the frame's *name* as a key in the *point* of a
*<point,magnitude>* pair, with corresponding value drawn from
among the member field names.

Each *field* consists of a *name*,
optionally a *path tag*,
and a subordinate structure
associated to that field. As a special exception, at most one
*field* may have the name of :code:`_` which means to use
this field by default whenever a point does not have an ordinal
for this frame's key. However, a composite subordinate to :code:`_`
must have an :code:`:axis` given explicitly, for it has no default name
to fall back on.

	Path tags are a new feature under development at the moment.
	There is a separate section of this chapter devoted to them.

Trees
................................

| *name* :code:`:tree` *[reader] marginalia substructure*

A tree splits layout into arbitrarily many parts, each with
homogeneous substructure, according to the ordinals actually
observed in the data stream on the characteristic axis.

Trees do not have fields, so originally they passed their own
field-name as default axis-key to their substructure. This changed
in version 0.8.5 to prepend :code:`per_` to the tree's own axis.
For example, given something like

.. code-block:: text


	foo :tree :frame [ a; b ]

the `tree` has axis :code:`foo`, but the `frame` has axis :code:`per_foo`.
You can of course override all this by sprinkling :code:`:axis` phrases
into appropriate places.

Menus
................................

Menus provide adaptive ragged structure.

Menus have a syntax similar to that of frames, except
using :code:`:menu` in place of :code:`:frame`. The
semantics are different, though: First, a menu's fields only
appear in the output report if their corresponding ordinals
got mentioned in a data stream. Second, a menu may not have
a field called :code:`_`, because that would make no sense.

Defining Named Zones
.............................

Concept:
	Named zones attach a name to a specific section of a layout
	structure, for later reference elsewhere as a shorter,
	more shelf-stable alternative to the equivalent list
	of axis criteria.

This should:
	#.	Make other parts of a module definition less sensitive to
		cosmetic changes in layout.

	#.	Simplify references in formula strings and patch selectors.

	#.	Expose data routing information back to the run-time in a
		symbolic manner, making also the API less sensitive to
		irrelevant details of layout.

Defining Syntax:
	Immediately after a field's name in a *frame* or *menu* definition,
	the keyword :code:`:zone` followed by an identifying name for
	the route's symbol.

	Zone definitions must be unique within each distinct top-level
	layout definition.

Referring to defined structures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In place of a subordinate structure, :code:`:use` *<name>* will
evaluate to a copy of the named structure declarations.

For example:

.. code-block:: text

	foo :frame [p; d; q]
	bar :frame [
		x :use foo
		y :use foo
		z +bold :use foo
	]

This will cause all three elements of the :code:`bar` frame to
have substructure corresponding to the :code:`foo` frame. In addition,
the :code:`+bold` format attribute applies to the :code:`z` field.

Named Zones in Referred/Factored Structures
...............................................................

This is easiest to explain by example.
Suppose we have a couple of layout structures something like:

.. code-block:: text

	inner :frame [
		quantity
		rate
		total :zone frobozz @'[inner=quantity]*[inner=rate]'
	]

	outer :frame [
		product
		original :use inner
		current :use inner
		delta :use inner @'[change=current]-[change=original]'
	]

In this example, the :code:`inner :frame` contains a definition
of :code:`:zone frobozz`. Subsequently, the :code:`outer :frame`
makes three distinct references to :code:`:use inner`.

Within the scope of the :code:`outer :frame` (and anything using it)
:code:`~frobozz` is effectively defined as :code:`inner=total` --
exactly the same definition as applies within the :code:`inner :frame`
scope. It's (currently) an error to also declare :code:`:zone frobozz`
within the text of the :code:`outer :frame`

Is this the be-all end-all answer? No, probably not. But it does
enough of the job for now. If you have a good use-case why the
semantics should be adjusted, please share.

