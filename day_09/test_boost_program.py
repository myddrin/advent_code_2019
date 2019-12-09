from common.intcode import Program


def test_copy_itself():
    prog = Program(
        [
            109, 1, 204, -1, 1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99,
        ],
        dynamic_memory=True,
    )
    prog.run()

    assert prog.outputs == [
        109, 1,
        204, -1,
        1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99,
    ]


def test_ouput_16_digit():
    prog = Program(
        [
            1102, 34915192, 34915192, 7, 4, 7, 99, 0,
        ],
        dynamic_memory=True,
    )
    prog.run()

    assert prog.outputs == [1219070632396864]


def test_output_large():
    prog = Program(
        [
            104, 1125899906842624, 99,
        ],
        dynamic_memory=True,
    )
    prog.run()

    assert prog.outputs == [1125899906842624]


def test_question_1():
    test_prog = Program(
        Program.load_memory_from_file('input.txt'),
        inputs=[1],
        dynamic_memory=True,
    )

    test_prog.run()

    assert test_prog.outputs == [3638931938]


def test_slow_question_2():
    boost_prog = Program(
        Program.load_memory_from_file('input.txt'),
        inputs=[2],
        dynamic_memory=True,
    )

    boost_prog.run()

    assert boost_prog.outputs == [86025]
