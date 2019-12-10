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

    def _get_visible_asteroids(self, cell: Cell) -> Set[Position]:
        visible_map = [
            [True] * len(self.map[0])
        ] * len(self.map)

        def _update_shadow(init_p, end_p, diff_p):
            for y in range(init_p.y, end_p.y, diff.y):
                for x in range(init_p.x, end_p.x, diff.x):
                    visible_map[y][x] = False

        for asteroid in self.asteroids():
            if asteroid.position != cell.position:
                continue

            # hide stuff in shadow
            diff = cell.difference(asteroid.position)

            init_p = Position(asteroid.position.x + diff.x, asteroid.position.y + diff.y)
            end_p = Position(
                len(self.map[0]),
                len(self.map),
            )
            if diff.x < 0:
                end_p.x = 0
            if diff.y < 0:
                end_p.y = 0

            if diff.y != 0:
                try_y = range(init_p.y, end_p.y, diff.y)
            else:
                try_y = [init_p.y]

            if diff.x != 0:
                try_x = range(init_p.x, end_p.x, diff.x)
            else:
                try_x = [init_p.x]

            for y in try_y:
                for x in try_x:
                    visible_map[y][x] = False

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