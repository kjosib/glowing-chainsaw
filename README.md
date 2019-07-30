# Project Cubicle:
This is a declarative domain-specific language for high-functioning, professional-looking,
business-oriented numerical and graphical reporting, meant to interface with Python.

## Say WHAT? Please explain.
I've done a lot of work atop `xlsxwriter`, using spreadsheet workbooks as an output format
for ready-to-print business and financial reports, often with complex and evolving
hierarchical structure and cosmetic requirements. Many contained nontrivial formulas
so the output workbooks can also be used as planning tools starting from a known-clean
base with each run of a report program.

After writing almost-the-same accursed quadruply-nested loop one too many times, I began to
crave a better way. Several blind alleys and partial solutions later, I arrived at this
hairy idea to factor the repeating concepts into a domain-specific language.

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

 