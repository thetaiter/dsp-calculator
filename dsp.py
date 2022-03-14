import sys
import uuid
import yaml
import pprint

from dataclasses import dataclass
from treelib import Node, Tree


RECIPE_DEFAULTS = {
    'name': None,
    'facility': 'Mining Machine',
    'time': 0,
    'raw': False,
    'inputs': set(),
    'outputs': set()
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
        return hash(self.get_id())

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.get_id() == other.get_id()
        )
    
    def get_id(self):
        if not hasattr(self, '_id') or not isinstance(self._id, uuid.UUID):
            self._id = uuid.uuid4()
        return str(self._id)

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
                self.recipes = set(Recipe(**(RECIPE_DEFAULTS|recipe)) for recipe in yaml.safe_load(recipes_file))
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

    def _generate_tree(self, recipe, include_raw, tree=None, parent=None, resources=None):
        if not tree:
            tree = Tree(identifier=str(uuid.uuid4()))
        
        if not resources:
            resources = set()
        
        for output in recipe.outputs:
            if output['name'] in resources:
                return tree
            else:
                resources.add(output['name'])

        recipe_node_id = str(uuid.uuid4())
        recipe_node = Node(recipe.name, recipe_node_id, data=recipe)
        tree.add_node(recipe_node, parent)

        for i in recipe.inputs:
            recipes_that_make_i = self.that_make(i['name'])
            raw = next((r.raw for r in recipes_that_make_i), None)

            if raw and not include_raw:
                break

            for r in recipes_that_make_i:
                self._generate_tree(r, include_raw, tree, recipe_node_id, resources)
        
        return tree

    def get_trees(self, resource, include_raw=False):
        recipes_that_make_resource = self.that_make(resource)

        if not recipes_that_make_resource:
            print(f'Error: No recipe found for {resource}')
            sys.exit(1)

        trees = set()

        for recipe in recipes_that_make_resource:
            trees.add(self._generate_tree(recipe, include_raw))

        return trees
