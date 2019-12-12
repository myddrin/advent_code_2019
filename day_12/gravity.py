import math
import re
from functools import reduce
from typing import List, Set, Optional

import attr


@attr.s(hash=True)
class Position3:
    x: int = attr.ib()
    y: int = attr.ib()
    z: int = attr.ib()

    def __getitem__(self, item: int) -> int:
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.z
        else:
            raise IndexError(item)

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        else:
            raise IndexError(key)

    def __str__(self):
        return f'({self.x},{self.y},{self.z})'


@attr.s
class Moon:
    position: Position3 = attr.ib()
    velocity: Position3 = attr.ib(default=attr.Factory(lambda :Position3(0, 0, 0)))

    @property
    def potential_energy(self):
        return sum((abs(self.position[d]) for d in range(0, 3)))

    @property
    def kinetic_energy(self):
        return sum((abs(self.velocity[d]) for d in range(0, 3)))

    @property
    def total_energy(self):
        return self.potential_energy * self.kinetic_energy

    def apply_gravity(self, other: "Moon") -> None:
        for d in range(0, 3):
            if self.position[d] < other.position[d]:
                self.velocity[d] += 1
                other.velocity[d] -= 1
            elif self.position[d] > other.position[d]:
                self.velocity[d] -= 1
                other.velocity[d] += 1

    def apply_velocity(self):
        for d in range(0, 3):
            self.position[d] += self.velocity[d]

    @classmethod
    def from_file(cls, filename: str) -> List["Moon"]:
        rv: List[Moon] = []
        with open(filename) as f:
            # Does not work for line 2 of the example for some reason
            # extract_position = re.compile(r'<x=([-]?\d*),.?y=([-]?\d),.?z=([-]?\d)>')
            for line in f:
                # p_search = extract_position.search(line)
                # rv.append(
                #     Moon(Position3(*map(int, p_search.groups()))),
                # )
                data = line.replace('\n', '').replace('<', '').replace('>', '').split(',')
                p = []
                for d in data:
                    p.append(int(d.split('=')[1]))
                rv.append(
                    Moon(Position3(*p))
                )
        return rv

    def __str__(self):
        return f'M({self.position},{self.velocity})'


class System:

    def __init__(self, moons: List[Moon]):
        self.moons = moons

    @property
    def total_energy(self):
        return sum((m.total_energy for m in self.moons))

    def state(self):
        return ';'.join((str(m) for m in self.moons))

    def run(self, max_t: int):
        for t in range(0, max_t):
            for i, moon_1 in enumerate(self.moons):
                for j, moon_2 in enumerate(self.moons[i + 1:], start=i + 1):
                    # print(f'Computing gravity between moon {i} and {j}')
                    moon_1.apply_gravity(moon_2)

            for i, moon in enumerate(self.moons):
                moon.apply_velocity()
                # print(f'Moon {i} now {moon}')

    def brute_convergence(self, past_states: Set[str], max_t: int=None) -> Optional[int]:
        past_states.add(self.state())

        t = 0
        while True:
            self.run(1)
            state = self.state()
            if state in past_states:
                return t + 1
            past_states.add(state)
            t += 1

            if max_t is not None and t >= max_t:
                return

    @classmethod
    def find_convergence(cls, filename: str, max_t: int=None) -> Optional[int]:

        obj = System(Moon.from_file(filename))
        past_states = [
            {str(m), }
            for m in obj.moons
        ]
        converges = [
            None
            for m in obj.moons
        ]

        t = 1
        while None in converges:
            obj.run(1)

            for i, m in enumerate(converges):
                if m is None:
                    moon_hash = str(obj.moons[i])
                    if moon_hash not in past_states[i]:
                        past_states[i].add(moon_hash)
                    else:
                        converges[i] = t

            t += 1
            if t % 1000 == 0:
                print(f't={t}')
            if max_t is not None and t >= max_t:
                print(f'Current converges={converges}')
                return

        print(f'Found convergence of {converges}')
        return reduce(lambda a, b: a * b // math.gcd(a, b), converges)


    def print(self):
        for i, moon in enumerate(self.moons):
            print(f'{i}: {moon}')

    @classmethod
    def from_state(cls, state: str):
        pass


if __name__ == '__main__':
    system = System(Moon.from_file('input.txt'))

    t = 1000
    system.run(t)

    print(f'System total energy after {t} steps is {system.total_energy}')

    # reset
    system = System(Moon.from_file('input.txt'))

    try_for = 4686774924
    previous_states = set()
    converges = system.brute_convergence(previous_states, try_for)
    if converges is not None:
        print(f'Found convergence after {converges}')
    else:
        print(f'Did not find convergence after {try_for}')
        print(f'{system.state()}')
