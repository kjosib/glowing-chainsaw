# Project Cubicle:

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

## What's working so far?

[Detailed documentation][doc-site] is available, or under development, or either or
neither or both.

[doc-site]: http://cubicle.readthedocs.io

Basically everything in the Minimum Viable Package at least works
passably. However, there are a few rough edges I'd still like to
file smooth.

Start with the [chess statistics example][chess] for the quick dunk in
the deep end.

There's a [functioning parser front end][parser] for a usable
subset of the intended language. The current working version of the
[grammar][grammar] is rather terse.

A [middle-end][middle] translates from [syntax tree][ast]
nodes to [static][static] structures using a tree-walking
approach.

The [dynamic][dynamic] sub-module may be thought of as the
report generator back-end, but really it's the run-time support module
for interpreting the static structures *in light of* the data that you
feed to a particular report instance.

[chess]: https://github.com/kjosib/glowing-chainsaw/tree/master/examples/core_chess.py
[parser]: https://github.com/kjosib/glowing-chainsaw/tree/master/src/cubicle/frontend.py
[grammar]: https://github.com/kjosib/glowing-chainsaw/tree/master/src/cubicle/core.md
[middle]: https://github.com/kjosib/glowing-chainsaw/tree/master/src/cubicle/middle.py
[ast]: https://github.com/kjosib/glowing-chainsaw/tree/master/src/cubicle/AST.py
[static]: https://github.com/kjosib/glowing-chainsaw/tree/master/src/cubicle/static.py
[dynamic]: https://github.com/kjosib/glowing-chainsaw/tree/master/src/cubicle/dynamic.py

## If I want to play with this, what else do I need?

The booze-tools module [on pypi][bt-pypi] or [github][bt-github] converts
the [grammar definition][grammar] to a table-driven parser.

If you install from PyPI, then a suitable version of booze-tools is installed
for you. If you're experimenting with the version of [Cubicle on GitHub][gh],
then I recommend getting [booze-tools from GitHub][bt-github] too,
because this project is a sort of adolescence for that one, and the
[version on PyPI][bt-pypi] may not be in sync.

[gh]: https://github.com/kjosib/glowing-chainsaw
[bt-github]: https://github.com/kjosib/booze-tools
[bt-pypi]: https://pypi.org/project/booze-tools/

You should have some sort of business or statistical data that naturally falls
into particular aggregations, categories, hierarchies, and the like.
As a stand-in, 
I'm currently using a [chess data table on kaggle.com][chess-kaggle]
which by permission appears at [resources][resources]. It's is sort of OK, but some
analogue of the classic "Northwind Traders" database would be a really amazing
resource to add.

[chess-kaggle]: https://www.kaggle.com/datasnaek/chess
[resources]: https://github.com/kjosib/glowing-chainsaw/tree/master/resources

## Roadmap: What's to do next?

Right now the most annoying misfeature has to do with symbolic
range selections in the formulas that appear in the marginalia.
I'd like to exercise greater intelligence about selecting the
intended data range when frames are involved. In particular,
auto-selecting the `_` field should only happen if that frame
is in the *static* context of a formula. This is subtle.

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
[Microsoft put it on GITHUB][northwind] with the [MIT license][mit]!
I guess I might see about porting that to SQLite.

[northwind]: https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/northwind-pubs
[mit]: https://github.com/microsoft/sql-server-samples/blob/master/license.txt
