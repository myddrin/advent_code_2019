from day_10.astoreoid_detector import AsteroidMap


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
