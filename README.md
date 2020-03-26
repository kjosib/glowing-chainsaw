# Project Cubicle:
The project goal is a high-level declarative domain-specific language for high-functioning, professional-looking,
business-oriented numerical and graphical reporting, meant to interface with Python.

## What's this about then?
Report generators are funny things. They combine data, organization, structure, calculation, and
attractively-styled presentation. It's entirely possible to do this from first principles each time,
perhaps atop a library like `xlsxwriter`, but when you find yourself making a stream of incremental
changes, it's easy to get frustrated. I did. I got sick and tired of writing essentially the same
deity-forsaken program over and over again: this time with three nested loops, that time with four;
this time with bold sums, that time with outlining; this row should show cents; that column percents. 

Functional and data abstraction were not the problem here: modern scripting languages like Python
give you plenty. Rather, it is simply the case that their syntax is a bad fit to the structure of
the problem: everything is equally possible, but very few things are even remotely desirable.

In the shower one day, I decided to build a domain-specific language for expressing all the structure,
organization, boilerplate, and formatting of a report. And then I did some digging around.
It turns out the world is better off if I put this code under a liberal open-source license
and do all my development on my own time with my own resources. Who knows? Maybe it leads to something.

## What's working so far?

Not enough to write home about yet. I've learned several ways NOT to do this, though...

## What's the development history?

I initially started with a top-down-design exploration of issues -- a [spike solution](src/spike_solution)
or so I thought at the time. It was all "simplest-things-that-might-work" but it
didn't all work together at the same time. So I set it aside for a while and did some thinking.

A smaller [core grammar](src/cubicle/core_grammar.md) was another tack: a
bottom-up design effort trying to respect the 80/20 rule. I wanted to get
experience with a less-ambitious design. Some good came of it:
I factored out what might be called a "back-end" and built a [demo](examples/backend.py)
which worked by "manually" constructing the data structures I imagined the
`cubicle` translator would build from vastly-more-concise syntax. That part
functioned perfectly, using the Chess data as a suitable example. But then
I set about building the translator. I got part way, but then set things aside
for three months due to higher priorities. It's not finished, and I may scrap that part too.

## If I want to play with this, what else do I need?

The [booze-tools](https://github.com/kjosib/booze-tools) module converts such definitions
to a table-driven parser. (For now, I recommend getting the version directly off GitHub,
because this project is a sort of adolescence for that one, and the version on PyPI may
not be in sync, especially with respect to how error reporting happens.)

You should have some sort of business or statistical data that naturally falls
into particular aggregations, categories, hierarchies, and the like. As a stand-in,
I'm currently using a [chess data table on kaggle.com](https://www.kaggle.com/datasnaek/chess)
which by permission appears at [resources](resources). It's is sort of OK, but some
analogue of the classic "Northwind Traders" database would be a really amazing
resource to add.

## Roadmap: What's to do next?

After building and probably scrapping two versions, there are certain bits they
have in common which should be factored into a sort of "settled canon" module:

* The back-end type stuff would make sense here, because it works. But see later...
* There are some utility functions involving pickles that should be extracted.
* The two grammar definitions have a great deal in common, especially concerning
the lexer and scan procedures. `MacroParse` supports having a separate scan and
parse documents, so that's part of the approach.

I've recently had a brainwave about how to implement [Visitor Pattern](https://en.wikipedia.org/wiki/Visitor_pattern)
most auspiciously in Python. Since this package deals so heavily with tree-like
structures, I figured the concept would clean up some bad code smells.

It turns out to feel WAY more organized: things that logically belong
together, are actually together. Mutual recursion is no longer
scattered all over a class hierarchy.
The [static.py](src/cubicle/static.py) definitions can just be about
the actual static-structure of a -- well --- "class of reports" (analogous to
how a computer-program represents actually a "class of computations"), while
[dynamic.py](src/cubicle/dynamic.py) gets a set of `Visitor` subclasses,
each one of which is responsible for a specific analysis or traversal for
a particular instance-report, filled with particular input-data.
At least, that's where this is going.
It's a process.
The `ShapeDefinition` hierarchy has mostly been tamed. Text templates and
formulas still need to be converted.

One thing I dislike about the "core grammar" is that it's designed around
stateful parsing. I did that, not because of any difficulty building passes
over an AST, but that the relevant code quickly got spread all over the place.
I got absolutely zero support from Python to do it in the textbook manner:
Java or C++ would tell me if I'd left out a method somewhere, or gotten the
parameters wrong. But this is why the above-mentioned visitor-pattern brainwave
should help -- or so I think. So anyway, I plan to adjust the grammar again:
it needs to be illustrative and informative, not merely workable.