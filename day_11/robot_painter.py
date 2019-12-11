from enum import Enum, unique, IntEnum
from typing import List, Dict, Set, Optional, Tuple

import attr

from common.intcode import Program, InputError


@unique
class Facing(Enum):
    Up = '^'
    Down = 'v'
    Left = '<'
    Right = '>'


@unique
class Rotation(IntEnum):
    Left90 = 0
    Rigth90 = 1


_rotation_map = {
    Facing.Up: {
        Rotation.Left90: Facing.Left,
        Rotation.Rigth90: Facing.Right,
    },
    Facing.Left: {
        Rotation.Left90: Facing.Down,
        Rotation.Rigth90: Facing.Up,
    },
    Facing.Right: {
        Rotation.Left90: Facing.Up,
        Rotation.Rigth90: Facing.Down,
    },
    Facing.Down: {
        Rotation.Left90: Facing.Right,
        Rotation.Rigth90: Facing.Left,
    },
}


@attr.s(hash=True)
class Position:
    x: int = attr.ib()
    y: int = attr.ib()

    def move(self, facing: Facing, direction: int) -> Tuple["Position", Facing]:
        rotation = Rotation(direction)
        new_facing = _rotation_map[facing][rotation]
        new_position = None

        if new_facing == Facing.Up:
            new_position = Position(self.x, self.y + 1)
        elif new_facing == Facing.Left:
            new_position = Position(self.x - 1, self.y)
        elif new_facing == Facing.Right:
            new_position = Position(self.x + 1, self.y)
        elif new_facing == Facing.Down:
            new_position = Position(self.x, self.y - 1)

        if new_position is None:
            raise RuntimeError(f'Unexpected new facing {new_facing}')
        return new_position, new_facing


class RobotPainter:
    Black = 0
    White = 1

    def __init__(self):
        self.init_memory: List[int] = Program.load_memory_from_file('input.txt')
        self.panels: List[int] = []
        self.position: Position = Position(0, 0)
        self.facing = Facing.Up
        self.hull: Dict[Position, int] = {}

    def reset(self, start_position):
        self.panels: List[int] = []
        self.hull: Dict[Position, int] = {}

        self.move_to(start_position, Facing.Up)

    def move_to(self, p: Position, facing: Facing):
        print(f'Robot is moving from {self.position} {self.facing} to {p} {facing}')
        self.position = p
        if p not in self.hull:
            self.hull[p] = self.Black
        self.facing = facing
        self.panels.append(self.hull[self.position])

    def run(self, start_position: Position=None, start_colour: int=Black, print_robot=False):
        if start_position is None:
            start_position = Position(0, 0)
        self.reset(start_position)

        if start_colour != self.Black:
            self.hull[self.position] = self.White
            self.panels[0] = self.White

        program = Program(self.init_memory, self.panels, dynamic_memory=True)

        output_pointer = 0
        program.reset_inputs()
        program.reset_memory()
        program.reset_pointers()
        while program.pointer is not None:
            program.pointer = program.execute(program.pointer)

            if len(program.outputs) >= output_pointer + 2:

                if print_robot:
                    for line in robot.hull_as_str(print_robot=False):
                        print(line)
                    print('----')

                print(f'Got outputs: {", ".join(map(str, program.outputs[output_pointer:]))}')

                self.hull[self.position] = program.outputs[output_pointer]
                p, facing = self.position.move(self.facing, program.outputs[output_pointer + 1])
                output_pointer += 2
                self.move_to(p, facing)

        print(f'Robot moved {output_pointer // 2} times')

    def hull_as_str(self, print_robot: bool=False) -> List[str]:
        max_p = Position(0, 0)
        min_p = Position(0, 0)

        for p in self.hull.keys():
            max_p.x = max(max_p.x, p.x)
            min_p.x = min(min_p.x, p.x)

            max_p.y = max(max_p.y, p.y)
            min_p.y = min(min_p.y, p.y)

        if print_robot:
            max_p.x = max(max_p.x, self.position.x)
            min_p.x = min(min_p.x, self.position.x)

            max_p.y = max(max_p.y, self.position.y)
            min_p.y = min(min_p.y, self.position.y)

        rv = []
        for y in range(min_p.y, max_p.y):
            row = ''
            for x in range(min_p.x, max_p.x):
                colour = self.hull.get(Position(x, y), self.Black)

                if print_robot and self.position == Position(x, y):
                    row += self.facing.value
                    continue

                if colour == self.Black:
                    row += ' '
                elif colour == self.White:
                    row += '#'
                else:
                    row += '?'
            rv.append(row)
        return rv


if __name__ == '__main__':

    robot = RobotPainter()
    # robot.run()
    # print(f'The robot ran over {len(robot.hull.keys())} tiles')
    #
    # for line in robot.hull_as_str():
    #     print(line)

    print(f'Re-run on white panel')

    robot.run(start_colour=robot.White, print_robot=True)

    # robot_on_white = RobotPainter(start_colour=RobotPainter.White)
    # robot_on_white.run()
    # print(f'The robot ran over {len(robot_on_white.hull.keys())} tiles')
    #
    for line in robot.hull_as_str():
        print(line)

    # There is a bug somewhere because the output is:
    """
    #  # #  #  ##  ###  #  # #  #  ##  #  #  
    #  # # #  #  # #  # #  # #  # #  # # #   
    #  # # #     # #  # #### #  # #    ###   
    #### ##      # ###  #  # #### #    #  #  
    #  # # #     # #  # #  # #  # #  # #  #
    """
    # Not HKORHHCK
    # Not AKORHACK
