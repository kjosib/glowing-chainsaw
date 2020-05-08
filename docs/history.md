## Project Cubicle: Development History

I initially started with a top-down-design exploration of issues --
a [spike solution](../src/spike_solution)
or so I thought at the time. It was all
"simplest-things-that-might-work" but it
didn't all work together at the same time.
So I set it aside for a while and did some thinking.

A smaller [core grammar](../src/cubicle/old_grammar.md) was another tack: a
bottom-up design effort trying to respect the 80/20 rule. I wanted to get
experience with a less-ambitious design. Some good came of it:
I factored out what might be called a "back-end" and built
a [demo](../examples/backend.py)
which worked by "manually" constructing the data structures I imagined the
`cubicle` translator would build from vastly-more-concise syntax. That part
functioned perfectly, using the Chess data as a suitable example. But then
I set about building the translator. I got part way, but then set things aside
for three months due to higher priorities.

When I got back, I realized the translator's complexity was growing
overwhelming. Let me clarify: I no longer felt like I understood it
all, so there was no possible way this could represent high-quality
maintainable extendable code. If you need to keep 100 things in your
head to work on a system, it's a bad system. (Incidentally, this is
why spreadsheets are bad, but I digress...)

Having built and (mostly) scrapped two versions, I saw there were
certain bits in common. These were factored into a sort of
"settled canon" package:

* Some utility functions just needed to get out of the way because they
were either too well set in stone or else too generic to be worried about.

* The two grammar definitions have a great deal in common, especially concerning
the lexer and scan procedures. `MacroParse` supports having a separate scan and
parse documents, so that's part of the approach.

* Whatever domain-knowledge surrounding `.XLSX` documents (such as what range
of values some formatting attribute may take) is absolutely constant.

One thing I disliked about the "core grammar": it was designed around
stateful parsing. I did that, not because of any difficulty building passes
over an AST, but that the relevant code quickly got spread all over the place.

* Ok, let's face it: **that was** the difficulty in building passes over an AST.)
Java or C++ would tell me if I'd left out a method somewhere, or gotten the
parameters wrong. Python gave me no such support.

After another smaller sabbatical, I had a brainwave about how to implement
[Visitor Pattern](https://en.wikipedia.org/wiki/Visitor_pattern)
most auspiciously in Python. Since this package deals so heavily with tree-like
structures, I figured the concept would clean up some bad code smells.

I started experimenting with this new `Vistor` base-class to clean up
a lot of the chaos inherent in the static-vs-dynamic structure of
report-definition vs. report-instance and.

It turned out to feel WAY more organized: things that logically belong
together (because they do the same sort of thing), actually are together.
Mutual recursion was no longer scattered all over a class hierarchy.
The [static.py](../src/cubicle/static.py) definitions can just be about
the actual static-structure of a -- well --- "class of reports" (analogous to
how a computer-program represents actually a "class of computations"), while
[dynamic.py](../src/cubicle/dynamic.py) gets a set of `Visitor` subclasses,
each one of which is responsible for a specific analysis or traversal for
a particular instance-report, filled with particular input-data.
The `ShapeDefinition` hierarchy has mostly been tamed.

With that pleasant experience, I decided to rebuild the grammar and parser
yet again. The parser *would* build a proper [AST](../src/cubicle/AST.py)
and then there would be a real
[tree-transduction](https://en.wikipedia.org/wiki/Tree_transducer)
built atop the `Vistor` class.



And that's how we get to today.
