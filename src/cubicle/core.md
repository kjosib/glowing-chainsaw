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
&{name}   :sigil MAGIC_NAME
```
Note there are certain places the underscore cannot appear syntactically.
### Patterns: INITIAL
This extends the `Names` pattern group.
```
@{name}           :sigil FUNCTION_NAME
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
[^['"{vertical}]+  :string CODE
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
       | template   :singleton
       | '(' .list([template function formula]) ')'

hint -> [ function formula ] optional(priority)
    | GAP :gap_hint
    | HEAD .INTEGER

priority -> '@' .number

shape_def -> marginalia | compound | USE .NAME

compound ->  .marginalia FRAME .reader .block_of(frame_item) :frame
           | .marginalia TREE  .reader .shape_def            :tree
           | .marginalia MENU  .reader .block_of(menu_item)  :menu

reader -> optional(axis)
axis -> NAME | MAGIC_NAME
menu_item -> NAME shape_def :field
frame_item -> menu_item | UNDERLINE shape_def :field

template -> STRING
  | BEGIN_TEMPLATE .list(tpl_element) END_TEMPLATE

tpl_element -> TEXT | BEGIN_REPLACEMENT .tpl_replacement END_REPLACEMENT

tpl_replacement -> axis | .axis '.' .NAME :tpl_axis_attr
  | ._ ARROW .NAME :tpl_cookery


function -> FUNCTION_NAME list(selector) :function

formula -> BEGIN_FORMULA .list(formula_element) END_FORMULA

formula_element -> CODE | selector

selector -> '{' .semilist(selection_item) '}' :selector

selection_item -> .axis '=' .MAGIC_NAME       :select_magic
                | .axis '=' .selection_set    :select_normal
                | .axis '=' '*'               :select_each

selection_set -> .NAME            :singleton
               | ._ '|' .NAME     :append

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

