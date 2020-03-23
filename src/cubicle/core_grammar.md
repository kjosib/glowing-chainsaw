# Core-Cubicle

This document is both a formal reference to the *core-cubicle* domain-specific
language and the input specification from which the parser is built.
(See project [booze-tools](https://github.com/kjosib/booze-tools) for how that works.)

I'll start with a lexical scanner definition and then move on to phrase structure.

Incidentally, *core-cubicle* has certain "define-before-use" features. This is because,
principally to avoid sending myself insane, it mostly tries to work in a single pass.

# Definitions
This is the part where regular common sub-expressions are defined. For now, I have only two.
```
name    \l\w*
sign    [-+]?
```

# Conditions
Basically, certain of the lexical start-conditions share some definitions
for the patterns that define certain kinds of `Names`. It is better to use inclusion than copies.
The MacroParse grammar definition format optionally expresses inclusion all in one place, in a
`Conditions` section.

Since this grammar uses that MacroParse feature at all, then every valid start-condition must
at least be mentioned in this section, even if it does no inclusion. (It's redundant, but all
good language has redundancy in various forms as defense against miscommunication.)
```
INITIAL -> Names
TEMPLATE
FORMULA
REPLACEMENT -> Names
SELECTION -> Names
```

# Patterns: Names
As explained above, in the `Conditions` section...
```
_         :token UNDERLINE
{name}    :token BARE_NAME
_{name}   :token GENSYM_NAME
&{name}   :sigil MAGIC_NAME
```

# Patterns: INITIAL
This extends the `Names` pattern group.
(Side note: Perhaps I should adjust the MacroParse language to move that
fact *here* rather than *there*?)
```
@{name}           :sigil FUNCTION_NAME
%{name}           :sigil STYLE_NAME
\.{name}          :sigil FORMAT_ATTRIBUTE
!{name}           :sigil OUTLINE_ATTRIBUTE
:\l+              :keyword
#{xdigit}{6}      :token COLOR
"                 :enter TEMPLATE
@'                :enter FORMULA
'[^'{vertical}]*' :delimited STRING
{sign}\d+               :integer
{sign}\d+\.\d+          :decimal
${sign}{xdigit}+        :hex_integer
--.*              :ignore
{horizontal}+     :ignore
{vertical}+       :token NL
{punct}           :punctuation
```

At about this point, I should mention that the `:enter FOO` and `:leave FOO` scanner-messages
must both operate a condition stack in the obvious method and also yield corresponding
tokens for the context-free portion of the language definition (which is given later,
under `Productions`).

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
Don't forget this extends the `Names` pattern group.
```
->        :token ARROW
]         :leave REPLACEMENT
{punct}   :punctuation
```

# Patterns: FORMULA
In certain contexts an arbitrary formula may appear. There's a slightly different semantic from
a text-template, and the embedded references work a bit differently. Also, you can have embedded
double-quoted things, which behave (syntactically and semantically) like templates. I don't otherwise
bother about character escapes because outside strings they won't be valid Excel formulae anyway.
```
[^['"{vertical}]+  :token CODE
'                  :leave FORMULA
"                  :enter TEMPLATE
\[                 :enter SELECTION
```

# Patterns: SELECTION
This is a best-guess for now. It also extends the `Names` pattern group.
```
]      :leave SELECTION
[=|;*]  :punctuation
```

# Productions: core_module
Here begins the context-free portion of the grammar.
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
OK OK I'll explain: they indicate significant symbols where only some of the symbols in
a right-hand side should be fed into the reduction message. And frankly I think that
problem should be solved a different way. There's a `booze-tools` issue #23 about this.

For brevity's sake, the head of a production rule may be abbreviated by the
underscore (`_`) character, thus simple recursion.

Let's continue:
```
toplevel -> .BARE_NAME STYLE .list(attribute)   :define_style
          | .BARE_NAME LEAF .marginalia         :define_leaf
          | .BARE_NAME .shape_def               :define_shape
          | canvas_decl canvas_body
```
At the top-level, you can define:
* Styles, which are named groups of formatting attributes you can use just about
anywhere a formatting attribute is called for,
* Primary axis definitions, which are either `leaf` or composite types.
* Canvases, which are particular report-grid layouts: these associated
```
attribute -> .FORMAT_ATTRIBUTE '=' .value   :assign_attribute
           | .FORMAT_ATTRIBUTE flag         :assign_attribute
           | .STYLE_NAME                    :style_reference

value -> number | BARE_NAME | COLOR | STRING
number -> INTEGER | DECIMAL
flag -> '+' :true  | '-' :false

marginalia -> .texts .optional(hint) margin_style :marginalia

texts -> :none
       | template   :singleton
       | '(' .list([template function formula]) ')'

margin_style ->   :begin_margin_style
  | ._ attribute
  | ._ outline

outline -> OUTLINE_ATTRIBUTE flag  :assign_outline
    | .OUTLINE_ATTRIBUTE '=' .number :assign_outline
     

shape_def -> marginalia :leaf
           | .marginalia FRAME .reader .block_of(menu_item) :record
           | .marginalia FRAME .GENSYM_NAME .block_of(frame_item) :frame
           | .marginalia TREE .reader  ._ :tree
           | .marginalia MENU .reader .block_of(menu_item) :menu
           | USE .BARE_NAME :named_shape

canvas_decl -> .BARE_NAME CANVAS .BARE_NAME .BARE_NAME :declare_canvas
canvas_body -> block_of(canvas_item) :end_canvas

reader -> BARE_NAME  :normal_reader
        | MAGIC_NAME :magic_reader

menu_item -> BARE_NAME shape_def

frame_item -> BARE_NAME shape_def
            | UNDERLINE shape_def
            | GENSYM_NAME shape_def

hint -> [ function formula ] optional(priority)
    | GAP :gap_hint
    | HEAD .INTEGER

function -> FUNCTION_NAME list(selector) :function
formula -> BEGIN_FORMULA .list(formula_element) END_FORMULA :formula
priority -> '@' .[INTEGER DECIMAL]

template -> STRING :simple_string_template
  | BEGIN_TEMPLATE .list(ELEMENT) END_TEMPLATE :template

selector -> '{' .semilist(selection_item) '}' :selector
selection_item -> .axis '=' .BARE_NAME :select_one
                | .axis '=' .set :select_set
axis -> BARE_NAME | MAGIC_NAME | GENSYM_NAME
set -> .BARE_NAME '|' .BARE_NAME :set_of_two
     | .set '|' .BARE_NAME :add_set

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
semilist(what) -> .what :singleton | ._ ';' .what :append
```

