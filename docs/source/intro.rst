Introduction
---------------------------------------

This document lays out the big-picture ideas so you can get your bearings
and understand how to exploit `cubicle`.

Bear in mind that some (decreasing) fraction of this document is
aspirational: it describes where I'd like the project to get to,
even though not everything is implemented yet.

Concept of Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

A domain-specific language is defined to succinctly describe the structure,
formatting, formulas, and boilerplate for business-oriented reports. An
application can then produce any such report conveniently by supplying one
or more streams of detail data and an environment of relevant business-domain
knowledge such as collation sequences, entity attributes, and so forth.

The expectation is that the underlying business domain data model will be
considerably more stable than the shifting winds of taste and temperament
that dictate how reports should look and act. As requirements evolve,
this kind of a system should help the programmer keep up. In particular,
when a new report is conceptually similar to an old one, little more than
a new skin is required: the domain model almost never changes, and existing
data access methods are often sufficient for the new task.

A simple standard interface is defined for passing data into a report,
agnostic to the source of that data. The package generates output into
spreadsheet documents using the excellent `xlsxwriter` package by John McNamara.
Once a report is generated, it can also be queried for the row- and
column-extent of specific (sets of) elements for integration with
additional requirements not specifically covered within this package.

Version one of the package focuses on attractive and professional presentation
for tabular and hierarchical reports in one or two dimensions, with limited
support for calculated functions. Later versions may add support for more
kinds of smart functions, charting integration, different output formats
such as HTML tables, ragged axes, or whatever else seems valuable.

Data Streams
^^^^^^^^^^^^^^^^^^^^^^^^^

At a Python level, `cubicle` mostly deals in streams of `point`-`magnitude` pairs.
But these are no ordinary pairs: each `point` is in fact a dictionary!

In concept, the `point` names a specific location in a notional hyperspace;
but each hyperspatial dimension has a name (rather than a positional
index) so a `point` is a dictionary from dimension-names to `ordinal` values.
The `magnitude` contributes its value to the hyperspatial location named
by the `point`.

An `ordinal` naturally ought to be drawn from what's appropriate
given the type of its dimension. For the moment, that restriction is
up to you to follow, because violating it will just break things later.

In some cases, you'll deal in non-numeric `magnitude` data. This is
particularly relevant with list-of-entity style reports.

Where you get your data streams from is up to you. However, relational
database queries are likely to be a good start.

Along with a stream of `point`-`magnitude` pairs you can generally specify
a context, which is another `point` along a different set of dimensions.
That can be useful particularly for routing the results of different
queries into different portions of a report grid.

Grids
^^^^^^^^^^^^^^^^^^^^^^^^^

A grid has a left and top `axis`, as well as a private data store
and an environment, which supplies certain supporting functions.
As a 3-D alternative, you might possibly want a family of grids,
sharing axes but using different private data for each.

An axis respects a particular layout elements (from the symbol table)
and manages tree of hash keys at run-time. It exposes operations to
find the hash node corresponding to a particular data point,
and also to resolve node selection expressions (explained later).

Actually, the bulk of the work to resolve those queries must be
delegated to the layout elements, because the layout elements
refer to `Reader` objects and potentially other custom bits.

`Reader` objects come in two forms:
* `SimpleReader` plucks a domain value directly from some input `point`.
* `ComputedReader` passes a point to a Python function registered
with the `Grid`'s environment object. This is particularly useful for
automatic implied categorization.


