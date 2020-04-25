# Project Cubicle:
The project goal is a high-level declarative domain-specific language for high-functioning, professional-looking,
business-oriented numerical and graphical reporting, meant to interface with Python.

A somewhat more [detailed introduction](docs/introduction.md) is available.
So is a bit of history and a roadmap.

## What's working so far?

The back-end demonstrates many key capabilities: you can see an
[example](examples/backend.py) of that. I have to warn you,
it's crazy verbose. That's acceptable because ultimately you won't
normally build things that way. It was mainly done to prove the
[static](src/cubicle/static.py) and
[dynamic](src/cubicle/dynamic.py) machinery.

There's a functioning [parser](src/cubicle/frontend.py) for a usable
subset of the intended language. The current working version of the
[grammar](src/cubicle/core.md) is rather terse.

There's a [middle-end](src/cubicle/middle.py) which is getting ever closer
to performing the translation from [AST](src/cubicle/AST.py) to
[static](src/cubicle/static.py) structures. It is where development is
presently most active.

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

I'll continue adding bits to the [middle end](src/cubicle/middle.py) until
the [chess example](examples/core_chess.py) works as well as the
[back-end driver example](examples/backend.py) does.
Then it will be time to see about adding important missing capabilities to
the language. That would require some more real-world use cases. I need to
harvest some good ideas from somewhere. Did I mention a copy of
something like Northwind would be really awesome? Hey I just noticed that
[Microsoft put it on GITHUB](https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/northwind-pubs)
with the [MIT license](https://github.com/microsoft/sql-server-samples/blob/master/license.txt)!
I guess I'll see about porting that to SQLite.