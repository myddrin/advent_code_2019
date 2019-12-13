from common.intcode import Program
from day_13.arcade import Arcade, Tile


def test_init_state():
    arcade = Arcade()
    arcade.run(Program.load_memory_from_file('input.txt'))

    n_blocks = sum((1 for t in arcade.screen.values() if t == Tile.Block))

    assert n_blocks == 355
