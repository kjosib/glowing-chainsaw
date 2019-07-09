# Project Cubicle
This is the actual syntax and grammar specification for the domain-specific language (DSL)
upon which *Project Cubicle* is founded.

# Productions: module

Basically, a cubicle module is a set of declarations. They all assign names to various sorts of objects.
Many of those objects have various attributes, and there is a certain amount of block-structure to the DSL.

To make this stuff a tad bit easier to read, here's a rule: nonterminals will be in lower-case. Wherever
a nonterminal and a terminal share the same name (modulo case) the nonterminal is the definition, and the
corresponding terminal is the reference. A reference will search surrounding lexical scopes as needed.

```
block(of) -> '[' .semilist(of) ']'
	| '[' NL  .lines(of) ']'
	| '[' ']' :empty

opt(x) -> x | :none
list(x) -> :empty | list(x) x :append
semilist(of) -> .of :first | ._ ';' .of :append
lines(of) -> :empty | ._ NL | ._ .of NL :append
decl(of) -> .ID .of

module -> lines(decl([namespace field style])) :namespace

namespace -> NAMESPACE '[' .module ']' 

field_layout -> .block(layout_item)
layout_item -> .ID .field   :layout_field
	| GAP .list(attr)       :layout_gap
	| .template .attributes :layout_heading

field -> FRAME .attributes .field_layout :frame
field -> TREE .axis_reader ._ :tree
field -> MENU .opt(axis_reader) .list(attr) .block(decl(field)) :menu
field -> .opt(template) .attributes :leaf
field -> LIKE .[ID QUAL_ID] .attributes :likeness

style -> STYLE .attributes

attributes -> .opt(hint) .opt(priority) .list(attr) :heritable
attr -> FLAG
	| .ATTRIBUTE '=' .[ID INTEGER DECIMAL COLOR STRING] :attribute
	| STYLE_REF

priority -> '@' .[INTEGER DECIMAL]

hint -> .FUNC_REF '(' .list([ID QUAL_ID]) ')' :function_hint
	| BEGIN_FORMULA .list(formula_element) END_FORMULA :formula_hint

axis_reader -> .ID :ground_reader | .COMPUTED :computed_reader

template -> BEGIN_TEMPLATE .list(template_element) END_TEMPLATE
template_element -> TEXT :literal | REPL

```

# Definitions
```
id        \l\w*|_
qualid    {id}(\.{id})+
```

# Patterns: INITIAL
```
{id}            :ident
{qualid}        :qualident
:\l+            :keyword
#{xdigit}{6}    :match COLOR
[.!&]{id}       :attribute
[.!&][-+]{id}   :flag
%{id}           :reference STYLE_REF
%{qualid}       :qref STYLE_REF
@{id}           :reference FUNC_REF
${id}           :reference COMPUTED
"               :begin TEMPLATE
@'              :begin FORMULA
'[^'{vertical}]*' :string 
\d+             :integer
\d+\.\d+        :decimal
->              :token ARROW
--.*            :ignore
{horizontal}+   :ignore
{vertical}+     :token NL
{punct}         :punctuation

```
Attributes/flags prefixed by `.` apply to all affected rows/columns. Those
prefixed by `!` apply only to header areas.

# Patterns: TEMPLATE
A string template is surrounded by double-quotes. It may contain literal text and
domain references (themselves within square brackets). The usual backslash-escaping
rules apply, except that a backslash before any upper-case letter becomes a newline.
A string template may not span lines.
```
[^[\\"{vertical}]+   :literal_text
\[{id}\]             :replacement
\\/{upper}           :embedded_newline
\\[abtnvfr]          :letter_escape
\\[[\\"]             :reference TEXT
"                    :end TEMPLATE
```
