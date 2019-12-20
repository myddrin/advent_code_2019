import math
from enum import Enum, unique
from typing import Dict, Iterator, Set

import attr


@attr.s(hash=True)
class Position:
    x: int = attr.ib()
    y: int = attr.ib()

    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y)

    def vector(self, position: "Position") -> "Position":
        diff_y = abs(self.y - position.y)
        diff_x = abs(self.x - position.x)

        div = math.gcd(diff_x, diff_y)
        if div != 1:
            diff_x = diff_x // div
            diff_y = diff_y // div

        if self.y > position.y:
            diff_y *= -1
        if self.x > position.x:
            diff_x *= -1

        return Position(diff_x, diff_y)


@attr.s(hash=True)
class Asteroid:
    position: Position = attr.ib()
    can_see: Set["Asteroid"] = attr.ib(default=None, cmp=False, hash=False)


@unique
class StringRepr(Enum):
    Asteroid = '#'
    Empty = '.'


class AsteroidMap:

    def __init__(self):
        self.asteroid_map: Dict[Position, Asteroid] = {}
        self._max_position: Position = Position(0, 0)

    def y_range(self):
        return range(0, self._max_position.y)

    def x_range(self):
        return range(0, self._max_position.x)

    def range(self) -> Iterator[Position]:
        for y in self.y_range():
            for x in self.x_range():
                yield Position(x, y)

    def is_asteroid(self, position: Position):
        a = self.asteroid_map.get(position)
        return a is not None

    def can_see(self, position: Position) -> int:
        a = self.asteroid_map.get(position)
        if a is not None:
            return len(a.can_see)
        return 0

    @classmethod
    def load_from_file(cls, filename: str) -> "AsteroidMap":
        obj = cls()

        with open(filename, 'r') as f:
            for y, line in enumerate(f):
                for x, c in enumerate(line.replace('\n', '')):
                    if c == StringRepr.Asteroid.value:
                        p = Position(x, y)
                        obj.asteroid_map[p] = Asteroid(p)

                        obj._max_position.x = max(obj._max_position.x, p.x + 1)
                        obj._max_position.y = max(obj._max_position.y, p.y + 1)

        return obj

    # def _update_visible(self, visible_map, cell, asteroid):
    #     diff = cell.difference(asteroid.position)
    #
    #     p = Position(asteroid.position.x + diff.x, asteroid.position.y + diff.y)
    #     end_p = Position(
    #         len(self.map[0]),
    #         len(self.map),
    #     )
    #     # if diff.x < 0:
    #     #     end_p.x = 0
    #     # if diff.y < 0:
    #     #     end_p.y = 0
    #
    #     while True:
    #         if p.x < 0 or p.x >= end_p.x or p.y < 0 or p.y > end_p.y:
    #             break
    #
    #         visible_map[p.y][p.x] = False
    #
    #         p = Position(p.x + diff.x, p.y + diff.y)
    #
    # def _empty_visible(self):
    #     visible_map = []
    #     for y in range(0, len(self.map)):
    #         row = []
    #         for x in range(0, len(self.map[0])):
    #             row.append(True)
    #         visible_map.append(row)
    #
    #     return visible_map
    #
    # def _get_visible_asteroids(self, cell: Cell) -> Set[Position]:
    #     visible_map = []
    #     for y in range(0, len(self.map)):
    #         row = []
    #         for x in range(0, len(self.map[0])):
    #             row.append(True)
    #         visible_map.append(row)
    #
    #     for asteroid in self.asteroids():
    #         if asteroid.position == cell.position:
    #             continue
    #
    #         # hide stuff in shadow
    #         self._update_visible(visible_map, cell, asteroid)
    #
    #     return set((
    #         asteroid.position
    #         for asteroid in self.asteroids()
    #         if visible_map[asteroid.position.y][asteroid.position.x]
    #     ))

    def compute_visible_asteroids(self, asteroid: Asteroid) -> None:
        visible_asteroids = {
            a.position: a
            for a in self.asteroid_map.values()
            if a != asteroid
        }  # start with a full map

        # Now for every other asteroids find if they hide others and remove the one they hide
        for other in self.asteroid_map.values():
            if other == asteroid:
                continue

            vector = asteroid.position.vector(other.position)
            # print(f'{asteroid.position} vs {other.position} gives vector {vector}')
            assert vector.x != 0 or vector.y != 0

            next_p = other.position + vector
            all_positions = list(self.range())
            # print(f'Found {len(all_positions)} positions')
            while next_p in all_positions:
                # print(f'Checking {next_p}')
                visible_asteroids.pop(next_p, None)
                next_p += vector

        asteroid.can_see = set(visible_asteroids.values())

    def compute_all_visible(self):
        print(f'Computing visible map for {len(self.asteroid_map)} asteroids')
        for i, asteroid in enumerate(self.asteroid_map.values()):
            print(f'For asteroid {i + 1}/{len(self.asteroid_map)} on {asteroid.position}')
            self.compute_visible_asteroids(asteroid)

    def best_monitor_station(self) -> Asteroid:
        asteroid = sorted(self.asteroid_map.values(), key=lambda a: len(a.can_see))[-1]
        return asteroid


if __name__ == '__main__':
    asteroid_map = AsteroidMap.load_from_file('input.txt')

    best = asteroid_map.asteroid_map.get(Position(11, 13))
    # best = None

    if best is None:
        asteroid_map.compute_all_visible()
        best = asteroid_map.best_monitor_station()
        # 11, 13
    else:
        asteroid_map.compute_visible_asteroids(best)
    print(f'Found best location on {best.position} because it can see {len(best.can_see)} other asteroids')
