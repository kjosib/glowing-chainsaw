Cubicle Language Reference
=============================

This document lays out the syntax and semantics of the
:code:`cubicle` report specification language.

(Obviously it isn't finished yet.)

Things you can define in a module
-------------------------------------

A cubicle module definition contains:

* axis layout component definitions
	These provide the general structure, format, and boilerplate
	for a report
	in one direction (either horizontal or vertical)
	or may be used as sub-components in larger layout structures.

* style definitions
	These provide for naming and re-using particular groups of color,
	font, border, formatting, etc. etc. etc.

* canvas definitions
	These describe entire report structures in 2-D. They:

	* refer to horizontal and vertical layout structures,
	* provide global "background" formatting, and
	* provide zone-level boilerplate: things specified
	  in both the horizontal and vertical axis.

Tokens or Lexemes
---------------------------------------

The cubicle module language is composed of:

* Keywords
	All start with a colon and delineate
	gramatical structures. These are:
	:code:`:canvas` :code:`:frame` :code:`:gap`
	:code:`:head` :code:`:leaf` :code:`:of`
	:code:`:menu` :code:`:merge` :code:`:style`
	:code:`:tree` :code:`:use`

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
	within :code:`[square]` brackets.

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

Style Definitions
-------------------------------------------

Layout Definitions
-------------------------------------------

Canvas Definitions
-------------------------------------------


