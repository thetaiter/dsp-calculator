#!/usr/bin/env python

import argparse
from dsp import Recipes


parser = argparse.ArgumentParser(description='Dyson Sphere Program Factory Calculator')
parser.add_argument('resources', metavar='resource', type=str, nargs='+', help='Resource to generate factory tree for')
parser.add_argument('--recipes-file', dest='recipes_file', default='recipes.yaml', help='YAML file containing recipes')
args = parser.parse_args()


def parse_resource_request(resource):
    r = resource
    raw_requested = False
    if resource[-1] == ':':
        r = resource[:-1]
        raw_requested = True
    return r, raw_requested


recipes = Recipes(args.recipes_file)

for resource in args.resources:
    recipe_trees = recipes.get_trees(*parse_resource_request(resource))

    for recipe_tree in recipe_trees:
        recipe_tree.show()
