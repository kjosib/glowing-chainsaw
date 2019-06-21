# Project Cubicle
This is the actual syntax and grammar specification for the domain-specific language (DSL)
upon which *Project Cubicle* is founded.

# Productions: module

Basically, a cubicle module is a set of declarations. They all assign names to various sorts of objects.
Many of those objects have various attributes, and there is a certain amount of block-structure to the DSL.

At runtime you want to be able to find stuff. So everything you actually declare shall be
accessible in a big-ol tree structure. Within structures, as you declare them, rules of
lexical scoping apply so that you can easily refer to things but not get confused.

To make this stuff a tad bit easier to read, here's a rule: nonterminals will be in lower-case. Wherever
a nonterminal and a terminal share the same name (modulo case) the nonterminal is the definition, and the
corresponding terminal is the reference. A reference will search surrounding lexical scopes as needed.

```
module -> :empty_module
	| .module .ID .toplevel	:declare

toplevel -> namespace | field | style | form
```
A namespace is just a lexical-scope organizational tool for everything else.
Names naturally reach into surrounding scopes as needed. Shadowing is probably best avoided.
```
namespace -> NAMESPACE '[' .module ']' :namespace
```
A field is one of a few different kinds of object:
```
field -> STRUCT .field_block .decor .with

decor -> :empty_decor
	| .decor .FORMAT '=' .value :assign_format
	| .decor .STYLE 

```
