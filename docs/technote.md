# Technical Details
Or, how do the bits fit together, for my own reference after N months of being away?

## General usage:

* "Compile" a .cub module:
    * This is mostly controlled in `cradle.py`.
    * Parse actions mostly generate nodes defined in `AST.py`.
        * The start symbol of the grammar is `module`, and its only rule produces a `namespace` node.
        * Namespaces can nest and also contain any other kind of object.
        * Everything is paired with an identifier `ID` entry which knows the location of its definition.
    * It calls a "transduce" function to:   
        * walk the AST,
        * do all the symbolic linkage, and
        * catch static semantic errors. (See note)
    * It returns a `module` object:
        * **FIXME:** It is returning a `symbols.Scope` and decorating
        it with extra fields. That's bad. Define an appropriate return type.
        * A `module` should provide:
            * A sensible interface
            * An "external" scope
            * The `failureprone.Text` object for any late-bound errors
            (such as bad ordinals) to be reported with context
            drawn from the `.cub` file.

* Fetch a `canvas`-type object from somewhere in the symbol table.
    * Surely there should be a *LoD*-compliant way better than
    `canvas = module.bindings['chess'].value`
    but that's how right now.
    * This is also WRONG, because actually that should be a
    canvas *definition*, not an *actual* canvas to which
    data can be written.
    
    * `assert isinstance(canvas, layout.Canvas)`

* Feed data to the `Canvas` object, mainly by way of its `.incr` method.
* Plot results: `canvas.plot(workbook, sheet, top_row_offset, left_column_offset)`

## How the transducer works, in fact and fancy:

## The dynamic structure of a `Canvas` object:
A `Canvas` object has (access to) three principle data structures:

* The top and left *spines*, which are field definitions that
    * tell the system how to navigate symbolically amidst the actual data, and
    * supply formatting and boilerplate definitions to the plotting process.
* The top and left *trees*, which determine exactly which elements are
actually observed in actual data.
* The *actual data* that's been seen: this is a `defaultdict` object with
`row, column` node pairs for keys.

Actually, the spines (along with certain formatting and boilerplate directives)
may be reachable by reference to a canvas *definition* object

## How `.incr` and related methods work:
For each of the vertical and horizontal axes, we kick off a
tree walk using the corresponding structure definition and tree object,
using the provided `point` dictionary as a sort of search-key. If all
goes well, you get a corresponding row and column node. Thus:
`self.data[row_node, column_node] += quantity` and similar for related
methods.

During the tree navigation, what can happen?

* A `:tree` definition routes according to an ordinal: normally
drawn from the `point`, but if the reference is "computed" then instead
a corresponding *bound-function* is consulted on that point.
(As such, the need for this function can be part of the static analysis.)

Note that trees shall automatically sort their contents. It is often
sufficient to use the system's native sort order, but a key feature is
to be able to specify collation sequences. Experience has shown that
collation normally goes with the name of a field (as does "friendlificiation")

* A `:frame` definition *with* a reference (`layout.DynamicFrame`) takes its ordinal
in the same manner as a `:tree`, but constrains and orders the possible
ordinals as per the sub-fields in the definition file; providing also
potentially-ragged structure beneath.

* A `:frame` definition *without* a reference (`layout.StaticFrame`) is in a bit of a tougher
spot. Reasonable options are some kind of positional arguments or
relying on an implied default. So if one subfield is called `_` (the underscore)
then that one subfield is the ONLY possible data subfield: all else must
be headers, gaps, etc. and correspondingly the strategy need not make a dynamic tree node.
On the other hand, if NO subfield is called `_`, then clearly a positional
argument is called for. This can be arranged perhaps by making a special kind
of "axis reader" which in fact consults positional arguments rather than
the data point. Generalizing: the first case is again a special reader.

* A `:menu` is a `:frame` in which the sub-fields only appear if, in the end,
they actually contain data.

* It may, at some point, seem wise to add more various organizational features
to the language. That point is not now.

## How plotting works in the abstract:
(Structure definition classes have the *strategy* pattern here.)

First, plan the layout. This is a tree walk (in sorted order) for each axis to determine
specific row and column numbers. One strategy would be to just emit all
the leaves and number them by rote. Sometimes the range defined by
an internal node is called for. If each node gets a `.first` and `.last`,
such requests are easy to satisfy. So that's the approach taken.

Next is a cross-tab between the two sets of leaves. At each point, you have
coordinates, style data from the structure definitions, and the presence
or absence of the key in the `.data` dictionary.

If a key is present then of course it must be respected. Otherwise, the correct
thing depends on row- and column-hints as well as canvas-definition boilerplate.

## How formatting works:
At the moment, formatting makes use of an LRU cache decorator to prevent
making excessive `workbook.format` objects. It takes into account style
objects which form a tree parallel to the field definitions.

*FIXME: It should also consider format priorities and canvas-level
format specifications. At the moment, column styles always prevail.*

## How hints and boilerplate work:
Field definitions optionally have a label and a formula.
(Heading or gap status is conferred under the covers by special
super-high-priority formulae.)

Every formula has a natural priority level used to break ties, but
a specific instance of the formula can be given a higher or lower
priority in the definition language. Details are beyond the scope
of this document.

Some functions are willing to break ties with themselves: generally
this would favor the horizontal interpretation, but by flag you can
favor the vertical interpretation instead.

In other cases, you'd have to use priority levels to break conflicts.

In general, explicit formulas should precede sums of all sorts,
but again you can change this by choosing a negative priority level.

Any formulas in the `:grid` definition are considered as priority
over all hints, and take effect in the order they appear. There's
no grammar for this yet, but it will come.

## How labels work
Labels are a mini templating language. Things in brackets are replaced
by elements that consider the values in a running "cursor" and
also whatever methods may be registered to convert those values to
"friendly" human-readable strings for presentation. There is grammar
to select a specific format among potentially several by using `field.format`
notation. The corresponding formatter must be registered for this to plot.
Once again, it could be made part of a static analysis -- but why?

## How sums/functions work
The grammar recognizes something like function calls with lists of
references as parameters. These are meant to be interpreted relative
to the location of their appearance, but it's a bit tricky to work that out --
both statically and dynamically -- which is why it's not yet written.

In a sense, these can be thought of as smart shorthand for formula templates.

## How formulas work

The concept is to allow a template language for formulas in the output
spreadsheet, where replaceable tokens become cell or range addresses formed
by navigating around the point of use. Again, it's not written yet.


