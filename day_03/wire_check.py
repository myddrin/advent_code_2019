from typing import List, Dict, Iterator, Optional

import attr


@attr.s(hash=True)
class Position:
    x = attr.ib()  # type: int
    y = attr.ib()  # type: int

    def distance(self, pos: "Position") -> int:
        return abs(pos.x - self.x) + abs(pos.y - self.y)

    def next_positions(self, command: str) -> Iterator["Position"]:
        direction = command[0]
        length = int(command[1:]) + 1
        if direction.upper() == 'R':
            for i in range(1, length):
                yield Position(self.x + i, self.y)
        elif direction.upper() == 'L':
            for i in range(1, length):
                yield Position(self.x - i, self.y)
        elif direction.upper() == 'U':
            for i in range(1, length):
                yield Position(self.x, self.y + i)
        elif direction.upper() == 'D':
            for i in range(1, length):
                yield Position(self.x, self.y - i)
        else:
            raise RuntimeError(f'Unexpected direction: {direction}')


class Grid:

    def __init__(self):
        self.center = Position(0, 0)
        self.cells: Dict[Position, Dict[int, int]] = {}
        self._next_wire_id = 0

    def _add_wire(self, position: Position, wire_id: int, steps: int):
        self.cells.setdefault(position, {})
        if wire_id not in self.cells[position]:
            self.cells[position][wire_id] = steps

    def add_wire(self, commands: List[str]) -> int:
        wire_id = self._next_wire_id
        self._next_wire_id += 1

        current_position = self.center
        steps = 0
        self._add_wire(current_position, wire_id, steps)
        steps += 1

        for cmd in commands:
            position = None

            for position in current_position.next_positions(cmd):
                self._add_wire(position, wire_id, steps)
                steps += 1

            if position is None:
                raise RuntimeError(f'Failed to get next position from {current_position} for {cmd}')
            current_position = position

        return wire_id

    def close_circuit(self, distance=False) -> Optional[Position]:
        entries = [
            position
            for position, wires in self.cells.items()
            if len(wires) > 1 and position != self.center
        ]
        if entries:
            if distance:
                # We want the closest to the center
                key_fn = self.get_distance_from_center
            else:
                # Otherwise we want the smallest step count
                key_fn = self.get_steps

            return sorted(entries, key=key_fn)[0]

    def get_distance_from_center(self, position: Position) -> Optional[int]:
        if position:
            return position.distance(self.center)

    def get_steps(self, position: Position) -> Optional[int]:
        if position in self.cells:
            return sum(self.cells[position].values())

    @classmethod
    def from_file(cls, filename: str) -> "Grid":
        grid = Grid()
        with open(filename) as f:
            for line in f:
                # one wire per line
                grid.add_wire(line.split(','))

        return grid


if __name__ == '__main__':

    the_grid = Grid.from_file('input.txt')

    by_distance = the_grid.close_circuit(distance=True)
    if by_distance:
        print(f'Close circuit by distance is: {the_grid.get_distance_from_center(by_distance)}')  # 896
    else:
        print('No close circuit by distance found')

    by_steps = the_grid.close_circuit()
    if by_steps:
        print(f'Close circuit by steps is: {the_grid.get_steps(by_steps)}')  # 16524
    else:
        print('No close circuit by distance found')
