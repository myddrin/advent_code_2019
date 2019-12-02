
from day_02.intcode_parser import Program


def test_add_register():
    prog = Program([1, 0, 0, 0, 99])
    next_pointer = prog.execute(0)
    assert next_pointer == 4  # instruction size
    assert prog.memory == [2, 0, 0, 0, 99]
    assert None == prog.execute(next_pointer), 'It should stop now'


def test_mult_register():
    prog = Program([2, 3, 0, 3, 99])
    next_pointer = prog.execute(0)
    assert next_pointer == 4  # instruction size
    assert prog.memory == [2, 3, 0, 6, 99]
    assert None == prog.execute(next_pointer), 'It should stop now'


def test_mult_store_in_data():
    prog = Program([2, 4, 4, 5, 99, 0])
    next_pointer = prog.execute(0)
    assert next_pointer == 4  # instruction size
    assert prog.memory == [2, 4, 4, 5, 99, 9801]
    assert None == prog.execute(next_pointer), 'It should stop now'


def test_add_then_mult_from_data():
    prog = Program([
        1, 1, 1, 4,
        99, 5, 6, 0,
        99,
    ])
    prog.run()
    assert prog.memory == [30, 1, 1, 4, 2, 5, 6, 0, 99]


def test_only_end():
    prog = Program([99])
    next_pointer = prog.execute(0)
    assert next_pointer is None


def test_step_by_step():
    init_memory = [
        1, 9, 10, 3,
        2, 3, 11, 0,
        99, 30, 40, 50,
    ]
    prog = Program([
        1, 9, 10, 3,
        2, 3, 11, 0,
        99, 30, 40, 50,
    ])
    assert init_memory == prog.memory

    pointer = prog.execute(0)
    assert pointer == 4
    assert [
        1, 9, 10, 70,
        2, 3, 11, 0,
        99, 30, 40, 50,
    ] == prog.memory

    new_pointer = prog.execute(pointer)
    assert new_pointer == pointer + 4
    assert [
        3500, 9, 10, 70,
        2, 3, 11, 0,
        99,
        30, 40, 50,
    ] == prog.memory
    pointer = new_pointer

    new_pointer = prog.execute(pointer)
    assert new_pointer is None
    assert [
        3500, 9, 10, 70,
        2, 3, 11, 0,
        99,
        30, 40, 50,
    ] == prog.memory
