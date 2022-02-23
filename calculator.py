#!/usr/bin/env python

import pprint

from dsp import Recipes


recipes = Recipes()
pp = pprint.PrettyPrinter(indent=4)

pp.pprint(recipes.get_tree('Hydrogen', include_raw=True))
