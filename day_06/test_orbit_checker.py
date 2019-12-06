from day_06.orbit_checker import SystemMap


def test_example():
    system_map = SystemMap.from_file('example.txt')

    for b in system_map.bodies.values():
        assert b.distance_to_com is not None, f'{repr(b)} has no distance to COM!'
        if b.name != system_map.center_of_mass:
            assert b.orbits is not None
        else:
            assert b.orbits is None

    assert system_map.bodies['COM'].distance_to_com == 0
    assert system_map.bodies['D'].distance_to_com == 3
    assert system_map.bodies['L'].distance_to_com == 7

    assert system_map.orbit_checksums() == 42


def test_distance():
    system_map = SystemMap.from_file('example_2.txt')

    you_orbit = system_map.bodies['YOU'].orbits
    san_orbit = system_map.bodies['SAN'].orbits

    print(f'You orbit {you_orbit} (path to COM: {", ".join(you_orbit.path_to_com())}')
    print(f'Santa orbits {san_orbit} (path to COM: {", ".join(san_orbit.path_to_com())}')

    assert you_orbit.path_to_com() == ['K', 'J', 'E', 'D', 'C', 'B', 'COM']
    assert san_orbit.path_to_com() == ['I', 'D', 'C', 'B', 'COM']

    path = system_map.shortest_path(you_orbit.name, san_orbit.name)
    assert path == ['K', 'J', 'E', 'D', 'I']
