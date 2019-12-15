from datetime import datetime
from enum import IntEnum, unique
from random import choice, seed
from typing import Dict, List, Callable, Generator, Tuple, Optional

import attr

from common.intcode import Program


@unique
class Direction(IntEnum):
    North = 1
    South = 2
    West = 3
    East = 4


def revese_direction(direction: Direction):
    if direction == Direction.North:
        return Direction.South
    elif direction == Direction.South:
        return Direction.North
    elif direction == Direction.West:
        return Direction.East
    elif direction == Direction.East:
        return Direction.West
    raise RuntimeError('Wrong direction')


@unique
class Status(IntEnum):
    WallFound = 0
    MoveOk = 1
    FoundOxygenTank = 2


@attr.s(hash=True)
class Position:
    x: int = attr.ib()
    y: int = attr.ib()

    def neighbour(self, direction: Direction):
        if direction == Direction.North:
            return Position(self.x, self.y - 1)
        elif direction == Direction.South:
            return Position(self.x, self.y + 1)
        elif direction == Direction.West:
            return Position(self.x - 1, self.y)
        elif direction == Direction.East:
            return Position(self.x + 1, self.y)
        raise RuntimeError('Wrong direction')

    def all_neighbours(self):
        # -> Generator[Tuple[Direction, "Position"]]
        for d in (Direction.North, Direction.South, Direction.East, Direction.West):
            yield d, self.neighbour(d)


class InputProgram(Program):

    def __init__(self, read_fn: Callable[[], int], *args, **kwargs):
        super(InputProgram, self).__init__(*args, **kwargs)
        self.read_fn = read_fn

    def read(self):
        return self.read_fn()


@attr.s
class Cell:
    distance_to_s: Optional[int] = attr.ib(default=0)
    is_corridor: bool = attr.ib(default=False)
    is_oxygen: bool = attr.ib(default=False)

    @property
    def is_accessible(self):
        return self.is_corridor or self.is_oxygen


class AllDone(RuntimeError):
    pass


class Droid(Program):

    def __init__(self, filename: str):
        super(Droid, self).__init__(Program.load_memory_from_file(filename), dynamic_memory=True)
        self.map: Dict[Position, Cell] = {}
        self.current_status = Status.MoveOk
        self.current_position = Position(0, 0)
        self.next_position = Position(0, 0)
        self.trail = []

    def read(self):
        self.print_map(self.current_position)

        # Find a new position to move to
        unknown_location = {
            d: p
            for d, p in self.current_position.all_neighbours()
            if p not in self.map
        }

        if unknown_location:
            # Chose a random one
            print(f'Current position {self.current_position}: unknown_locations: {unknown_location}')
            d = choice(list(unknown_location.keys()))
            print(f'Chose: {d}')
            self.trail.append(d)
            self.next_position = unknown_location[d]
            return d.value
        else:
            # # Backtrack to a location that has the most unknown positions
            # neighbours = {}
            # for d, p in self.current_position.all_neighbours():
            #     # TODO(tr) rewrite with distance to start? This can get stuck :(
            #     if self.map[p].is_corridor:
            #         # Ignore neighbours that are walls!
            #         neighbours[d] = 0
            #         for d2, p2 in p.all_neighbours():
            #             if p2 == p:
            #                 continue  # Ignore current position
            #             if p2 not in self.map:
            #                 neighbours[d] += 2
            #             elif self.map[p2].is_corridor:
            #                 neighbours[d] += 1
            #             # otherwise no score
            #
            # print(f'Current position {self.current_position}: backtrack: {neighbours}')
            # # best_direction = sorted(neighbours, key=neighbours.get)[-1]
            # # print(f'Best: {best_direction}')
            # best_direction = choice(list(neighbours.keys()))
            # self.next_position = self.current_position.neighbour(best_direction)
            # return best_direction

            if not self.trail:
                raise AllDone  # That is not exactly true

            # Backtrack on the trail
            d = revese_direction(self.trail.pop())
            self.next_position = self.current_position.neighbour(d)
            print(f'Going back to previous point {self.next_position}')
            return d

    def print_map(self, special_pos: Optional[Position] = None, special_char: str = 'D'):
        min_p = Position(0, 0)
        max_p = Position(0, 0)
        for p in self.map.keys():
            min_p.x = min(min_p.x, p.x)
            min_p.y = min(min_p.y, p.y)
            max_p.x = max(max_p.x, p.x)
            max_p.y = max(max_p.y, p.y)

        for y in range(min_p.y, max_p.y + 1):
            row = ''
            for x in range(min_p.x, max_p.x + 1):
                p = Position(x, y)
                if p == Position(0, 0):
                    row += 'S'
                elif special_pos is not None and p == special_pos:
                    row += special_char
                elif p not in self.map:
                    row += '?'
                elif self.map[p].is_oxygen:
                    row += 'O'
                elif self.map[p].is_corridor:
                    row += '.'
                else:
                    row += '#'
            print(row)

    def write(self, value: int):
        self.current_status = Status(value)
        print(f'Received status {self.current_status}')
        if self.current_status == Status.FoundOxygenTank:
            print(f'Found oxygen tank on {self.next_position}')
            self.map[self.next_position] = Cell(
                # self.map[self.current_position].distance_to_s + 1,
                None,
                is_corridor=False,
                is_oxygen=self.current_status == Status.FoundOxygenTank,
            )
        elif self.current_status == Status.MoveOk:
            print(f'Moving from {self.current_position} -> {self.next_position}')

            if self.next_position not in self.map:
                self.map[self.next_position] = Cell(
                    # self.map[self.current_position].distance_to_s + 1,
                    None,
                    is_corridor=True,
                )
            self.current_position = self.next_position
            self.next_position = None
        elif self.current_status == Status.WallFound:
            print(f'Staying on {self.current_position} because of wall on {self.next_position}')
            self.trail.pop()  # Can't go to a wall
            if self.next_position not in self.map:
                self.map[self.next_position] = Cell(
                    None,
                )

    def compute_distance(self, position: Position):
        c = [
            self.map[p].distance_to_s
            for d, p in position.all_neighbours()
            if p in self.map and self.map[p].distance_to_s is not None and self.map[p].is_accessible
        ]
        self.map[position].distance_to_s = min(c) + 1
        print(f'Position to start of {position} is {self.map[position].distance_to_s}')
        for d, p in position.all_neighbours():
            next_p = self.map.get(p)
            if next_p and next_p.is_accessible and next_p.distance_to_s is None:
                self.compute_distance(p)

    def find_oxygen_tank(self) -> Optional[Position]:

        self.current_status = Position(0, 0)
        self.next_position = Position(0, 0)
        self.map = {
            self.current_status: Cell(0, True),
        }

        try:
            while True:
                self.pointer = self.execute(self.pointer)
        except AllDone:
            pass

        # Compute distance from start
        for d, p in Position(0, 0).all_neighbours():
            next_p = self.map.get(p)
            if next_p and next_p.is_accessible and next_p.distance_to_s is None:
                self.compute_distance(p)

        for p, c in self.map.items():
            if c.is_oxygen:
                return p
        return

        # 1. send movement command
        # 2. run until output
        # 3. read output


if __name__ == '__main__':

    droid = Droid('input.txt')
    chosen_seed = datetime.now()
    seed(chosen_seed)

    oxygen = droid.find_oxygen_tank()

    print(f'Found oxygen tank at {oxygen} ({droid.map[oxygen].distance_to_s}) seed={chosen_seed}')
    droid.print_map(droid.current_position)  # 188 is too low...
