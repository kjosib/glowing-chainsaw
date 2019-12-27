# Core-Cubicle

This document is both a formal reference to the *core-cubicle* domain-specific
language and the input specification from which the parser is built.
(See project [booze-tools](https://github.com/kjosib/booze-tools) for how that works.)

I'll start with a lexical scanner definition and then move on to phrase structure.

Incidentally, *core-cubicle* has certain "define-before-use" features. This is because,
principally to avoid sending myself insane, it mostly tries to work in a single pass.

# Definitions
This is the part where regular common sub-expressions are defined. For now, I have only one.
```
name        \l\w*
```

# Conditions
Basically, the `INITIAL` and `REPLACEMENT` lexical start-conditions share some definitions
for the patterns that define certain kinds of `Names`. It is better to use inclusion than copies.
Since this grammar uses that MacroParse feature at all, then every valid start-condition must at least be
mentioned in this section, even if it does no inclusion. (It's a redundancy, but a valuable one.)
```
INITIAL -> Names
TEMPLATE
FORMULA
REPLACEMENT -> Names
```

# Patterns: Names
As explained above, in the `Conditions` section...
```
_         :token UNDERLINE
{name}    :token BARE_NAME
#{name}   :token GENSYM_NAME
${name}   :sigil MAGIC_NAME
```

# Patterns: INITIAL
```
@{name}           :sigil FUNCTION_NAME
%{name}           :sigil STYLE_NAME
\.{name}          :sigil FORMAT_ATTRIBUTE
&{name}           :sigil OUTLINE_ATTRIBUTE
:\l+              :keyword
#{xdigit}{6}      :token COLOR
"                 :enter TEMPLATE
@'                :enter FORMULA
'[^'{vertical}]*' :delimited STRING
\d+               :integer
\d+\.\d+          :decimal
--.*              :ignore
{horizontal}+     :ignore
{vertical}+       :token NL
{punct}           :punctuation
```

# Patterns: TEMPLATE
A string template is surrounded by double-quotes. It may contain literal text and
domain references (themselves within square brackets). The usual backslash-escaping
rules apply, except that a backslash before any upper-case letter becomes a newline.
A string template may not span lines.
```
[^[\\"{vertical}]+   :token TEXT
\\/{upper}           :embedded_newline
\\[abtnvfr]          :letter_escape
\\\[                 :sigil TEXT
"                    :leave TEMPLATE
\[                   :enter REPLACEMENT
```

# Patterns: REPLACEMENT
```
->        :token ARROW
]         :leave REPLACEMENT
{punct}   :punctuation
```


For now, I'm going to leave undefined how you deal with arbitrary formulas. However, I strongly
suspect they'll work out nicely in the end.

# Productions: core_module
To make this section a bit easier to read, here's a style guide:

* Non-terminal grammar symbols will be in lower case.
* Terminal symbols will be in UPPER CASE.
* Reserved keywords appear as themselves.
* Messages to the parse driver appear after a colon, `:like_this`.
```
core_module -> lines_of(toplevel)
```
This form of grammar specification allows macros.
For example, given polymorphic `:empty` and `:append`
messages, `lines_of(...)` is defined as follows:
```
lines_of(something) -> :empty
    | ._ NL
    | ._ .something NL :append
```
Ignore the dots sprinkled into the production rules. They control the parse engine.
For brevity's sake, the head of a production rule may be abbreviated by the
underscore (`_`) character, thus simple recursion.

Let's continue:
```
toplevel -> .BARE_NAME STYLE .list(attribute)   :define_style
          | .BARE_NAME LEAF .marginalia         :define_leaf
          | .BARE_NAME .shape_def               :define_shape
          | canvas_decl canvas_body

attribute -> .FORMAT_ATTRIBUTE '=' .value   :typical_attribute
           | .STYLE_NAME                    :style_reference
           | .FORMAT_ATTRIBUTE '+'          :true_attribute
           | .FORMAT_ATTRIBUTE '-'          :false_attribute

value -> BARE_NAME | INTEGER | DECIMAL | COLOR | STRING

marginalia -> template_definition 

shape_def -> marginalia :leaf
           | FRAME .reader .marginalia .block_of(frame_item) :frame
           | FRAME .GENSYM_NAME .marginalia .block_of(frame_item) :frame
           | TREE .reader .marginalia OF ._ :tree
           | MENU .reader .marginalia .block_of(menu_item) :menu

canvas_decl -> .BARE_NAME CANVAS .BARE_NAME .BARE_NAME :declare_canvas
canvas_body -> block_of(canvas_item) :end_canvas

reader -> BARE_NAME  :normal_reader
        | MAGIC_NAME :magic_reader

proper_field -> ID field

assignment -> .ATTRIBUTE '=' .[ID INTEGER DECIMAL COLOR STRING] :assignment

hint -> [ function formula ] optional(priority)
function -> .FUNC_REF '(' .list(reference) ')' :function
formula -> BEGIN_FORMULA .list(formula_element) END_FORMULA :formula
priority -> '@' .[INTEGER DECIMAL]

template -> BEGIN_TEMPLATE .list(ELEMENT) END_TEMPLATE

``` 
So about those macros: Here's the definition
of the `lines_of(something)` macro in terms of `something` and a terminal
symbol `NL`, which the lexical analyzer will emit whenever it reads a *newline*:
Here are the remaining macros:
```
block_of(what) -> '[' .semilist(what) ']'
	| '[' NL  .lines_of(what) ']'
	| '[' ']' :empty

optional(x) -> x | :none
list(x) -> :empty | list(x) x :append
semilist(what) -> .what :first | ._ ';' .what :append
```

