from day_05.aircon_check import DiagnosticProgram


def test_aircon_diagnositic():
    memory = DiagnosticProgram.load_memory_from_file('input.txt')

    prog = DiagnosticProgram(memory)
    assert prog.run(1) == 9654885


def test_thermal_diagnostic():
    memory = DiagnosticProgram.load_memory_from_file('input.txt')

    prog = DiagnosticProgram(memory)
    assert prog.run(5) == 7079459
