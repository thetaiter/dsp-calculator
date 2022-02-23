import sys
import yaml
import pprint

from dataclasses import dataclass

recipe_defaults = {
    'name': None,
    'facility': 'Mining Machine',
    'time': 0,
    'raw': False,
    'inputs': [],
    'outputs': []
}

pp = pprint.PrettyPrinter(indent=4)

@dataclass
class Recipe:
    name: str
    facility: str
    time: int
    raw: bool
    inputs: set[dict]
    outputs: set[dict]


    def __hash__(self):
        return hash(self.name)


    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.name == other.name
        )


    def makes(self, resource):
        return resource in set(output['name'] for output in self.outputs)


    def uses(self, resource):
        return resource in set(input['name'] for input in self.inputs)


class Recipes:
    recipes: set[Recipe]


    def __init__(self, recipe_file='recipes.yaml'):
        self.load(recipe_file)


    def load(self, recipe_file):
        with open(recipe_file, 'r') as recipes_file:
            try:
                self.recipes = set(Recipe(**(recipe_defaults|recipe)) for recipe in yaml.safe_load(recipes_file))
            except yaml.YAMLError as yaml_exception:
                print(f'An exception occurred while attempting to parse {recipe_file}:', file=sys.stderr)
                print(yaml_exception, file=sys.stderr)
                sys.exit(1)


    def that_make(self, resource):
        return set(recipe for recipe in self.recipes if recipe.makes(resource))


    def that_use(self, resource):
        return set(recipe for recipe in self.recipes if recipe.uses(resource))


    def get(self, name):
        return next((recipe for recipe in self.recipes if recipe['name'] == name), None)


    def get_tree(self, resource, include_raw=False):
        if not self.that_make(resource):
            print(f'Error: No recipe found for {resource}', file=sys.stderr)
            return None

        tree = []

        for recipe in self.that_make(resource):
            tree.append(recipe)

            for i in recipe.inputs:
                recipes_that_make_i = self.that_make(i['name'])
                raw = next(r.raw for r in recipes_that_make_i)

                if raw and not include_raw:
                    return tree

                if len(recipes_that_make_i.union(tree)) != len(recipes_that_make_i) + len(tree):
                    return tree

                subtree = self.get_tree(i['name'], include_raw=include_raw)
                
                if subtree and not any(subtree[i] in tree for i, t in enumerate(tree)):
                    tree.extend(subtree)

        return tree
