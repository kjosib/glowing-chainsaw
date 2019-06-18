# Presentation Module

In concept, you:
* Name and define optional bits like formats, parametric SQL queries, etc.
	* Obviously this means there's a symbol table. It has to understand scopes.
	* Atoms are only meaningful in context, and sigils can influence context.
	* Need a way to bind in a SQL engine, annotate queries, etc.
	* Might want to provide bindings for other embedded sub-languages.
	* Best to use a proper embedding hyper-language, perhaps inspired by &lt;?PHP ?&gt;
* Name and define axes:
	* repeating substructure.
	* headings.
	* data formats.
	* outlining.
	* routing (i.e. determining which group an individual belongs to) -- which probably
		involves other bindings provided at environment set-up time.
	* standard functions like sum, count, subtotal, etc (using a cool sub-language which
		knows its own strengths and weaknesses).
* Name and define grids. These:
	* reflect particular horizontal, vertical, and perhaps third axes. (3-D has two ways...)
	* call forth data (from named sources) into appropriately designated spaces within
		the broader scope of the grid.
	* Assign formulas, formatting, and labels to more selected bits of the grid which only
		make sense limiting by both axes at once.
	* The innards probably can be seen as like AWK on crack and mixed with CSS: selectors
		tell what's affected while the remainder of a line says what to do with the affected
		bits of the graph. Selectors inside functions are relative to the semantic position
		of each affected cell, but may be annotated to create absolute cell referces... 

So the host can decide to plot a graph at a given place, perhaps providing data streams
for the named parameters. Afterwards, it might reasonably want dimensional data on
different parts of the plotted grid: this facilitates not only setting up print
parameters, but also tracking down data ranges for configuring charts.


