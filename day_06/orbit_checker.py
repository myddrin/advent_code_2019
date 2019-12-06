import attr
from typing import Optional, List, Dict, Iterator, Tuple, Iterable


@attr.s
class Body:
    name: str = attr.ib()
    distance_to_com: Optional[int] = attr.ib(default=None)

    orbits: Optional["Body"] = attr.ib(default=None)
    """The Body that this Body orbits"""
    satelites: List["Body"] = attr.ib(default=attr.Factory(list))
    """The Bodies that are orbitting that Body"""

    def add_body(self, other: "Body") -> int:
        if other.orbits is not None:
            raise RuntimeError(f'{other} already orbits a body')

        self.satelites.append(other)
        other.orbits = self
        return len(self.satelites)

    def set_distance_to_com(self, distance: int):
        self.distance_to_com = distance
        for body in self.satelites:
            body.set_distance_to_com(distance + 1)

    def path_to_com(self) -> List[str]:
        rv = [self.name]
        if self.distance_to_com > 0:
            if not self.orbits:
                raise RuntimeError(f'{self} does not orbit anything but is not COM')
            rv += self.orbits.path_to_com()

        return rv

    def __str__(self):
        return f'{self.name}({self.distance_to_com})'


@attr.s
class SystemMap:
    center_of_mass = 'COM'

    bodies: Dict[str, Body] = attr.ib(default=attr.Factory(dict))

    @classmethod
    def load_file(cls, filename: str) -> Iterator[Tuple[str, str]]:
        with open(filename) as f:
            for line in f:
                main, satelite = line.replace('\n', '').split(')')
                yield main, satelite

    @classmethod
    def load_map(cls, body_map: Iterable[Tuple[str, str]]):
        system_map = cls()

        for main, satelite in body_map:
            main_body = system_map.bodies.get(main)
            if main_body is None:
                main_body = Body(main)
                print(f'Creating {main_body}')
                system_map.bodies[main] = main_body

            satelite_body = system_map.bodies.get(satelite)
            if satelite_body is None:
                satelite_body = Body(satelite)
                print(f'Creating {satelite_body}')
                system_map.bodies[satelite] = satelite_body

            d = main_body.add_body(satelite_body)
            print(f'{main} now has {d} satelites')

        if cls.center_of_mass not in system_map.bodies:
            raise RuntimeError(f'File has not Center Of Mass')
            # This triggers a recursive call
        system_map.bodies[cls.center_of_mass].set_distance_to_com(0)
        return system_map

    @classmethod
    def from_file(cls, filename: str) -> "SystemMap":
        return cls.load_map(cls.load_file(filename))

    def orbit_checksums(self) -> int:
        return sum((b.distance_to_com for b in self.bodies.values()))

    def shortest_path(self, a: str, b: str):
        if a not in self.bodies:
            raise RuntimeError(f'{a} is unknown')
        if b not in self.bodies:
            raise RuntimeError(f'{b} is unknown')

        body_a = self.bodies[a]
        body_b = self.bodies[b]

        body_a_path_to_com = body_a.path_to_com()
        body_b_path_to_com = body_b.path_to_com()

        found_paths: Dict[str, List[str]] = {}

        for body_name in body_a_path_to_com:
            if body_name in body_b_path_to_com and body_name not in found_paths:
                # We have a common distance to COM
                path = []
                for b in body_a_path_to_com:
                    path.append(b)
                    if b == body_name:
                        break
                idx = len(path)
                for b in body_b_path_to_com:
                    if b == body_name:
                        break
                    path.insert(idx, b)

                found_paths[body_name] = path

        rv = sorted(found_paths.values(), key=lambda p: len(p))
        print(f'Found {len(found_paths)} paths ({len(rv[0])} to {len(rv[-1])})')
        return rv[0]


if __name__ == '__main__':

    system_map = SystemMap.from_file('input.txt')

    checksum = system_map.orbit_checksums()
    print(f'System map orbit checksum is {checksum}')  # 130681

    you_orbit = system_map.bodies['YOU'].orbits
    san_orbit = system_map.bodies['SAN'].orbits

    print(f'You orbit {you_orbit}')
    print(f'Santa orbits {san_orbit}')

    path_to_santa = system_map.shortest_path(you_orbit.name, san_orbit.name)
    print(f'The path to Santa is {len(path_to_santa) - 1} steps')  # 313
