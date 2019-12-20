import pytest

from day_10.astoreoid_detector import AsteroidMap, Position


def test_sanity():
    assert Position(0, 1) == Position(0, 1)
    assert Position(1, 0) != Position(0, 1)


@pytest.mark.parametrize('position, exp_vector', (
    (Position(3, 1), Position(3, 1)),  # A, cannot ve simplified
    (Position(3, 2), Position(3, 2)),  # B, cannot be simplified
    (Position(3, 3), Position(1, 1)),  # C, simplifies 3,3 -> 1,1
    (Position(2, 3), Position(2, 3)),  # D, cannot be simplified
    (Position(1, 3), Position(1, 3)),  # E, cannot be simplified
    (Position(2, 4), Position(1, 2)),  # F, simplifies 2,4 -> 1,2
    (Position(4, 3), Position(4, 3)),  # G, cannot be simplified
))
def test_vector(position, exp_vector):
    """
    #.........
    ...A......
    ...B..a...
    .EDCG....a
    ..F.c.b...
    .....c....
    ..efd.c.gb
    .......c..
    ....f...c.
    ...e..d..c
    """
    vector = Position(0, 0).vector(position)
    assert vector == exp_vector

    rev_vector = position.vector(Position(0, 0))
    exp_rev_vector = Position(-exp_vector.x, -exp_vector.y)
    assert rev_vector == exp_rev_vector


def test_load_map():
    asteroid_map = AsteroidMap.load_from_file('example_1.txt')

    is_asteroid = []

    for y in asteroid_map.y_range():
        is_asteroid.append([
            asteroid_map.is_asteroid(Position(x, y))
            for x in asteroid_map.x_range()
        ])

    assert asteroid_map.y_range() == range(0, 5)
    assert asteroid_map.x_range() == range(0, 5)
    assert len(asteroid_map.asteroid_map) == 10

    exp_is_asteroid = [
        [False, True, False, False, True],
        [False, False, False, False, False],
        [True, True, True, True, True],
        [False, False, False, False, True],
        [False, False, False, True, True],
    ]

    for y, l in enumerate(is_asteroid):
        assert l == exp_is_asteroid[y], f'Line {y}'


def test_view():
    asteroid_map = AsteroidMap.load_from_file('example_1.txt')
    asteroid_map.compute_all_visible()

    view = []
    for y in asteroid_map.y_range():
        view.append([
            asteroid_map.can_see(Position(x, y))
            for x in asteroid_map.x_range()
        ])

    exp_view = [
        [0, 7, 0, 0, 7,],
        [0, 0, 0, 0, 0,],
        [6, 7, 7, 7, 5,],
        [0, 0, 0, 0, 7,],
        [0, 0, 0, 8, 7,],
    ]
    for y, l in enumerate(exp_view):
        assert l == view[y], f'For line {y}'


@pytest.mark.parametrize('filename, position, can_see', (
    ('example_1.txt', Position(3, 4), 8),
    ('example_2.txt', Position(5, 8), 33),
    ('example_3.txt', Position(1, 2), 35),
    ('example_4.txt', Position(6, 3), 41),
    ('example_5.txt', Position(11, 13), 210),
))
def test_best_station(filename, position, can_see):
    asteroid_map = AsteroidMap.load_from_file(filename)
    best = asteroid_map.find_station()
    assert best.position == position
    assert len(best.can_see) == can_see


@pytest.mark.parametrize('filename, position, can_see', (
    ('example_5.txt', Position(11, 13), 210),
))
def test_slow_best_station(filename, position, can_see):
    asteroid_map = AsteroidMap.load_from_file(filename)
    best = asteroid_map.find_station()
    assert best.position == position
    assert len(best.can_see) == can_see