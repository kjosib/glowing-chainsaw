# Core-Cubicle Mark 3

After the "spike solution" and a previous attempt, this is the third version of the grammar.

### Definitions
```
name    \l\w*
sign    [-+]?
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
&{name}   :sigil COMPUTED
```
Note there are certain places the underscore cannot appear syntactically.
### Patterns: INITIAL
This extends the `Names` pattern group.
```
%{name}           :sigil STYLE_NAME
\+{name}          :sigil ACTIVATE
-{name}           :sigil DEACTIVATE
:\l+              :keyword
#{xdigit}{6}      :string COLOR
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
[^[\\"{vertical}]+   :string TEXT
\\/{upper}           :embedded_newline
\\[abtnvfr]          :letter_escape
\\\[                 :sigil TEXT
"                    :leave TEMPLATE
\[                   :enter REPLACEMENT
```
### Patterns: REPLACEMENT
This extends the `Names` pattern group.
```
->        :token ARROW
]         :leave REPLACEMENT
{punct}   :punctuation
```
### Patterns: FORMULA
```
[^['"{vertical}]+  :string TEXT
'                  :leave FORMULA
"                  :enter TEMPLATE
\[                 :enter SELECTION
```
### Patterns: SELECTION
This extends the `Names` pattern group.
```
]      :leave SELECTION
[=|;*]  :punctuation
```

## Productions: cubicle_module
```
cubicle_module -> lines_of(toplevel)

toplevel -> .NAME STYLE .list(attribute)   :define_style
          | .NAME LEAF .marginalia         :field
          | .NAME .compound                :field
          | .NAME CANVAS .NAME .NAME .block_of(canvas_item) :define_canvas

attribute -> STYLE_NAME | ACTIVATE | DEACTIVATE
           | .NAME '=' .constant    :assignment

constant -> number | NAME | COLOR | STRING
number -> INTEGER | DECIMAL

marginalia -> .texts .optional(hint) .list(attribute) :marginalia

texts -> :none
       | label   :singleton
       | '(' .list([label formula]) ')'

hint -> formula optional(priority)
    | GAP :gap_hint
    | HEAD .INTEGER

priority -> '@' .number

shape_def -> marginalia | compound | USE .NAME

compound ->  .marginalia FRAME .reader .block_of(frame_item) :frame
           | .marginalia TREE  .reader .shape_def            :tree
           | .marginalia MENU  .reader .block_of(menu_item)  :menu

reader -> optional(axis)
axis -> NAME | COMPUTED
menu_item -> NAME shape_def :field
frame_item -> field_name shape_def :field
field_name = NAME | UNDERLINE

label -> STRING :label_constant
  | BEGIN_TEMPLATE .list(tpl_element) END_TEMPLATE :label_interpolated

literal -> TEXT :literal_text

tpl_element -> literal
  | BEGIN_REPLACEMENT .tpl_replacement END_REPLACEMENT

tpl_replacement -> NAME :tpl_plaintext
  | .COMPUTED           :tpl_raw
  | .NAME '.' .NAME     :tpl_attribute


formula -> BEGIN_FORMULA .list(formula_element) END_FORMULA :formula

formula_element -> literal 
 | BEGIN_SELECTION .selector END_SELECTION
 | label :quote_label

selector -> .semilist(criterion)    :selector
criterion -> .NAME '=' .predicate   :criterion

predicate -> '*'      :select_each
  | COMPUTED          :select_computed
  | alternatives      :select_set
  | '^' .alternatives :select_not_set

alternatives -> field_name   :singleton
      | ._ '|' .field_name   :append


``` 
Macro Definitions:
```
lines_of(something) -> :empty
    | ._ NL
    | ._ .something NL :append

block_of(what) -> '[' .semilist(what) ']'
	| '[' NL  .lines_of(what) ']'
	| '[' ']' :empty

optional(x) -> x | :none

list(x) -> :empty | list(x) x :append

semilist(what) -> .what :singleton | ._ ';' .what :append
```

