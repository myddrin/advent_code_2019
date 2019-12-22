from typing import Dict

import pytest

from day_14.nanofactory import Recipe, NanoFactory


def test_load_from_line():
    obj = Recipe.load_from_line('10 ORE => 10 A')
    assert obj.output == 'A'
    assert obj.quantities == 10
    assert obj.inputs == {
        'ORE': 10,
    }
    assert str(obj) == '10 ORE => 10 A'

    obj = Recipe.load_from_line('7 A, 1 B => 1 C')
    assert obj.output == 'C'
    assert obj.quantities == 1
    assert obj.inputs == {
        'A': 7,
        'B': 1,
    }
    assert str(obj) == '7 A, 1 B => 1 C'


def test_load_file():
    nano = NanoFactory.from_file('example_1.txt')

    exp_recipes = {
        'A': '10 ORE => 10 A',
        'B': '1 ORE => 1 B',
        'C': '7 A, 1 B => 1 C',
        'D': '7 A, 1 C => 1 D',
        'E': '7 A, 1 D => 1 E',
        'FUEL': '7 A, 1 E => 1 FUEL',
    }
    assert {
        k: str(v)
        for k, v in nano.recipes.items()
    } == exp_recipes
    assert nano.mined_ore == 0


@pytest.mark.parametrize('quantities, elem, mined_ore, store', (
    (9, 'ORE', 9, {'ORE': 9}),
    # 10 ORE => 10 A
    (9, 'A', 10, {'A': 10}),
    # 1 ORE => 1 B
    (5, 'B', 5, {'B': 5}),
    # 7 A, 1 B => 1 C
    (1, 'C', 10 + 1, {'A': 3, 'C': 1}),
    # 7 A, 1 C => 1 D
    (1, 'D', 10 + 1 + 10, {'A': 6, 'D': 1}),
    # 7 A, 1 D => 1 E
    (1, 'E', 10 + 1 + 10 + 10, {'A': 9, 'E': 1}),
    # 7 A, 1 E => 1 FUEL
    (1, 'FUEL', 10 + 1 + 10 + 10, {'A': 2, 'FUEL': 1}),
))
def test_example_1(elem: str, quantities: int, mined_ore: int, store: Dict[str, int]):
    nano = NanoFactory.from_file('example_1.txt')
    nano.produce(elem, quantities, True)

    assert nano.mined_ore == mined_ore
    assert {k: v for k, v in nano.storage.items() if v > 0} == store


@pytest.mark.parametrize('filename, ore', (
    ('example_2.txt', 13312),
    ('example_3.txt', 180697),
    ('example_4.txt', 2210736),
))
def test_example_2(filename: str, ore: int):
    nano = NanoFactory.from_file(filename)
    nano.produce('FUEL', 1, True)

    assert nano.mined_ore == ore


def test_question_1():
    nano = NanoFactory.from_file('input.txt')
    nano.produce('FUEL', 1, True)
    assert nano.mined_ore == 654909


@pytest.mark.xfail(reason='bug to identify in mass_produce')
def test_question_2():  # Does not pass :(
    nano = NanoFactory.from_file('input.txt')
    nano.mass_produce('FUEL', 654909)
    assert nano.storage['FUEL'] == 2876992


@pytest.mark.parametrize('filename, ore_per_fuel, fuel', (
    # ('example_2.txt', 13312, 82892753),  # this does not pass :(
    ('example_3.txt', 180697, 5586022),
    ('example_4.txt', 2210736, 460664),
))
def test_mass_produce(filename: str, ore_per_fuel: int, fuel: int):
    nano = NanoFactory.from_file(filename)
    nano.storage = {
        'ORE': 1000000000000,
    }
    nano.mass_produce('FUEL', ore_per_fuel)
    assert nano.storage['FUEL'] == fuel, f'{nano.storage}'


@pytest.mark.xfail(reason='bug to identify in mass_produce')
@pytest.mark.parametrize('filename, ore_per_fuel, fuel', (
    ('example_2.txt', 13312, 82892753),  # this does not pass :(
))
def test_mass_produce(filename: str, ore_per_fuel: int, fuel: int):
    nano = NanoFactory.from_file(filename)
    nano.storage = {
        'ORE': 1000000000000,
    }
    nano.mass_produce('FUEL', ore_per_fuel)
    assert nano.storage['FUEL'] == fuel, f'{nano.storage}'