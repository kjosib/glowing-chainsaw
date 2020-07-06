Cubicle Language Reference
=============================

This document lays out the syntax and semantics of the
:code:`cubicle` report specification language.


Overview
----------------------------------------------

The general idea is you define your report "skins" in a
*cubicle* module as described herein, compile that module
to a static data structure (which you may pickle) and then
later, construct reports based on those skins with data you
supply at runtime. Details of those other operations are in
the chapter on integration.

Top-Level Definitions
^^^^^^^^^^^^^^^^^^^^^^^^^

At the outermost (top-level) syntactic level, a cubicle module defines:

* layout structures
	These provide the general structure, format, and boilerplate
	for a report in one direction (either horizontal or vertical)
	or may be used as sub-components in larger layout structures.

* styles
	These provide for naming and re-using particular groups of color,
	font, border, formatting, etc. etc. etc.
	Styles may be used anywhere formatting directives are appropriate.

* canvas definitions
	These describe entire report structures in 2-D. They:

	* refer to horizontal and vertical layout structures,
	* provide global "background" formatting, and
	* provide "patch" boilerplate: things specified
	  in both the horizontal and vertical -- or
	  at any rate things specified to override the
	  default interaction between rows and columns.

Every definition begins with a name (identifier), then a keyword
describing what sort of thing is being defined.

Contributing Components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Within the top-level definitions, certain other things may be defined:

* Subordinate Layout
	Layout structure syntax allows arbitrary in-place nesting, so
	in general things that conceptually go together are lexically
	together in the module file.

* Named Routes
	These abstract over cosmetic details of layout structure.
	They're defined within layout structure, and used within
	both selectors and the API for named reference deep into
	nested layout structures. (Or: They *will* be, when finished.)

* Selectors
	Every place that needs to address a portion of other layout
	uses the same syntax and supports pretty much the same ideas.

* Template Strings
	Anything inside double quotes supports various automagical substitutions.

* Formula Strings
	Formulas in spreadsheets refer to other cells. *Cubicle* abstracts
	out the specific row and column numbers, so formulas can contain
	selectors to pick out the cells you mean, symbolically.

* Patch Instructions
	These take care of all the special exceptional cases in your
	report layouts which cannot be expressed simply as the cross-product
	of horizontal and vertical layout structures.

Tokens or Lexemes
---------------------------------------

The cubicle module language is composed of:

* Keywords
	| All start with a colon and delineate
	  grammatical structures. These are:
	| :code:`:axis` :code:`:canvas` :code:`:frame`
	  :code:`:gap` :code:`:head` :code:`:leaf`
	  :code:`:menu` :code:`:merge` :code:`:path`
	  :code:`:style` :code:`:tree` :code:`:use`
	| Keywords are not case-sensitive.

* Identifiers
	Following the usual programming-language convention,
	these start with a letter and may contain digits and underscores.
	Certain identifiers are special in certain contexts.

* Sigils
	Punctuation marks prefixing an identifier to inflect
  	it with special meaning:

	* :code:`%foo` is a style reference.
	* :code:`@foo` is a computed reference.
	  (You supply a definition at runtime).
	* :code:`+foo` and :code:`-foo` turn on or off boolean
	  formatting elements like bold or underline.
	* :code:`~foo` is a reference to a named route in the layout.

* Integer and Real numbers
	These follow the ordinary conventions for representation.
	In addition, you can supply a hexadecimal integer by
	prefixing it with the :code:`$` sign, as in :code:`$DEADBEEF`.

* Colors
	In addition to the sixteen predefined color names,
	a hash mark followed by six hexadecimal digits,
	like :code:`#feeded` is taken as a color. This rule
	takes precedence over the end-of-line comment rule.

* Comments
	a hash mark (:code:`#`) which is NOT immediately
	followed by six hexadecimal digits is taken as the
	start of a comment, which extends to the end of the
	same line. Comments are ignored, like whitespace.

* Simple strings
	surrounded by single quotes :code:`'like this'`, and which do not
	implement substitution.

* Template strings
	surrounded by double quotes :code:`"like this"`
  	and which interpolate substitution parameters found
	within :code:`[square]` brackets.

* Formula strings
	prefixed by the (:code:`@`) sign and otherwise surrounded
	by single quotes like this example:
	:code:`@'sum([across=_,winner=*,victory=*])'`
	Square brackets delimit reference-replacement parameters.

