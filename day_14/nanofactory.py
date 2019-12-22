import re
from typing import Dict

import attr


@attr.s
class Recipe:
    output: str = attr.ib()
    quantities: int = attr.ib()
    inputs: Dict[str, int] = attr.ib(default=attr.Factory(dict))

    @classmethod
    def load_from_line(cls, line: str) -> "Recipe":
        input_str, output_str = line.split('=>')
        ingredient = re.compile(r'(\d+) (\w+)')

        found_outputs = ingredient.search(output_str).groups()
        recipe = cls(found_outputs[1], int(found_outputs[0]))
        for elem in input_str.split(','):
            found_input = ingredient.search(elem).groups()
            recipe.inputs[found_input[1]] = int(found_input[0])

        return recipe

    def __str__(self):
        inputs = []
        for name in sorted(self.inputs.keys()):
            inputs.append(f'{self.inputs[name]} {name}')
        return f'{", ".join(inputs)} => {self.quantities} {self.output}'


class ForbiddenMining(RuntimeError):
    pass


@attr.s
class NanoFactory:
    recipes: Dict[str, Recipe] = attr.ib(default=attr.Factory(dict))
    storage: Dict[str, int] = attr.ib(default=attr.Factory(dict))
    _mined_ore: int = attr.ib(default=0)

    @classmethod
    def from_file(cls, filename: str) -> "NanoFactory":
        nano_factory = cls()
        with open(filename) as f:
            for line in f:
                recipe = Recipe.load_from_line(line)
                if recipe.output in nano_factory.recipes:
                    raise RuntimeError(f'Several recipes for {recipe.output}')
                nano_factory.recipes[recipe.output] = recipe

        return nano_factory

    @property
    def mined_ore(self) -> int:
        return self._mined_ore

    def _mine_ore(self, quantities: int = 1):
        self._mined_ore += quantities
        self._store('ORE', quantities)

    def _store(self, element: str, quantities: int):
        if element not in self.storage:
            self.storage[element] = quantities
        else:
            self.storage[element] += quantities

    def produce(self, element: str, quantities: int, allow_mining: bool) -> None:
        if element == 'ORE':
            self._mine_ore(quantities)
            return
        if element not in self.recipes:
            raise RuntimeError(f'Unknown element {element}')

        if element not in self.storage:
            self.storage[element] = 0

        recipe = self.recipes[element]
        while self.storage[element] < quantities:
            # Apply the recipe
            print(f'Applying {recipe}')
            for input_elem, input_qte in recipe.inputs.items():
                # print(f' - need {input_qte} {input_elem} (store={self.storage.get(input_elem)})')
                if self.storage.get(input_elem, 0) < input_qte:
                    if input_elem == 'ORE':
                        if allow_mining:
                            self._mine_ore(input_qte)
                            # print(f' => Mined {input_qte} ORE')
                        else:
                            raise ForbiddenMining(f'When applying {recipe}')
                    else:
                        self.produce(input_elem, input_qte, allow_mining)
                # else:
                #     print(f'  => Consuming {input_qte} {input_elem} ({self.storage[input_elem]} left)')
                self.storage[input_elem] -= input_qte
            self._store(recipe.output, recipe.quantities)
        # print(f'== Storage {self.storage} ==')

    def _mass_produce(self, element: str, quantities: int):
        if element == 'ORE':
            self._mine_ore(quantities)
            return
        if element not in self.recipes:
            raise RuntimeError(f'Unknown element {element}')

        if element not in self.storage:
            self.storage[element] = 0

        recipe = self.recipes[element]
        apply = quantities // recipe.quantities
        if quantities % recipe.quantities:
            apply += 1

        # Apply the recipe several times
        print(f'Applying {apply}x({recipe}) ')

        for input_elem, input_qte in recipe.inputs.items():
            in_store = self.storage.get(input_elem, 0)
            consume = apply * input_qte
            # print(f' - need {consume} {input_elem} (in_store={in_store}) for {recipe}')

            if in_store < consume:
                if input_elem == 'ORE':
                    raise ForbiddenMining(f'Needed for {apply}x({recipe})')
                else:
                    self._mass_produce(input_elem, consume)

            # print(f'-- Consuming {consume} {input_elem} --')
            self.storage[input_elem] -= consume

        self._store(recipe.output, apply * recipe.quantities)
        # print(f'== Storage {self.storage} == produced {apply * recipe.quantities} {recipe.output}')

    def mass_produce(self, elem: str, ore_per_elem: int) -> int:
        # Brute force mass produce is very slow.
        mass = self.storage['ORE'] // ore_per_elem
        while mass > 5:
            try:
                self._mass_produce(elem, mass)
                mass = self.storage['ORE'] // ore_per_elem
            except ForbiddenMining:
                print(f'Mass produce {self.storage[elem]} {elem} (ore per elem is {ore_per_elem})')
                break

        print(f'Storage is now {self.storage}')
        # Once we mass produced we do linear production to finish the reserves.
        i = 0
        while True:
            try:
                self.produce(elem, self.storage[elem] + 1, allow_mining=False)
                i += 1
            except ForbiddenMining:
                print(f'Produced {i} additional {elem}')
                break

        return self.storage[elem]


if __name__ == '__main__':
    nano = NanoFactory.from_file('input.txt')

    print(f'Loaded {len(nano.recipes)} recipes')
    nano.produce('FUEL', 1, allow_mining=True)

    print(f'We need to mine {nano.mined_ore} ORE for 1 FUEL')
    ore_per_fuel = nano.mined_ore

    # Reset the mining and try until mining error
    nano.storage = {
        'ORE': 1000000000000,
    }
    fuel = nano.mass_produce('FUEL', ore_per_fuel)
    print(f'Produced {fuel} FUEL from a trillion ORE')  # 2876992
    print(f'Leftover is {nano.storage}')
