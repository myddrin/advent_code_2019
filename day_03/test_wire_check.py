from typing import List, Optional

import pytest

from day_03.wire_check import Grid, Position


def test_r8_from_center():
    center = Position(0, 0)
    next_locations = list(center.next_positions('R8'))
    assert next_locations == [
        Position(1, 0),
        Position(2, 0),
        Position(3, 0),
        Position(4, 0),
        Position(5, 0),
        Position(6, 0),
        Position(7, 0),
        Position(8, 0),
    ]


_first_wire = [
    # R8
    Position(1, 0),
    Position(2, 0),
    Position(3, 0),
    Position(4, 0),
    Position(5, 0),
    Position(6, 0),
    Position(7, 0),
    Position(8, 0),
    # U5
    Position(8, 1),
    Position(8, 2),
    Position(8, 3),
    Position(8, 4),
    Position(8, 5),
    # L5
    Position(7, 5),
    Position(6, 5),
    Position(5, 5),
    Position(4, 5),
    Position(3, 5),
    # D3
    Position(3, 4),
    Position(3, 3),
    Position(3, 2),
]

_second_wire = [
    # U7
    Position(0, 1),
    Position(0, 2),
    Position(0, 3),
    Position(0, 4),
    Position(0, 5),
    Position(0, 6),
    Position(0, 7),
    # R6
    Position(1, 7),
    Position(2, 7),
    Position(3, 7),
    Position(4, 7),
    Position(5, 7),
    Position(6, 7),
    # D4
    Position(6, 6),
    Position(6, 5),
    Position(6, 4),
    Position(6, 3),
    # L4
    Position(5, 3),
    Position(4, 3),
    Position(3, 3),
    Position(2, 3),
]


def test_add_first_wire():
    grid = Grid()

    first_id = grid.add_wire(['R8', 'U5', 'L5', 'D3'])
    assert first_id == 0

    for step, position in enumerate(_first_wire, start=1):
        assert position in grid.cells
        assert first_id in grid.cells[position]
        assert len(grid.cells[position]) == 1
        assert grid.get_steps(position) == step


def test_add_second_wire():
    grid = Grid()

    first_id = grid.add_wire(['R8', 'U5', 'L5', 'D3'])
    second_id = grid.add_wire(['U7', 'R6', 'D4', 'L4'])
    assert second_id == 1

    for position in set(list(_first_wire) + list(_second_wire)):
        assert position in grid.cells
        in_first = position in _first_wire
        in_second = position in _second_wire
        if in_first and in_second:
            assert len(grid.cells[position]) == 2
        else:
            assert len(grid.cells[position]) == 1

        if in_first:
            assert first_id in grid.cells[position]
        if in_second:
            assert second_id in grid.cells[position]


def test_self_cross_is_ok():
    grid = Grid()

    wire_id = grid.add_wire(['R20', 'U10', 'L10', 'D20'])

    for value in grid.cells.values():
        assert len(value) == 1
        assert wire_id in value


@pytest.mark.parametrize('x, y, exp_distance', (
    (0, 0, 0),
    (3, 3, 6),
    (-3, 3, 6),
    (3, -3, 6),
    (-3, -3, 6),
))
def test_distance(x: int, y: int, exp_distance: int):
    center = Position(0, 0)
    assert Position(x, y).distance(center) == exp_distance


@pytest.mark.parametrize('wires, exp_distance, exp_steps', (
    (
        (
            ('R8', 'U5', 'L5', 'D3'),
            ('U7', 'R6', 'D4', 'L4'),
        ),
        6,
        30,
    ),
    (
        (
            ('R75', 'D30', 'R83', 'U83', 'L12', 'D49', 'R71', 'U7', 'L72'),
            ('U62', 'R66', 'U55', 'R34', 'D71', 'R55', 'D58', 'R83'),
        ),
        159,
        610,
    ),
    (
        (
            ('R98', 'U47', 'R26', 'D63', 'R33', 'U87', 'L62', 'D20', 'R33', 'U53', 'R51'),
            ('U98', 'R91', 'D20', 'R16', 'D67', 'R40', 'U7', 'R15', 'U6', 'R7'),
        ),
        135,
        410,
    ),
))
def test_close_circuit(wires: List[List[str]], exp_distance: Optional[int], exp_steps: Optional[int]):
    grid = Grid()
    for wire_commands in wires:
        grid.add_wire(wire_commands)

    close_circuit = grid.close_circuit(distance=True)
    assert grid.get_distance_from_center(close_circuit) == exp_distance

    close_circuit = grid.close_circuit()
    assert grid.get_steps(close_circuit) == exp_steps
