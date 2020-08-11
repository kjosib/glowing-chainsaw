Styles
-------------------------------------------

All layout elements, canvases, and patch definitions
can be styled with formatting attributes, which are
basically defined by what the *xlsxwriter* module supports.

The language allows you to define and refer back to
named collections of formatting attributes.

Format Attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can use sigils like :code:`+bold` and :code:`-text_wrap` turn on or off boolean
attributes. Other attributes need a specific value.
If that value is a number or *looks like an identifier,* you may
supply it without quotes, as in :code:`align=center`. If the attribute
is a complex string, surround it with single-quotes, as in
this example: :code:`num_format='0.0%;[red]-0.0%'` Finally,
if the attribute is a color, you can use either a predefined name,
like :code:`font_color=green` or a hexadecimal color code,
like :code:`bg_color=#ffcccc`. (At some point support for decimal
RGB colors may be added.)

List of Pre-Defined Colors:
	| black blue brown cyan gray green lime magenta
	| navy orange pink purple red silver white yellow

The exact list of supported attributes is defined in the file
:code:`cubicle/xl_schema.py`, which please see.

	Note on special cases:
		Setting either of the
		properties *border* or *border_color* stands in
		for setting the corresponding attributes on all
		four of *top, bottom, left*, and *right*.


Defining a named style
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To define a style called "example", include a line like:

:code:`example :style +bold +underline align=center`

The pattern is:

#. name of the style
#. keyword :code:`:style`
#. one or more formatting attributes as described in the previous section.
#. newline

Please note: styles can only be defined in the outermost
scope of a module. Attempting it nested inside other structures
will yield a syntax error upon compiling the module.

Referring back to a style
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assuming you've defined a style called "example",
then later on in the module you can refer back to it
with the :code:`%example` sigil wherever formatting
attributes are appropriate, *including in subsequent style
definitions*.

