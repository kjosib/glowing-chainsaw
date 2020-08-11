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

	Note Regarding Zone Intersections:

	If both the horizontal and vertical layout structures associated with
	a :code:`:canvas` definition both define a :code:`:zone` with the same
	name, then the zone name will refer to the intersection of the two
	sets of constraints -- even within formulas defined as part of
	layout marginalia.

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

