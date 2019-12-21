import math

import pytest

from day_10.astoreoid_detector import AsteroidMap, Position, Asteroid


def test_sanity():
    assert Position(0, 1) == Position(0, 1)
    assert Position(1, 0) != Position(0, 1)
    assert [Position(0, 1), Position(1, 0)] == [Position(0, 1), Position(1, 0)]


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


def test_angle():
    station = Position(8, 3)
    a = Asteroid(Position(8, 0))
    b = Asteroid(Position(10, 3))
    c = Asteroid(Position(8, 5))
    d = Asteroid(Position(5, 3))

    assert a.angle_from(station) == 0.0
    assert b.angle_from(station) == math.pi / 2
    assert c.angle_from(station) == math.pi
    assert d.angle_from(station) == 3 * math.pi / 2


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

    for y, line in enumerate(is_asteroid):
        assert line == exp_is_asteroid[y], f'Line {y}'


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
        [0, 7, 0, 0, 7],
        [0, 0, 0, 0, 0],
        [6, 7, 7, 7, 5],
        [0, 0, 0, 0, 7],
        [0, 0, 0, 8, 7],
    ]
    for y, line in enumerate(exp_view):
        assert line == view[y], f'For line {y}'


@pytest.mark.parametrize('filename, position, can_see', (
    ('example_1.txt', Position(3, 4), 8),
    ('example_2.txt', Position(5, 8), 33),
    ('example_3.txt', Position(1, 2), 35),
    ('example_4.txt', Position(6, 3), 41),
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


def test_load_station():
    asteroid_map = AsteroidMap.load_from_file('example_6.txt')

    assert asteroid_map._station is not None
    assert asteroid_map._station.position == Position(8, 3)


def test_lazer_rotations():
    asteroid_map = AsteroidMap.load_from_file('example_6.txt')

    station = asteroid_map.find_station()
    destroyed = station.laser_rotation()
    exp_destroyed = [
        Position(8, 1),
        Position(9, 0),
        Position(9, 1),
        Position(10, 0),
        Position(9, 2),
        Position(11, 1),
        Position(12, 1),
        Position(11, 2),
        Position(15, 1),
        Position(12, 2),
        Position(13, 2),
        Position(14, 2),
        Position(15, 2),
        Position(12, 3),
        Position(16, 4),
        Position(15, 4),
        Position(10, 4),
        Position(4, 4),
        Position(2, 4),
        Position(2, 3),
        Position(0, 2),
        Position(1, 2),
        Position(0, 1),
        Position(1, 1),
        Position(5, 2),
        Position(1, 0),
        Position(5, 1),
        Position(6, 1),
        Position(6, 0),
        Position(7, 0),
    ]
    for i, a in enumerate(destroyed):
        assert a.position == exp_destroyed[i], f'Offset {i}'
    assert len(destroyed) == len(exp_destroyed)


def test_destruction():
    asteroid_map = AsteroidMap.load_from_file('example_6.txt')

    exp_destroyed = [
        Position(8, 1),
        Position(9, 0),
        Position(9, 1),
        Position(10, 0),
        Position(9, 2),
        Position(11, 1),
        Position(12, 1),
        Position(11, 2),
        Position(15, 1),
        Position(12, 2),
        Position(13, 2),
        Position(14, 2),
        Position(15, 2),
        Position(12, 3),
        Position(16, 4),
        Position(15, 4),
        Position(10, 4),
        Position(4, 4),
        Position(2, 4),
        Position(2, 3),
        Position(0, 2),
        Position(1, 2),
        Position(0, 1),
        Position(1, 1),
        Position(5, 2),
        Position(1, 0),
        Position(5, 1),
        Position(6, 1),
        Position(6, 0),
        Position(7, 0),
        # rot
        Position(8, 0),
        Position(10, 1),
        Position(14, 0),
        Position(16, 1),
        Position(13, 3),
        # rot
        Position(14, 3),
    ]
    destroyed = asteroid_map.destroy_all()

    for i, a in enumerate(destroyed):
        assert a.position == exp_destroyed[i], f'Rot 0, offset {i}'
    assert len(destroyed) == len(exp_destroyed)

    assert len(asteroid_map.asteroid_map) == 1, "Didn't destroy all"


def test_slow_destroy_all():
    asteroid_map = AsteroidMap.load_from_file('example_5.txt')
    asteroid_map.set_station(Position(11, 13))

    destroyed = asteroid_map.destroy_all()
    assert len(destroyed) == 299

    assert destroyed[0].position == Position(11, 12)
    assert destroyed[1].position == Position(12, 1)
    assert destroyed[2].position == Position(12, 2)
    assert destroyed[9].position == Position(12, 8)
    assert destroyed[19].position == Position(16, 0)
    assert destroyed[49].position == Position(16, 9)
    assert destroyed[99].position == Position(10, 16)
    assert destroyed[199].position == Position(8, 2)
    assert destroyed[200].position == Position(10, 9)
    assert destroyed[298].position == Position(11, 1)

    assert len(asteroid_map.asteroid_map) == 1


def test_slow_question_1():
    asteroid_map = AsteroidMap.load_from_file('input.txt')
    station = asteroid_map.find_station()
    assert station.position == Position(11, 13)


def test_question_2():
    asteroid_map = AsteroidMap.load_from_file('input.txt')
    asteroid_map.set_station(Position(11, 13))

    destroyed = asteroid_map.destroy_all(200)
    winner = destroyed[199]
    assert winner.position == Position(6, 4)
