# Plotting in Detail

The abstract is given in the overall [technical notes](technote.md).
Here are some ways, in fact and fancy, that this could work, as well as
the reasons for the chosen decisions.

All of the rows/columns will need distinct corresponding leaf nodes.
These leaf nodes index into the data store to find quantity data.
They also quite reasonably should be assigned to "format classes" about
which more will be said later.

By the time any actual plotting is done, all aliasing has been removed
from the definitions of axes, so there's that.

All this combines to mean that, during the planning phase, a single
tree-walk can (and should) assign the leaves' spatial positions,
accumulate the ordered list of leaves, and work out the format class
numbers of all leaf (obviously) and internal (for merges) nodes.

## Cursors:
A dictionary from axis-keys to labels is sufficient to name any
point on a grid, or node within a tree, so long as the axis-keys
follow certain rules. As a matter of good sense, no `ShapeDefinition`
may have an ancestor with an identical axis key.
Also, the horizontal keys must be disjoint from the vertical keys.

Such a dictionary can be seen as a "context" for anchoring
ranges of related cells which formula parameters may refer to.


## Format Class Numbers?
Formatting directives are based on predicates. Predicates apply to cursor keys.
Cursor keys SHOULD be either horizontal or vertical, but in any case the
`ShapeDefinition` must be able to help accumulate the set of such keys
over which it, or any of its descendants, are concerned.

Note that it may be valuable to support various KINDS of predicates, and
not simply "equals X" or whatever. In particular, we might want to know if
we're on the first or last member of each whatever, so that box directives
can play well with merges. (These are tricky to do right, so ... careful!)

## Axis Planning:
So now we understand that every node needs first-row, last-row, and
style code. We also understand that this walk requires a cursor and a
leaf list, but also a first- and last-set.

## Merges:
Merges are special, and they really should have their own formatting
directives attached. This is especially useful for making sure
borders are drawn correctly. In fact, it may be worthwhile to consider
box directives on a similar footing to merges, but I digress.

## Boilerplate: Formulas, Gaps, and Headers
Similar to formatting instructions?

During planning, if the ShapeDefinition objects are imbued with,
say, a numeric reference into a list of all known marginalia,
then this reference can be copied to the dynamic-trees. That,
along with priority information, can resolve MOST of the question
"what margin notes apply?".

What marginalia cannot specify, "zones" given by selectors in the
canvas definition certainly can.

All of this suggests a new architecture. 

