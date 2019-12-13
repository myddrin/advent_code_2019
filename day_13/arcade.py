from enum import IntEnum, unique
from typing import List, Dict

import attr

from common.intcode import Program, InputError


@unique
class Tile(IntEnum):
    Empty = 0
    Wall = 1
    Block = 2
    HorizontalPaddle = 3
    Ball = 4


@attr.s(hash=True)
class Position:
    x: int = attr.ib()
    y: int = attr.ib()


class Arcade:
    _score_position = Position(-1, 0)

    def __init__(self):
        self.screen: Dict[Position, Tile] = {}
        self.score = 0

    def reset(self):
        self.screen = {}
        self.score = 0

    def print_screen(self):
        max_x = 0
        max_y = 0
        for p in self.screen.keys():
            max_x = max(max_x, p.x)
            max_y = max(max_y, p.y)

        print(f'Score: {self.score}')
        for y in range(0, max_y + 1):
            row = ''
            for x in range(0, max_x + 1):
                t = self.screen.get(Position(x, y), Tile.Empty)
                if t == Tile.Empty:
                    row += ' '
                elif t == Tile.Wall:
                    row += '%'
                elif t == Tile.Block:
                    row += '#'
                elif t == Tile.HorizontalPaddle:
                    row += '_'
                elif t == Tile.Ball:
                    row += 'O'
                else:
                    raise RuntimeError('Unknown tile')
            print(row)

    def run(self, init_memory: List[int], interactive=False, init_inputs=None, auto_play=False):
        self.reset()
        if init_inputs is None:
            inputs = []
        else:
            inputs = init_inputs
        program = Program(init_memory, inputs=inputs, dynamic_memory=True)

        if interactive or auto_play:
            init_memory[0] = 2

        output_idx = 0
        max_blocks = None
        track = {
            Tile.Ball: None,
            Tile.HorizontalPaddle: None,
        }

        while program.pointer is not None:
            try:
                program.pointer = program.execute(program.pointer)

                if len(program.outputs) >= output_idx + 3:

                    # Read one entry
                    pos = Position(
                        program.outputs[output_idx],
                        program.outputs[output_idx + 1],
                    )
                    if pos == self._score_position:
                        self.score = program.outputs[output_idx + 2]
                    else:
                        tile = Tile(program.outputs[output_idx + 2])
                        self.screen[pos] = tile

                        if auto_play and tile in track:
                            print(f'Tracking {tile} as {pos}')
                            track[tile] = pos

            except InputError:
                if interactive:
                    n_blocks = sum((1 for t in self.screen.values() if t == Tile.Block))
                    if max_blocks is None:
                        max_blocks = n_blocks
                    else:
                        print(f'score/block={self.score / max_blocks}')
                    print(f'Pointer: {program.pointer}, inputs={len(inputs)}, n_blocks={n_blocks}')
                    self.print_screen()
                    # Read console to know if we move the joystick
                    key = input('Joystick (Q=left, P=Right): ')
                    if not key:
                        inputs.append(0)
                    elif key.lower() == 'q':
                        inputs.append(-1)
                    elif key.lower() == 'p':
                        inputs.append(1)
                    else:
                        raise
                elif auto_play:
                    if None in track.values():
                        raise
                    ball_pos = track[Tile.Ball]
                    paddle_pos = track[Tile.HorizontalPaddle]

                    if ball_pos.x > paddle_pos.x:
                        inputs.append(1)
                    elif ball_pos.x < paddle_pos.x:
                        inputs.append(-1)
                    else:
                        inputs.append(0)
                    self.print_screen()

        return inputs


if __name__ == '__main__':
    arcade = Arcade()
    # init_inputs = [
    #     1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #     -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 0, 0,
    #     1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #     0, 0, 0, 0, 0,
    #     -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    #     1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #     1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    #     -1, -1, 0, 0,
    #     1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0,
    #     -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #     1, 1, 1, 0, 0, 0, 0, 0, 0, 0,
    #     -1,
    # ]
    # len_ = len(init_inputs)
    inputs = arcade.run(
        Program.load_memory_from_file('input.txt'),
        # interactive=True,
        # init_inputs=init_inputs,
        auto_play=True,
    )

    n_blocks = sum((1 for t in arcade.screen.values() if t == Tile.Block))

    print(f'After running there are {n_blocks} on the screen. The score is {arcade.score}')

    arcade.print_screen()
    # print(f'Saved moves: {inputs[len_:]}')
