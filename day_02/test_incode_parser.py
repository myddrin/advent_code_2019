
from day_02.intcode_parser import brute_force, IntCodeProgram


def test_day_02_first_question():
    prog = IntCodeProgram.run_from_file('input.txt', 12, 2, verbose=True)
    assert prog.return_code == 3765464


def test_day_02_second_question():
    prog = IntCodeProgram.load_memory_from_file('input.txt')
    found = brute_force(prog, 19690720, len(prog))
    assert found[0] == 76
    assert found[1] == 10
