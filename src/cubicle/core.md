# Core-Cubicle (Mark 3)

After the "spike solution" and a previous attempt, this is the third version of the grammar.

This document is both a formal reference to the *core-cubicle* domain-specific
language and the input specification from which the parser is built.
(See project [booze-tools](https://github.com/kjosib/booze-tools) for how that works.)

I'll start with a lexical scanner definition and then move on to phrase structure.


### Definitions
```
name          \l\w*
sign          [-+]?
backslash     \\
openbracket   \[
```

### Conditions
```
INITIAL -> Names
TEMPLATE
FORMULA
REPLACEMENT -> Names
SELECTION -> Names
```

### Patterns: Names
```
_         :name UNDERLINE
{name}    :name NAME
@{name}   :sigil COMPUTED
~{name}   :sigil ROUTE
```
Note there are certain places the underscore cannot appear syntactically.
### Patterns: INITIAL
This extends the `Names` pattern group.
```
%{name}           :sigil STYLE_NAME
\+{name}          :sigil ACTIVATE
-{name}           :sigil DEACTIVATE
:\l+              :keyword
#{xdigit}{6}      :string COLOR :1
"                 :enter TEMPLATE
@'                :enter FORMULA
'[^'{vertical}]*' :delimited STRING
{sign}\d+               :integer
{sign}\d+\.\d+          :decimal
${sign}{xdigit}+        :hex_integer
#.*               :ignore
{horizontal}+     :ignore
{vertical}\s*     :token NL
{punct}           :punctuation
```
### Patterns: TEMPLATE
A string template is surrounded by double-quotes. It may contain literal text and
domain references (themselves within square brackets). The usual backslash-escaping
rules apply, except that a backslash before any upper-case letter becomes a newline.
A string template may not span lines.
```
[^"{openbracket}{backslash}{vertical}]+    :string TEXT
{backslash}/{upper}                        :embedded_newline
{backslash}[abtnvfr]                       :letter_escape
{backslash}["{openbracket}{backslash}]     :escape_literal
"                                          :leave TEMPLATE
{openbracket}                              :enter REPLACEMENT
```
### Patterns: REPLACEMENT
This extends the `Names` pattern group.
```
->        :token ARROW
]         :leave REPLACEMENT
{punct}   :punctuation
[1-9]\d*  :integer
```
### Patterns: FORMULA
```
[^['"{vertical}]+  :string TEXT
'                  :leave FORMULA
"                  :enter TEMPLATE
{openbracket}      :enter SELECTION
```
### Patterns: SELECTION
This extends the `Names` pattern group.
```
]        :leave SELECTION
{punct}  :punctuation
```

## Precedence:
```
%void AXIS CANVAS FRAME GAP HEAD LEAF MENU MERGE STYLE TREE USE ZONE
%void '=' ',' ';' '.' '!' '[' ']' '(' ')' '{' '}' '^' '@' '|' '*' ':' NL
%void BEGIN_TEMPLATE END_TEMPLATE
%void BEGIN_FORMULA END_FORMULA
%void BEGIN_SELECTION END_SELECTION
%void BEGIN_REPLACEMENT END_REPLACEMENT
```

## Productions: cubicle_module
Here begins the context-free portion of the grammar.
To make this section a bit easier to read, here's a style guide:

* Non-terminal grammar symbols will be in lower case.
* Terminal symbols will be in UPPER CASE.
* Reserved keywords appear as themselves.
* Messages to the parse driver appear after a colon, `:like_this`.
* Dots prepended to symbols in the right-hand sides of production rules
  denote semantic significance in the manner currently supported by the
  parser generator. (The manner may change in a future version.)

```
cubicle_module -> lines_of(toplevel)

toplevel -> NAME STYLE list(attribute)   :define_style
          | NAME LEAF marginalia         :define_shape
          | NAME compound                :define_shape
          | NAME CANVAS NAME NAME list(attribute) block_of(patch) :define_canvas

attribute -> STYLE_NAME | ACTIVATE | DEACTIVATE
           | NAME '=' constant    :assignment

constant -> number | NAME | COLOR | STRING
number -> INTEGER | DECIMAL

marginalia -> texts optional(hint) list(attribute) :marginalia

texts -> :none
       | label   :singleton
       | '(' list([label formula]) ')'

hint -> formula optional(priority)
    | GAP :gap_hint
    | HEAD INTEGER

priority -> '@' number

shape_def -> marginalia | compound | marginalia USE NAME :linkref

compound ->  marginalia FRAME reader block_of(frame_item) :frame
           | marginalia TREE  reader shape_def            :tree
           | marginalia MENU  reader block_of(menu_item)  :menu

reader -> :none | AXIS [NAME COMPUTED]
menu_item -> NAME tag_option shape_def :field
frame_item -> field_name tag_option shape_def :field
field_name = NAME | UNDERLINE

tag_option -> :none | ZONE NAME

label -> STRING :label_constant
  | BEGIN_TEMPLATE list(tpl_element) END_TEMPLATE :label_interpolated

literal -> TEXT :literal_text

tpl_element -> literal
  | BEGIN_REPLACEMENT tpl_replacement END_REPLACEMENT

tpl_replacement -> NAME :tpl_plaintext
  | COMPUTED          :tpl_raw
  | NAME '.' NAME     :tpl_attribute
  | NAME '!' INTEGER  :tpl_head_ref
  | '.' NAME          :tpl_global_ref

formula -> BEGIN_FORMULA list(formula_element) END_FORMULA

formula_element -> literal 
 | BEGIN_SELECTION selector END_SELECTION :magic_sum
 | BEGIN_SELECTION ':' selector END_SELECTION :raw_range
 | label :quote_label

selector -> commalist(criterion)
criterion -> ROUTE | NAME '=' predicate :criterion

predicate -> '*'      :select_each
  | COMPUTED          :select_computed
  | alternatives      :select_set
  | '^' alternatives  :select_not_set

alternatives -> field_name   :singleton
      | _ '|' field_name   :append

patch -> selector '{' content list(attribute) '}'        :patch_plain
       | MERGE selector '{' content list(attribute) '}'  :patch_merge
       | selector block_of(patch)                        :patch_block

content -> :none | label | formula | GAP :blank_cell

``` 
Macro Definitions:
```
lines_of(something) -> :empty
    | _ NL
    | _ something NL :append

block_of(what) -> '[' semilist(what) ']'
	| '[' NL  lines_of(what) ']'
	| '[' ']' :empty

optional(x) -> x | :none

list(x) -> :empty | list(x) x :append

semilist(what) -> what :singleton | _ ';' what :append
commalist(what) -> what :singleton | _ ',' what :append
```

