Template Strings
----------------------------------------------

Cubicle uses :code:`"Double Quotes"` to delimit *template strings*.
They can contain:

Replacement Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^

Inside square brackets, put the name of an axis.

Example:
	:code:`"Subtotal [region] Sales"`

Effect:
	At each cell where the template applies, the substring
	:code:`[region]`
	gets replaced by the applicable value of the
	:code:`region` axis, correctly mapped to plain text
	using the runtime-environment object.

Caveat:
	The mentioned axis is assumed to exist in the address of
	any cell where the template is used. If the example
	template applies to a cell without a :code:`region`,
	it will result in some sort of error condition.

The Future:
	I'd like to expand the syntax of replacement parameters
	to provide more control over how a value gets prepared.
	In particular, I might reasonably want different views
	of the same (Python) object in different parts of the
	same report. Implementing a design is easy enough, but
	coming up with a sufficiently-elegant design is not.

Character Escapes and Line Breaks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The usual C-style *backslash-letter* escape codes (``abtnvfr``) are supported,
although I can't imagine any use for these except for :code:`\n`,
for newline.

The aesthetics of that are dubious at best.

In general:
	You're going to want to break lines between words.
	The first word on the next line will generally be capitalized.
	Doing it with :code:`\n` will be ugly and hard to read,
	especially for nontechnical people who might contribute copy.

	Ugly Example: :code:`"Multi-Line\nTitle Text"`

Therefore:
	Backslash appearing before a capital letter *becomes*
	a line-break, leaving the capital letter intact on the
	subsequent line.

	Less-Ugly Example: :code:`"Multi-Line\Title Text"`

Finally, you can use :code:`\[`, :code:`\\` and :code:`\"`
to represent a literal left-square-bracket, backslash, or
double-quote, respectively.
(Backslash before any other character is considered a syntax error.)

	If you provide a module definition as a triple-quoted string,
	it will be an excellent idea to make that string "raw",
	as in :code:`r"""... \X  ..."""`, to avoid quadruple-backslash heck.

Formula Strings
-------------------------------------------

Begin a formula with :code:`@'` and finish it off with :code:`'`.
Leave out any leading :code:`=`. *Cubicle* will supply
that part for you.

Example:
	:code:`@'if(1+1=2, "Good!", "Oops! Wrong Universe.")'`

Symbolic References
^^^^^^^^^^^^^^^^^^^^^^^^^^

Formulas can contain symbolic cell references, as mentioned in the section
on selectors. There are two types, illustrated by the following two
*equivalent* examples: the :code:`:` just inside the square brackets turns
*off* the automatic summation feature. (Experience has shown sums are the
most common whenever more than one cell is selected here.)

Equivalent Examples:
	| :code:`@'sum([:this=that,that=the_other])'`
	| :code:`@'[this=that,that=the_other]'`

Please note:
	Excel uses double-quotes to delimit literal strings within formulas.

	It therefore makes sense that within *Cubicle* formula strings,
	double-quotes delimit *template strings* which get interpolated
	as such. Why? Because it's useful! Besides, when are you ever going
	to include a cell reference inside a literal string?

Open Issue:
	Currently, discontiguous selectors render as a comma-separated list
	of regular (cell or range) references. That is fine for taking sums,
	but can screw up the use of other formulas. It's not clear whether
	this is an actual problem.
