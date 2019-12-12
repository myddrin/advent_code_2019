import pytest

from day_12.gravity import Position3, Moon, System


@pytest.mark.parametrize('position, velocity, exp_pot, exp_kin, exp_total', (
    (Position3(2, 1, -3), Position3(-3, -2, 1), 6, 6, 36),
    (Position3(1, -8, 0), Position3(-1, 1, 3), 9, 5, 45),
    (Position3(3, -6, 1), Position3(3, 2, -3), 10, 8, 80),
    (Position3(2, 0, 4), Position3(1, -1, -1), 6, 3, 18),
))
def test_energy(position, velocity, exp_pot, exp_kin, exp_total):
    moon = Moon(position, velocity)
    assert moon.potential_energy == exp_pot
    assert moon.kinetic_energy == exp_kin
    assert moon.total_energy == exp_total


def test_apply_gravity():
    ganymede = Moon(Position3(3, 5, 6), Position3(0, 1, 2))
    calysto = Moon(Position3(5, 3, 6), Position3(3, 4, 5))

    ganymede.apply_gravity(calysto)

    # Position unchanged
    assert ganymede.position == Position3(3, 5, 6)
    assert calysto.position == Position3(5, 3, 6)
    # velocity changed
    assert ganymede.velocity == Position3(0 + 1, 1 - 1, 2 + 0)
    assert calysto.velocity == Position3(3 - 1, 4 + 1, 5 + 0)


def test_apply_velocity():
    ganymede = Moon(Position3(3, 5, 6), Position3(-1, 2, 2))
    calysto = Moon(Position3(5, 3, 6), Position3(4, 3, 5))

    ganymede.apply_velocity()
    calysto.apply_velocity()

    # position changed
    assert ganymede.position == Position3(2, 7, 8)
    assert calysto.position == Position3(9, 6, 11)
    # velocity unchanged
    assert ganymede.velocity == Position3(-1, 2, 2)
    assert calysto.velocity == Position3(4, 3, 5)


def test_example_1_loading():
    system = System(Moon.from_file('example_1.txt'))

    exp_moons = [
        ((-1, 0, 2), (0, 0, 0)),
        ((2, -10, -7), (0, 0, 0)),
        ((4, -8, 8), (0, 0, 0)),
        ((3, 5, -1), (0, 0, 0)),
    ]
    for i, moon in enumerate(system.moons):
        assert moon.position == Position3(*exp_moons[i][0])
        assert moon.velocity == Position3(*exp_moons[i][1])


def test_example_1_run_1():
    system = System(Moon.from_file('example_1.txt'))

    system.print()

    system.run(1)

    exp_moons = [
        ((2, -1, 1), (3, -1, -1)),
        ((3, -7, -4), (1, 3, 3)),
        ((1, -7, 5), (-3, 1, -3)),
        ((2, 2, 0), (-1, -3, 1)),
    ]
    for i, moon in enumerate(system.moons):
        assert moon.position == Position3(*exp_moons[i][0])
        assert moon.velocity == Position3(*exp_moons[i][1])


def test_example_1_run_10():
    system = System(Moon.from_file('example_1.txt'))
    system.run(10)

    exp_moons = [
        ((2, 1, -3), (-3, -2, 1), 36),
        ((1, -8, 0), (-1, 1, 3), 45),
        ((3, -6, 1), (3, 2, -3), 80),
        ((2, 0, 4), (1, -1, -1), 18),
    ]
    for i, moon in enumerate(system.moons):
        assert moon.position == Position3(*exp_moons[i][0]), f'For moon {i}'
        assert moon.velocity == Position3(*exp_moons[i][1]), f'For moon {i}'
        assert moon.total_energy == exp_moons[i][2], f'For moon {i}'

    assert system.total_energy == 179


def test_example_2_run_100():
    system = System(Moon.from_file('example_2.txt'))
    system.run(100)

    exp_moons = [
        ((8, -12, -9), (-7, 3, 0), 29, 10, 290),
        ((13, 16, -3), (3, -11, -5), 32, 19, 608),
        ((-29, -11, -1), (-3, 7, 4), 41, 14, 574),
        ((16, -13, 23), (7, 1, 1), 52, 9, 468),
    ]
    for i, moon in enumerate(system.moons):
        assert moon.position == Position3(*exp_moons[i][0]), f'For moon {i}'
        assert moon.velocity == Position3(*exp_moons[i][1]), f'For moon {i}'
        assert moon.potential_energy == exp_moons[i][2], f'For moon {i}'
        assert moon.kinetic_energy == exp_moons[i][3], f'For moon {i}'
        assert moon.total_energy == exp_moons[i][4], f'For moon {i}'

    assert system.total_energy == 1940


def test_example_1_brute_converges():
    system = System(Moon.from_file('example_1.txt'))
    print(f'Initial state: {system.state()}')
    past_states = set()

    assert system.brute_convergence(past_states, 1000) is None  # 1000
    assert system.brute_convergence(past_states, 1770) is None  # 2770

    assert system.state() == 'M((2,-1,1),(-3,2,2));' \
                             'M((3,-7,-4),(2,-5,-6));' \
                             'M((1,-7,5),(0,-3,6));' \
                             'M((2,2,0),(1,6,-2))'

    assert system.brute_convergence(past_states, 1000) == 2


def test_example_1_find_converges():
    assert System.find_convergence('example_1.txt', 3000) == 2772


# def test_slow_example_2_converges():
#     system = System(Moon.from_file('example_2.txt'))
#     print(f'Initial state: {system.state()}')
#     past_states = set()
#
#     assert system.find_convergence(past_states, 4686774924) == 4686774924


def test_question_1():
    system = System(Moon.from_file('input.txt'))
    system.run(1000)

    assert system.total_energy == 5517
