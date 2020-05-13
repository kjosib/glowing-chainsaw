# Project Cubicle:
The project goal is a high-level declarative domain-specific language for high-functioning, professional-looking,
business-oriented numerical and graphical reporting, meant to interface with Python.

A somewhat more [detailed introduction](docs/introduction.md) is available.
So is a bit of history and a roadmap.

## What's working so far?

Start with the [chess statistics example](examples/core_chess.py) for the
quick dunk in the deep end.

There's a functioning [parser](src/cubicle/frontend.py) for a usable
subset of the intended language. The current working version of the
[grammar](src/cubicle/core.md) is rather terse.

A [middle-end](src/cubicle/middle.py) translates from [AST](src/cubicle/AST.py)
nodes to [static](src/cubicle/static.py) structures using a tree-walking
approach.

The [dynamic](src/cubicle/dynamic.py) sub-module may be thought of as the
report generator back-end, but really it's the run-time support module
for interpreting the static structures *in light of* the data that you
feed to a particular report instance.

## What's this about then?
Report generators are funny things. They combine data, organization, structure, calculation, and
attractively-styled presentation. It's entirely possible to do this from first principles each time,
perhaps atop a library like `xlsxwriter`, but when you find yourself making a stream of incremental
changes, it's easy to get frustrated. I did. I got sick and tired of writing essentially the same
`$deity`-forsaken program over and over again: this time with three nested loops, that time with four;
this time with bold sums, that time with outlining; this row should show cents; that column percents.
And then everything changes because the boss wants another column wedged into the middle. 

Functional and data abstraction were not the problem here: modern scripting languages like Python
give you plenty. Rather, it is simply the case that their syntax is a bad fit to the structure of
the problem: everything is equally possible, but very few things are even remotely desirable.

In the shower one day, I decided to build a domain-specific language for expressing all the structure,
organization, boilerplate, and formatting of a report. And then I did some digging around.
It turns out the world is better off if I put this code under a liberal open-source license
and do all my development on my own time with my own resources. Who knows? Maybe it leads to something.

## If I want to play with this, what else do I need?

The [booze-tools](https://github.com/kjosib/booze-tools) module converts such definitions
to a table-driven parser. (For now, I recommend getting the version directly off GitHub,
because this project is a sort of adolescence for that one, and the version on PyPI may
not be in sync.)

You should have some sort of business or statistical data that naturally falls
into particular aggregations, categories, hierarchies, and the like. As a stand-in,
I'm currently using a [chess data table on kaggle.com](https://www.kaggle.com/datasnaek/chess)
which by permission appears at [resources](resources). It's is sort of OK, but some
analogue of the classic "Northwind Traders" database would be a really amazing
resource to add.

## Roadmap: What's to do next?

Right now the major deficiency vs. how the
[back-end driver example](examples/backend.py)
used to work is merge-ranges, so that's pretty high on the priority list.
It ties in closely with patch labels and patch formulas. (Patch styles
already work.)

In support of charting facilities, I might begin by making sure a once
plotted `Canvas` object can report the extent of some selection. This
way at least other code can probe the final layout.

I've an idea to make a variation on the `Tree` shape which acts as a
proper *span* in some sort of consecutively enumerated range like months
or weeks. The notion is that your source data might be missing some intervals
and you still want the output report to include them all, just with zeros.
It just needs a reasonable way to interface that requirement back to the
application-provided "runtime environment" object.

It may be worthwhile to add a charting sub-language.

Then it will be time to find and add any important missing capabilities to
the language. That would require some more real-world use cases. I need to
harvest some good ideas from somewhere. Did I mention a copy of
something like Northwind would be really awesome? Hey I just noticed that
[Microsoft put it on GITHUB](https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/northwind-pubs)
with the [MIT license](https://github.com/microsoft/sql-server-samples/blob/master/license.txt)!
I guess I'll see about porting that to SQLite.