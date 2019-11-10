# Project Cubicle:
This is a declarative domain-specific language for high-functioning, professional-looking,
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
I have a lexical and phrase structure [defined](src/cubicle/grammar.md) for an initial
subset of the language focused on structure and formatting.
The [booze-tools](https://github.com/kjosib/booze-tools) module converts that definition
to a table-driven parser. A suitable parse-driver plug-in composes an Abstract Syntax
Tree under direction of the aforementioned table-driven parser. The nontrivial AST nodes
all implement a method called `analyze` which performs semantic checks, connects the dots,
and transmutes the AST into the symbol table.

## Roadmap: What's to do next?
First, it is necessary to carve some module boundaries and make some architectural decisions.

A sample application will catalyze development of some data input and output bindings.
There's a [chess data table on kaggle.com](https://www.kaggle.com/datasnaek/chess) that
should get this off the ground.

 