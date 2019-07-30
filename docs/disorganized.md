# Disorganized Documentation

The point of building a system like this is to harness both cube-structured and
relational data *and functions* into a framework that supports:
* a pipeline into  presentations.
* reasonably-efficient, concise ad-hoc queries without major ceremony.
* a variety of data sources and sinks, including ad-hoc I/O.
* consistency of structure and schema.
* consistent application of business logic without having to remember every detail at all times and in all places.

## Context:
For some time now, I've been working in the arena of financial and progress reporting for
a large engineering and construction company. Now a sizable system is built in Python
atop a combination of a "poor-man's OLAP cube" library, a nice but insufficiently-excellent
layer atop `xlsxwriter`, and SQLite.

The use of named (rather than indexed) dimensions for data was a real game-changer very
early on in the development of our little reporting system, and it must be understood that
SQLite came *much* later: initially all data had to be editable using only the standard-load
desktop office suite.

Today, the RDBMS is great for ad-hoc queries, a massive performance improvement, and
dramatically simplifies many tasks, but lots of data either still lives in or gets
imported-on-change from CSV or even the occasional spreadsheet. Also, there's a lot
of business logic which flat-out requires the power of a general-purpose programming
language to get right.

One constant frustration has been that everything except the SQL is a bunch of ad-hoc
object-oriented duck-typed inconsistent dross rather than plugging into a coherent and queryable
common framework. That's what this module aims to rectify: Think of it as a way to
tie relational and multidimensional DATA and FUNCTIONS into a common scripting
framework that takes advantage of structural knowledge to produce tolerably-beautiful output.

## Background:
### Time
A lot of business data is time-series structured: How many widgets (by kind) for
each interval from January until December? But there's a second dimension of time,
which is: How did our forecast-by-period change over time?

There's a need to group data by fiscal week, month, or year. These don't line up with the
normal civil calendar but are instead dictated by a certain international standard
involving Thursdays and a 4-4-5 pattern of weeks, with a defined exception in October
for the occasional 53-week year.

Fiscal time, as a dimension, has a clear and functional hierarchy as well as a natural
ordering among points or discrete intervals at the same level. For presentation,
simple functions can be written which will render the name of any week, month, or year
in a format that even a Sarbanes-Oxley auditor has no trouble understanding.

### Space
Another major category of "dimension" is better understood as an enumeration.
School subjects are a perfect example: "Reading, Writing, and Arithmetic" are
an idiomatically-standard order-of-presentation, although this is *not* alphabetical.
People get used to seeing things in a certain order, and reporting should respect that.

Also, members of an enumeration may have various kinds of "roll-up". College courses
might naturally group into sciences, humanities, etc. These roll-ups mostly come from
some attribute of the lower-level item: it starts to sound relational because it *is*
relational in nature. However, SQL is a relatively horrible language for this kind of
thing: it makes you repeat yourself two or three times to avoid getting stupid results.

Yes, a nice SQL abstraction layer can help with the repetition, but it remains
tied to the notion that everything is a non-ordered table in the RDBMS.

### Matter
The bulk of data in the system consists of measured quantities: large groups of real
numbers associated with particular ordinals along defined dimensions. The common
operations are selection, summary, aggregation, and element-wise join.

Decency compels that glowing-chainsaw must also facilitate reading and writing data in
a variety of formats, and also structuring output data into pleasing views -- possibly
with charts, graphs, and expressions about spreadsheet formulas that should be embedded
into a final presentation. So much the better if said formulas can contain symbolic
references into other sheets or ranges which automatically get placed correctly
according to however much bulk turns out to exist in the final product.

### Energy
There are also "virtual measures" and "virtual attributes" which, under the covers,
represent functions of two or more parameters:
* How many hours are workable per week? It depends on which country you're operating
out of and what kind of schedule you drive people to.
* Which subjects are in-major or elective for GPA? It depends on the student.
* Which change notifications are active in the forecast? It depends on the effective-date
for your report, as well as some complicated logic surrounding the life-cycle of a change.
* What's the forecast if nothing has been forecast? It's the baseline, but knowing which
case to consult requires knowing which cases have been defined for any given project,
as well as a sensible fall-back schedule.

All this is to say we need to be able to plug things into TensorMatic and then access
those things in a controlled way from within the TensorMatic script language.

## The Approach:
I expect I'll cook up a little interpreter atop the booze-tools package.
You'll be able to make a blank "interpreter state", register various things,
"execute" an initialization script which probably defines a lot more things,
and then either you interact with a REPL or extract specific presentations
based, perhaps, on another fork of this DSL.

## What's this about presentations?

