from day_10.astoreoid_detector import AsteroidMap, Position


def test_sanity():
    assert Position(0, 1) == Position(0, 1)


def test_load_map():
    map = AsteroidMap.load_from_file('example_1.txt')

    is_asteroid = []
    for l in map.map:
        is_asteroid.append([
            c.asteroid
            for c in l
        ])

    assert len(map.map) == 5
    assert len(map.map[0]) == 5

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
    map = AsteroidMap.load_from_file('example_1.txt')

    view = []
    for l in map.map:
        view.append([
            len(c.can_see) if c.asteroid else None
            for c in l
        ])

    assert len(map.map) == 5
    assert len(map.map[0]) == 5

    exp_visible = [
        [True, True, True, True, True],
        [True, True, True, True, True],
        [True, True, True, True, True],
        [True, True, True, True, False],
        [True, True, True, True, True],
    ]

    visible = map._empty_visible()
    map._update_visible(visible, map.map[0][1], map.map[2][3])
    assert visible == exp_visible

    exp_0_1 = set((
        Position(1, 0),
        Position(4, 0),
        Position(0, 2),
        Position(1, 2),
        Position(2, 2),
        Position(3, 2),
        Position(4, 2),
    ))

    assert map.map[0][1].can_see == exp_0_1, \
        f'Unexpected {", ".join(str(f) for f in map.map[0][1].can_see if f not in exp_0_1)}'

    exp_is_asteroid = [
        [None, 7, None, None, 7],
        [None, None, None, None, None],
        [6, 7, 7, 7, 5],
        [None, None, None, None, 7],
        [None, None, None, 8, 7],
    ]

    for y, l in enumerate(view):
        assert l == exp_is_asteroid[y], f'Line {y}'