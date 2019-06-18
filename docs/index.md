# Disorganized Documentation


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
