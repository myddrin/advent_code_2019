import math
from enum import Enum, unique
from typing import Dict, Iterator, Set, List, Optional

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

    def angle_from(self, position: Position) -> float:
        # To consider position as the center of a trigonometric circle
        this_position = position + Position(-self.position.x, -self.position.y)
        # We inverse the x axis to rotation 90 deg up?
        rad = math.atan2(-this_position.x, this_position.y)
        # atan2 returns -pi to pi
        if rad < 0.0:
            rad += 2 * math.pi
        return rad

    def laser_rotation(self) -> List["Asteroid"]:
        return sorted(self.can_see, key=lambda a: a.angle_from(self.position))


@unique
class StringRepr(Enum):
    Asteroid = '#'
    Station = 'X'
    Empty = '.'


class AsteroidMap:

    def __init__(self):
        self.asteroid_map: Dict[Position, Asteroid] = {}
        self._max_position: Position = Position(0, 0)
        self._station: Optional[Asteroid] = None

    def set_station(self, position: Position):
        self._station = self.asteroid_map[position]
        if self._station.can_see is None:
            self.compute_visible_asteroids(self._station)

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
            if a.can_see is None:
                self.compute_visible_asteroids(a)
            return len(a.can_see)
        return 0

    @classmethod
    def load_from_file(cls, filename: str) -> "AsteroidMap":
        obj = cls()
        station_position = None

        with open(filename, 'r') as f:
            for y, line in enumerate(f):
                for x, c in enumerate(line.replace('\n', '')):
                    if c in (StringRepr.Asteroid.value, StringRepr.Station.value):
                        p = Position(x, y)
                        obj.asteroid_map[p] = Asteroid(p)

                        obj._max_position.x = max(obj._max_position.x, p.x + 1)
                        obj._max_position.y = max(obj._max_position.y, p.y + 1)

                        if c == StringRepr.Station.value:
                            station_position = p

        if station_position is not None:
            obj.set_station(station_position)
        return obj

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

    def find_station(self) -> Asteroid:
        if self._station is None:
            self.compute_all_visible()
            self._station = sorted(self.asteroid_map.values(), key=lambda a: len(a.can_see))[-1]

        return self._station

    def destroy_all(self, max_destroyed: Optional[int] = None) -> List[Asteroid]:
        destroyed = []
        i = 1
        while len(self._station.can_see) > 0:
            to_destroy = self._station.laser_rotation()
            print(f'Circle {i} of destruction: found {len(to_destroy)} asteroids')
            for a in to_destroy:
                destroyed.append(a)
                self.asteroid_map.pop(a.position)
                if max_destroyed is not None and len(destroyed) >= max_destroyed:
                    return destroyed
            self.compute_visible_asteroids(self._station)
            i += 1

        return destroyed


if __name__ == '__main__':
    asteroid_map = AsteroidMap.load_from_file('input.txt')

    station_p = Position(11, 13)  # None to compute it

    if station_p is not None:
        asteroid_map.set_station(station_p)

    station = asteroid_map.find_station()

    print(f'Found best location on {station.position} because it can see {len(station.can_see)} other asteroids')

    asteroid_destroyed = asteroid_map.destroy_all(200)

    if len(asteroid_destroyed) >= 200:
        winner = asteroid_destroyed[199]
        print(f'200th destroyed asteroid is on {winner.position} => {winner.position.x * 100 + winner.position.y}')
    else:
        print(f'Huh. There were not enough asteroids')
