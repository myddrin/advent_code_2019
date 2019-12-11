from typing import Optional, List, Set

import attr


@attr.s(hash=True)
class Position:
    x: int = attr.ib()
    y: int = attr.ib()


@attr.s
class Cell:
    position: Position = attr.ib()
    asteroid = attr.ib(default=False)
    can_see: Set["Cell"] = attr.ib(default=attr.Factory(set))
    """The number visible from this location"""

    def difference(self, position: "Position"):
        diff_y = self.position.y - position.y
        diff_x = self.position.x - position.x
        if diff_y != 0 and diff_x % diff_y == 0:
            diff_x = diff_x // diff_y
            diff_y = 1
        elif diff_x != 0 and diff_y % diff_x == 0:
            diff_x = 1
            diff_y = diff_y // diff_x

        return Position(diff_x, diff_y)


class AsteroidMap:
    Asteroid = '#'
    Empty = '.'

    def __init__(self):
        self.map: List[List[Cell]] = []

    def asteroids(self):
        for l in self.map:
            for c in l:
                if c.asteroid:
                    yield c

    @classmethod
    def load_from_file(cls, filename: str) -> "AsteroidMap":
        obj = cls()

        with open(filename, 'r') as f:
            for y, line in enumerate(f):
                obj.map.append([
                    Cell(Position(x, y), c == cls.Asteroid)
                    for x, c in enumerate(line.replace('\n', ''))
                ])

        x = len(obj.map[0])
        for y, line in enumerate(obj.map[1:], start=1):
            if len(line) != x:
                raise RuntimeError(f'Incomplete map line {y} has a different size from line 0. Exp={x} Act={len(line)}')

        obj.compute_visible()
        return obj

    def _update_visible(self, visible_map, cell, asteroid):
        diff = cell.difference(asteroid.position)

        p = Position(asteroid.position.x + diff.x, asteroid.position.y + diff.y)
        end_p = Position(
            len(self.map[0]),
            len(self.map),
        )
        # if diff.x < 0:
        #     end_p.x = 0
        # if diff.y < 0:
        #     end_p.y = 0

        while True:
            if p.x < 0 or p.x >= end_p.x or p.y < 0 or p.y > end_p.y:
                break

            visible_map[p.y][p.x] = False

            p = Position(p.x + diff.x, p.y + diff.y)

    def _empty_visible(self):
        visible_map = []
        for y in range(0, len(self.map)):
            row = []
            for x in range(0, len(self.map[0])):
                row.append(True)
            visible_map.append(row)

        return visible_map

    def _get_visible_asteroids(self, cell: Cell) -> Set[Position]:
        visible_map = []
        for y in range(0, len(self.map)):
            row = []
            for x in range(0, len(self.map[0])):
                row.append(True)
            visible_map.append(row)

        for asteroid in self.asteroids():
            if asteroid.position == cell.position:
                continue

            # hide stuff in shadow
            self._update_visible(visible_map, cell, asteroid)

        return set((
            asteroid.position
            for asteroid in self.asteroids()
            if visible_map[asteroid.position.y][asteroid.position.x]
        ))

    def compute_visible(self):
        for cell in self.asteroids():
            visible_map = self._get_visible_asteroids(cell)

            cell.can_see = visible_map
            # We start from where the asteroid is and spread outward


if __name__ == '__main__':

    pass