* Whitespace
	Newlines are significant to the general syntax. Horizontal
	whitespace is taken literally within all kinds of strings.
	In other respects, the amount and type of whitespace is
	ignored except as a a convenient separator between tokens
	which might otherwise be confused. In particular, indentation
	is not significant, but it's good for anyone reading your code.

* Various punctuation and nesting concepts
	Commas, semicolons, curly braces, brackets, and parentheses all
	have their places.

Styles
-------------------------------------------

All layout elements, canvases, and patch definitions
can be styled with formatting attributes, which are
basically defined by what the *xlsxwriter* module supports.

The language allows you to define and refer back to
named collections of formatting attributes.

Format Attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can use sigils like :code:`+bold` and :code:`-text_wrap` turn on or off boolean
attributes. Other attributes need a specific value.
If that value is a number or *looks like an identifier,* you may
supply it without quotes, as in :code:`align=center`. If the attribute
is a complex string, surround it with single-quotes, as in
this example: :code:`num_format='0.0%;[red]-0.0%'` Finally,
if the attribute is a color, you can use either a predefined name,
like :code:`font_color=green` or a hexadecimal color code,
like :code:`bg_color=#ffcccc`. (At some point support for decimal
RGB colors may be added.)

The exact list of supported attributes is defined in the file
:code:`cubicle/xl_schema.py`, which please see.

	Note on special cases:
		Setting either of the
		properties *border* or *border_color* stands in
		for setting the corresponding attributes on all
		four of top, bottom, left, and right.

Defining a named style
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To define a style called "example", include a line like:

:code:`example :style +bold +underline align=center`

The pattern is:

#. name of the style
#. keyword :code:`:style`
#. one or more formatting attributes as described in the previous section.
#. newline

Please note: styles can only be defined in the outermost
scope of a module. Attempting it nested inside other structures
will yield a syntax error upon compiling the module.

Referring back to a style
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assuming you've defined a style called "example",
then later on in the module you can refer back to it
with the :code:`%example` sigil wherever formatting
attributes are appropriate, *including in subsequent style
definitions*.

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

If a structure named in a :code:`:use` clause contains :code:`:zone`
definitions, then these are meant to be available within the larger
structure, HOWEVER the precise semantics are still in flux.

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
express as the intersection of marginalia. Every
patch instruction consists of:

	| *<merge_option> <selector>* :code:`{` *<content> <formatting>* :code:`}`

#. Optional :code:`:merge` keyword
	If present, the selected cell blocks get merged in the report.

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

The general idea is that patches take effect as if painted in order
from first to last. (That's not the actual algorithm, but it could be,
and the only distinction would be performance.)

Nesting Patches
................................

This part describes a planned feature. It does not work yet.

	The idea is to add nesting structure for (non-merge) patches.
	Suppose several subsequent patch instructions have several
	criteria in common: I'd like to be able to give the common
	subset of criteria, then nested within brackets, a subordinate
	list of (now shorter) patch instructions.

Named Zone Intersection
................................

If both the horizontal and vertical layout structures associated with
a :code:`:canvas` definition both define a :code:`:zone` with the same
name, then for patch instructions and the application interface, the
zone name will refer to the intersection of the two sets of constraints.

In other words, you can define :code:`:zone data` in both the horizonal
and vertical dimensions, and the system will do the right thing.

Selectors
-------------------------------------------

A *selector* is a symbolic reference to some specific portion of
layout. Selectors are used in a couple different ways. A selector:

Within a formula string, inside square brackets:
	Becomes a cell reference embedded in the resulting formula
	that gets written into the workbook when the canvas gets plotted.

In the head of a patch instruction:
	Tells which portion of the layout canvas to apply the
	templates, formulas, and formatting in the body of the
	patch instruction.

Selector Syntax and Semantics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Syntactically, a selector is written down as a comma-separated list
of *criteria*. Semantically, it represents all cells (or in the case
of merge-instructions, all cell-blocks) with layout-addresses that
satisfy the conjunction (logical-AND) of the given criteria.

Ordinary Criteria
..........................

Each criterion is generally written as:

	| *<axis>* :code:`=` *<predicate>*

The *axis* is the name of a characteristic axis for some composite
layout structure. (Even if the axis is computed, leave off the :code:`@`
inside a selector.)

Named-Zone Criteria
..........................

You may also refer to named-zones within selectors:

	| :code:`~like_this`

The sigil :code:`~` denotes a zone/route defined within
layout structure. For example, :code:`~hours` would
refer to a route called "hours", and stand in for all
appropriate criteria to select that portion of layout.

	At the moment zone references only work properly within
	patch-instructions. The plan is to make them also work inside
	layout definitions, but this may be another few days.

