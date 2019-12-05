import pytest

from common.intcode import Program, OpCode, OpMode, BaseInstruction, AddInstruction, MultInstruction


def test_add_register():
    prog = Program([1, 0, 0, 0, 99])
    next_pointer = prog.execute(0)
    assert next_pointer == 4  # instruction size
    assert prog.memory == [2, 0, 0, 0, 99]
    assert prog.execute(next_pointer) is None, 'It should stop now'


def test_mult_register():
    prog = Program([2, 3, 0, 3, 99])
    next_pointer = prog.execute(0)
    assert next_pointer == 4  # instruction size
    assert prog.memory == [2, 3, 0, 6, 99]
    assert prog.execute(next_pointer) is None, 'It should stop now'


def test_mult_store_in_data():
    prog = Program([2, 4, 4, 5, 99, 0])
    next_pointer = prog.execute(0)
    assert next_pointer == 4  # instruction size
    assert prog.memory == [2, 4, 4, 5, 99, 9801]
    assert prog.execute(next_pointer) is None, 'It should stop now'


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


def test_outputs_inputs():
    inputs = [1]
    prog = Program([3, 0, 4, 0, 99], inputs=inputs)
    prog.run()

    assert prog.outputs == inputs


def test_add_values():
    prog = Program([
        AddInstruction.make_opcode(OpMode.IMMEDIATE, OpMode.IMMEDIATE), 8, 8, 0,
        99,
    ])
    prog.execute(0)
    assert prog.memory == [16, 8, 8, 0, 99]


def test_mult_values():
    prog = Program([
        MultInstruction.make_opcode(OpMode.IMMEDIATE, OpMode.IMMEDIATE), 8, 8, 0,
        99,
    ])
    prog.execute(0)
    assert prog.memory == [64, 8, 8, 0, 99]


def test_negative_values():
    prog = Program([
        MultInstruction.make_opcode(OpMode.IMMEDIATE, OpMode.IMMEDIATE), -2, 2, 0,
        AddInstruction.make_opcode(OpMode.POSITION, OpMode.IMMEDIATE), 0, 8, 1,
        99,
    ])
    prog.execute(0)
    assert prog.memory == [-4, -2, 2, 0, 1001, 0, 8, 1, 99]
    prog.execute(4)
    assert prog.memory == [-4, 4, 2, 0, 1001, 0, 8, 1, 99]


@pytest.mark.parametrize('input', (
    8,
    7,
    -1,
    16,
))
def test_eq_position(input):
    prog = Program(
        [
            3, 9, 8, 9, 10, 9, 4, 9, 99, -1, 8,
        ],
        inputs=[input],
    )

    prog.run()
    if input == 8:
        exp = 1
    else:
        exp = 0
    assert prog.outputs == [exp]


@pytest.mark.parametrize('input', (
    8,
    7,
    -1,
    16,
))
def test_less_than_position(input):
    prog = Program(
        [
            3, 9, 7, 9, 10, 9, 4, 9, 99, -1, 8,
        ],
        inputs=[input],
    )

    prog.run()
    if input < 8:
        exp = 1
    else:
        exp = 0
    assert prog.outputs == [exp]


@pytest.mark.parametrize('input', (
    8,
    7,
    -1,
    16,
))
def test_eq_immediate(input):
    prog = Program(
        [
            3, 3, 1108, -1, 8, 3, 4, 3, 99,
        ],
        inputs=[input],
    )

    prog.run()
    if input == 8:
        exp = 1
    else:
        exp = 0
    assert prog.outputs == [exp]


@pytest.mark.parametrize('input', (
    8,
    7,
    -1,
    16,
))
def test_less_than_immediate(input):
    prog = Program(
        [
            3, 3, 1107, -1, 8, 3, 4, 3, 99,
        ],
        inputs=[input],
    )

    prog.run()
    if input < 8:
        exp = 1
    else:
        exp = 0
    assert prog.outputs == [exp]


@pytest.mark.parametrize('input', (
    8,
    0,
    -1,
    16,
))
def test_jump_0_position(input):
    prog = Program(
        [
            3, 12,  # input in *12
            6, 12, 15,  # jmp_false *12 == 0 -> goto *15 (9)
            1, 13, 14, 13,  # add *13(0) + *14(1) -> *13
            4, 13,  # output *13(0 or 1)
            99,  # end (addr=11)
            -1, 0, 1, 9,
        ],
        inputs=[input],
    )

    prog.run()
    if input == 0:
        exp = 0
    else:
        exp = 1
    assert prog.outputs == [exp]


@pytest.mark.parametrize('input', (
    8,
    0,
    -1,
    16,
))
def test_jump_0_immediate(input):
    prog = Program(
        [
            3, 3, 1105, -1, 9, 1101, 0, 0, 12, 4, 12, 99, 1
        ],
        inputs=[input],
    )

    prog.run()
    if input == 0:
        exp = 0
    else:
        exp = 1
    assert prog.outputs == [exp]


@pytest.mark.parametrize('input', (
    7,
    -1,
    8,
    9,
    100,
))
def test_larger_jumper(input):
    """
    The program uses an input instruction to ask for a single number.
    The program will then output 999 if the input value is below 8,
    output 1000 if the input value is equal to 8,
    or output 1001 if the input value is greater than 8.
    """
    prog = Program(
        [
            3, 21, 1008, 21, 8, 20, 1005, 20, 22, 107, 8, 21, 20, 1006, 20, 31,
            1106, 0, 36, 98, 0, 0, 1002, 21, 125, 20, 4, 20, 1105, 1, 46, 104,
            999, 1105, 1, 46, 1101, 1000, 1, 20, 4, 20, 1105, 1, 46, 98, 99,
        ],
        inputs=[input],
    )
    
    prog.run()
    if input < 8:
        exp = 999
    elif input == 8:
        exp = 1000
    else:
        exp = 1001
    assert prog.outputs == [exp]
