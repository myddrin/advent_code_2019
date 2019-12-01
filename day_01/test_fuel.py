import pytest

from day_01.fuel import mass_to_fuel, recursive_mass_to_fuel


@pytest.mark.parametrize('mass, fuel', (
    (0, 0),
    (6, 0),
    (12, 2),
    (14, 2),
    (1969, 654),
    (100756, 33583),
))
def test_mass_to_fuel(mass: int, fuel: int):
    assert mass_to_fuel(mass) == fuel


@pytest.mark.parametrize('mass, fuel', (
    (0, 0),
    (6, 0),
    (12, 2),
    (14, 2),
    (1969, 966),
    (100756, 50346),
))
def test_recursive_mass_to_fuel(mass: int, fuel: int):
    assert recursive_mass_to_fuel(mass) == fuel
