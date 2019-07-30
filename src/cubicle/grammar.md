# Project Cubicle
This is the actual syntax and grammar specification for the domain-specific language (DSL)
upon which *Project Cubicle* is founded. This exact document (yes, the one you are looking at
as you read these words) gets passed through [booze-tools](https://github.com/kjosib/booze-tools)
to generate the scanner and parser for this little domain-specific language. A fabulous consequence
is that the documentation is guaranteed to be in sync with the actual DSL.

## How to Read this Document:
Each section header concerns a different grammatical topic. The
informative text is in the ordinary presentation, while the formal
defining elements are within "code-block" sections.

Unlike typical inputs to parser/scanner generator tools, there is
no actual host-language code in this definition document. Instead,
it uses symbolic messages like `:this`. The code to process
those messages is in a separate *driver* module which (in principle)
could be written in *any* programming language. Therefore,
you can ignore such message symbols unless you're hacking on the
language engine itself.

I believe this interface boundary yields a superior experience in
the long run: the documentation is the code (rather than the reverse),
and the same defining document can be put to many purposes.

# Productions: module
This section explains the phrase structure of the DSL by means of
*production rules* written in an extended variant of BNF.
To make this section a bit easier to read, here's a style guide:

* Non-terminal grammar symbols will be in lower case.
* Terminal symbols will be in UPPER CASE.
* Reserved keywords appear as themselves.

In *Cubicle*, a `module` is a set of top-level declarations, each on a line.
You can think of it as the body of an outermost namespace. The
following grammar rule expresses that concept (and attaches a
parse action called `namespace`, but you can ignore that bit).
```
module -> lines_of(toplevel) :namespace
```
This form of grammar specification allows macros. `lines_of(...)`
will be defined later. Meanwhile, let's see what a top-level declaration
looks like:
```
toplevel -> ID [namespace field named_style grid]
```
This means that a top-level declaration consists of a name (`ID`)
paired with one of several kinds of object given within the square
brackets.

Without further ado, here are the rules for the top-level objects:
```
namespace -> NAMESPACE '[' .module ']' 

named_style -> STYLE .style

grid -> GRID .reference .reference :grid
```
Ignore the dots sprinkled into the production rules. They control the parse engine.
Let's continue:
```
field -> FRAME .optional(axis) .style .block_of(frame_item) :frame
       | TREE .axis ._ :tree
       | MENU .optional(axis) .style .block_of(proper_field) :menu
       | .optional(template) .optional(hint) .style :leaf
       | LIKE .reference .optional(hint) .style :likeness
```
For brevity's sake, the head of a production rule may be abbreviated by the underscore character.
```
reference -> ID | QUAL_ID

proper_field -> ID field
frame_item -> proper_field
    | .template .optional(hint) .style :mezzanine
    | .optional(ID) HEAD .optional(template) .optional(hint) .style  :semantic_header
    | .optional(ID) GAP .optional(template) .style :overt_gap


style -> .list([assignment FLAG STYLE_REF])
assignment -> .ATTRIBUTE '=' .[ID INTEGER DECIMAL COLOR STRING] :assignment

hint -> [ function formula ] optional(priority)
function -> .FUNC_REF '(' .list(reference) ')' :function
formula -> BEGIN_FORMULA .list(formula_element) END_FORMULA :formula
priority -> '@' .[INTEGER DECIMAL]

axis -> .ID :ground_axis | .COMPUTED :computed_axis

template -> BEGIN_TEMPLATE .list(ELEMENT) END_TEMPLATE

``` 
So about those macros: Here's the definition
of the `lines_of(something)` macro in terms of `something` and a terminal
symbol `NL`, which the lexical analyzer will emit whenever it reads a *newline*:
```
lines_of(something) -> :empty
    | ._ NL
    | ._ .something NL :append
```
Here are the remaining macros:
```
block_of(what) -> '[' .semilist(what) ']'
	| '[' NL  .lines_of(what) ']'
	| '[' ']' :empty

optional(x) -> x | :none
list(x) -> :empty | list(x) x :append
semilist(what) -> .what :first | ._ ';' .what :append
```

# Definitions
Typical rules for what's an identifier: it must start with a letter,
and then may contain letters, digits, and underscores.

There is an exception: the single underscore may name a *default*
field within a `frame`. That field would be selected for entering
data when an ordinal is not supplied for the frame's axis.

A dot-separated sequence of identifiers makes a *qualified* identifier.
Such things are valid in certain contexts. Spaces may not appear amid
the portions of a qualified identifier.

These two patterns are given first as common-pattern definitions because
there are numerous lexical rules which recognize them prefixed by
various *sigils*, which basically inflect them into different *parts
of speech*.
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
\[{id}\]             :simple_replacement
\[{id}\.{id}\]       :formatted_replacement
\\/{upper}           :embedded_newline
\\[abtnvfr]          :letter_escape
\\[[\\"]             :reference TEXT
"                    :end TEMPLATE
```
