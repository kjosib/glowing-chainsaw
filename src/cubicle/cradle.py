"""
The "cradle" is where things get started. Not the simplest thing that might work,
but the simplest thing that does any work whatsoever.
"""
import os
from boozetools import foundation
from boozetools.macroparse import compiler

print(open(os.path.join(os.path.split(__file__)[0], 'grammar.md')).read())