Ok ok ok. Basically, a particular range in a report will have some kind
of structure. Normally this is the intersection of two trees: one for the
vertical, and one for the horizontal, dimensions. It's possible to define
the layers of hierarchy for each tree. Such is aggravatingly verbose
when done in Python directly, so a nice notation would be fabulous.

Also, things do get a bit hairy in the static headers of some reports.

The main things common to every report are:
* Logical and Physical Structure, including explicit gaps and heading zones.
* Formatting, which may include merging blocks of cells.
* Static and dynamic header labels.
* Controlled aggregation: most commonly summation, but sometimes other functions.
* Consistent application of arbitrary formulas.
* Outlining
* Row and column sizes
* Plugging clumps of raw data into "the matrix", which may grow as-needed to support it.

Sometimes, reports may consist of two or more individual data grids which must
be correctly laid out on a worksheet so as not to overlap. There is usually some
sort of page header. Sometimes a collection of functionally-similar sub-reports
are to be produced from various slices of the same underlying data, each on successive
pages. That last bit may be controlled by a runtime flag, or by the presence of more
than one ordinal along some dimension....

I believe the right approach is:
* Structure definitions go in one section wherein:
  * Fields may be annotated as gaps or heading elements.
  * Outlining, sizing, and implied-aggregation declarations also go here.
  * Literal Structures get zero or more extra (named) attributes attached to
  each field, accessible later by "dynamic label" instructions.
* The remainder of the "fit and finish" shall be done with directives consisting
of a selector followed by one or more "instructions" in a line:
  * These may apply formatting, add formats, formulas, or labels, etc.
  * Selectors most normally are self-contained, but some amy need access to
  parameters from some sort of environment. A notation must be provided.
  * By the way, it's handy to be able to define shortcuts for groups of similar
  instructions that may need to apply across more than one selector.
* Formulas need a handful of cool features for relative selectors, etc.
* The actual raw data comes in through a very simple Python interface which the
main TensorMatic script language supports.

Where charts are concerned: It's important to be able to read back the layout locations
of specific portions of a grid that's been plotted to a worksheet. Having that,
one can sensibly prepare charts.

## Why the name?
Github suggested it, and I found it more amusing than my own ideas.

## What Else?
What, indeed?

At this point, sleep.

### Random Theoretical Notes

#### Time Series Data comes in three kinds:
1. Event-Stream: things happened at particular instants (to whatever resolution).
2. Interval: addresses a sum (or other aggregate) over successive similar blocks of time.
Interpolation is valid but optional.
3. Cumulative: provides a running total at the end of every participating period, with an
implied zero (in whatever structure) before the beginning of the first period.
Interpolation is valid but optional.

Normally when showing a chart, one speaks of interval or cumulative data. There is little
meaning to event-stream data. 

#### Lazy Functional Interpretation:
The script may declare relationships between all kinds of tensors,
structures, time-series, presentations, etc.
Some of those relationships will be abstract.
Nothing in the script itself actually causes concrete calculation (on ground data) to
take place as a direct result of interpreting it; rather, it establishes
the sorts of computations that would have to take place were such a value to
be requested/required in the later phase of actual-evaluation.

The vision is you have one script which collectively tells the shape of all
sorts of reports and then a DSL driver follows that script to interact with
one or more "data providers" (plug-ins) for whatever actual data is relevant
given the parameters of an invocation.

#### How to Build a DSL:
First, write stuff in the language you wish you had. Then, write down the
grammar for this language. Use trial-parse methods to figure out what does
and does not parse, adjusting each as you go according to your aesthetic.
Build a driver that generates suitable preliminary semantic values: these
summarize parse trees. In the simple case, these are directly interpretable.
But first perform whatever ahead-of-time validation -- possibly in the act
of transmogrifying the abstract-parse into the next closer-to-executable
representation. At some point, you get close enough to the bare metal for
your purpose: execute THIS.

#### Some relavant types:
* Classical Scalars: color, string, atom, number, date
* Inclusive and Exclusive Ranges (on either end)
* Domain-specific Discrete Enumerations:
	* Static Hierarchies: (a.k.a. "breakdown structures" or "enumerations")
		* Physical Scope: branch, city, state, region.
		* Activity: discipline/type(e.g. eng/supt)/kind(e.g. Office/Field/Craft)
		* Organization: Home-Office/Support-Office/Field-Site.
	* Boundless Ordered Hierarchies:
		* Time: week, half-month, month, quarter, year.
		* There could be others.
* Heterogenous Structures:
	* This is likely to be the theoretical outline of many time-series.
	* You have different buckets, each with different sub-structure.
* Allocation Trees:
	* You have X skill points. Assign them to attributes. Do try to balance!
#### Some examples from the real world:
