Language Overview
=====================================

This document lays out the syntax and semantics of the
:code:`cubicle` report specification language.


Overview
----------------------------------------------

The general idea is you define your report "skins" in a
*cubicle* module as described herein, compile that module
to a static data structure (which you may pickle) and then
later, construct reports based on those skins with data you
supply at runtime. Details of those other operations are in
the chapter on integration.

Top-Level Definitions
^^^^^^^^^^^^^^^^^^^^^^^^^

At the outermost (top-level) syntactic level, a cubicle module defines:

* layout structures
	These provide the general structure, format, and boilerplate
	for a report in one direction (either horizontal or vertical)
	or may be used as sub-components in larger layout structures.

* styles
	These provide for naming and re-using particular groups of color,
	font, border, formatting, etc. etc. etc.
	Styles may be used anywhere formatting directives are appropriate.

* canvas definitions
	These describe entire report structures in 2-D. They:

	* refer to horizontal and vertical layout structures,
	* provide global "background" formatting, and
	* provide "patch" boilerplate: things specified
	  in both the horizontal and vertical -- or
	  at any rate things specified to override the
	  default interaction between rows and columns.

Every definition begins with a name (identifier), then a keyword
describing what sort of thing is being defined.

Contributing Components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Within the top-level definitions, certain other things may be defined:

* Subordinate Layout
	Layout structure syntax allows arbitrary in-place nesting, so
	in general things that conceptually go together are lexically
	together in the module file.

* Named Routes
	These abstract over cosmetic details of layout structure.
	They're defined within layout structure, and used within
	both selectors and the API for named reference deep into
	nested layout structures. (Or: They *will* be, when finished.)

* Selectors
	Every place that needs to address a portion of other layout
	uses the same syntax and supports pretty much the same ideas.

* Template Strings
	Anything inside double quotes supports various automagical substitutions.

* Formula Strings
	Formulas in spreadsheets refer to other cells. *Cubicle* abstracts
	out the specific row and column numbers, so formulas can contain
	selectors to pick out the cells you mean, symbolically.

* Patch Instructions
	These take care of all the special exceptional cases in your
	report layouts which cannot be expressed simply as the cross-product
	of horizontal and vertical layout structures.

Tokens or Lexemes
---------------------------------------

The cubicle module language is composed of:

* Keywords
	| All start with a colon and delineate
	  grammatical structures. These are:
	| :code:`:axis` :code:`:canvas` :code:`:frame`
	  :code:`:gap` :code:`:head` :code:`:leaf`
	  :code:`:menu` :code:`:merge` :code:`:path`
	  :code:`:style` :code:`:tree` :code:`:use`
	| Keywords are not case-sensitive.

* Identifiers
	Following the usual programming-language convention,
	these start with a letter and may contain digits and underscores.
	Certain identifiers are special in certain contexts.

* Sigils
	Punctuation marks prefixing an identifier to inflect
  	it with special meaning:

	* :code:`%foo` is a style reference.
	* :code:`@foo` is a computed reference.
	  (You supply a definition at runtime).
	* :code:`+foo` and :code:`-foo` turn on or off boolean
	  formatting elements like bold or underline.
	* :code:`~foo` is a reference to a named route in the layout.

* Integer and Real numbers
	These follow the ordinary conventions for representation.
	In addition, you can supply a hexadecimal integer by
	prefixing it with the :code:`$` sign, as in :code:`$DEADBEEF`.

* Colors
	In addition to the sixteen predefined color names,
	a hash mark followed by six hexadecimal digits,
	like :code:`#feeded` is taken as a color. This rule
	takes precedence over the end-of-line comment rule.

* Comments
	a hash mark (:code:`#`) which is NOT immediately
	followed by six hexadecimal digits is taken as the
	start of a comment, which extends to the end of the
	same line. Comments are ignored, like whitespace.

* Simple strings
	surrounded by single quotes :code:`'like this'`, and which do not
	implement substitution.

* Template strings
	surrounded by double quotes :code:`"like this"`
  	and which interpolate substitution parameters found
	within :code:`[square]` brackets. There's a modicum
	of structure available within such parameters for
	addressing different bits and bobs of information.

* Formula strings
	prefixed by the (:code:`@`) sign and otherwise surrounded
	by single quotes like this example:
	:code:`@'sum([across=_,winner=*,victory=*])'`
	Square brackets delimit reference-replacement parameters.

* Whitespace
	Newlines are significant to the general syntax. Horizontal
	whitespace is taken literally within all kinds of strings.
	In other respects, the amount and type of whitespace is
	ignored except as a a convenient separator between tokens
	which might otherwise be confused. In particular, indentation
	is not significant, but it's good for anyone reading your code.

* Various punctuation and nesting concepts
	Commas, semicolons, curly braces, brackets, and parentheses all
	have their places.


Ideas for the Future
-------------------------------------------

It's entirely possible new features could be added.
If you have a good suggestion, please send it in.
You should be able to contact me through GitHub.


