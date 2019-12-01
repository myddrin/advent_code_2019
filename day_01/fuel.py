from typing import Iterator


def load_modules(filename: str) -> Iterator[int]:
    with open(filename) as f:
        for line in f:
            yield int(line)


def mass_to_fuel(mass: int) -> int:
    if mass < 6:
        return 0
    return mass // 3 - 2


def recursive_mass_to_fuel(mass: int) -> int:
    fuel = mass_to_fuel(mass)
    if fuel > 0:
        return fuel + recursive_mass_to_fuel(fuel)
    return fuel


if __name__ == '__main__':

    total_fuel = 0
    total_recursive_fuel = 0
    for module in load_modules('input.txt'):
        total_fuel += mass_to_fuel(module)
        total_recursive_fuel += recursive_mass_to_fuel(module)

    print(f'Fuel needed: {total_fuel}')
    print(f'Recursive fuel needed: {total_recursive_fuel}')