Static Predicates
.....................

The simplest predicate is just a field name appropriate to the
axis associated with the predicate. It selects very specifically
that one sub-layout. To support :code:`:frame` layouts with a "default"
field, the underscore (:code:`_`) is a valid name in this context.

You can supply a list of alternatives, separated by :code:`|` vertical
bar characters. In this case, each alternative is selected individually.

You can specify "all sub-fields *except* one or more alternatives"
by prepending a :code:`^` caret to the alternatives.

You may wish to specify merely that a particular axis has some value
defined at this point. In that case, the :code:`*` asterisk stands
in for the set of all values. This is especially suited to
certain applications of :code:`:merge` patch-instructions
and :code:`:tree` layouts.

Computed Predicates
........................

You can delegate a selection process to the host-language integration
layer. For example, :code:`@interesting` might implement a test for
interesting games, so in context you could write :code:`game=@interesting`
as a criterion. In place of the word "interesting" you can substitute
any identifier: the syntax is an :code:`@`\ -sigil with base-name properly
defined in your integration layer.

The implementation details are described in the integration chapter.

Selector Caveats
..........................

It is considered an error to constrain the same-named axis
twice in a single selector. This is true even if one of the
constraints is implied in a zone reference.

Template Strings
-------------------------------------------

Cubicle uses :code:`"Double Quotes"` to delimit *template strings*.
They can contain:

Replacement Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^

Inside square brackets, put the name of an axis.

Example:
	:code:`"Subtotal [region] Sales"`

Effect:
	At each cell where the template applies, the substring
	:code:`[region]`
	gets replaced by the applicable value of the
	:code:`region` axis, correctly mapped to plain text
	using the runtime-environment object.

Caveat:
	The mentioned axis is assumed to exist in the address of
	any cell where the template is used. If the example
	template applies to a cell without a :code:`region`,
	it will result in some sort of error condition.

The Future:
	I'd like to expand the syntax of replacement parameters
	to provide more control over how a value gets prepared.
	In particular, I might reasonably want different views
	of the same (Python) object in different parts of the
	same report. Implementing a design is easy enough, but
	coming up with a sufficiently-elegant design is not.

Character Escapes and Line Breaks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The usual C-style *backslash-letter* escape codes (``abtnvfr``) are supported,
although I can't imagine any use for these except for :code:`\n`,
for newline.

The aesthetics of that are dubious at best.

In general:
	You're going to want to break lines between words.
	The first word on the next line will generally be capitalized.
	Doing it with :code:`\n` will be ugly and hard to read,
	especially for nontechnical people who might contribute copy.

	Ugly Example: :code:`"Multi-Line\nTitle Text"`

Therefore:
	Backslash appearing before a capital letter *becomes*
	a line-break, leaving the capital letter intact on the
	subsequent line.

	Less-Ugly Example: :code:`"Multi-Line\Title Text"`

Finally, you can use :code:`\[`, :code:`\\` and :code:`\"`
to represent a literal left-square-bracket, backslash, or
double-quote, respectively.
(Backslash before any other character is considered a syntax error.)

	If you provide a module definition as a triple-quoted string,
	it will be an excellent idea to make that string "raw",
	as in :code:`r"""... \X  ..."""`, to avoid quadruple-backslash heck.

Formula Strings
-------------------------------------------

Begin a formula with :code:`@'` and finish it off with :code:`'`.
Leave out any leading :code:`=`. *Cubicle* will supply
that part for you.

Example:
	:code:`@'if(1+1=2, "Good!", "Oops! Wrong Universe.")'`

Formulas can contain symbolic cell references, as explained in the section
on selectors.

Example:
	:code:`@'sum([this=that,that=the_other])'`

Please note:
	Excel uses double-quotes to delimit literal strings within formulas.

	It therefore makes sense that within *Cubicle* formula strings,
	double-quotes delimit *template strings* which get interpolated
	as such. Why? Because it's useful! Besides, when are you ever going
	to include a cell reference inside a literal string?

Open Issue:
	Currently, discontiguous selectors render as a comma-separated list
	of regular (cell or range) references. That is fine for taking sums,
	but can screw up the use of other formulas. It's not clear whether
	this is an actual problem.

Ideas for the Future
-------------------------------------------

It's entirely possible new features could be added.
If you've got a good suggestion, please send it in.



