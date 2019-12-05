import logging

from common.intcode import Program


class DiagnosticProgram(Program):

    def __init__(self, *args, **kwargs):
        super(DiagnosticProgram, self).__init__(*args, **kwargs)

    def run(self, system: int) -> int:
        self.reset_inputs([system])
        super(DiagnosticProgram, self).run()
        return self.outputs[-1]


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    init_memory = DiagnosticProgram.load_memory_from_file('input.txt')

    prog = DiagnosticProgram([m for m in init_memory], verbose=True)
    diagnostic_code = prog.run(1)
    print(f'Outputs are {", ".join(map(str, prog.outputs))}')
    print(f'Aircon diagnostic is {diagnostic_code}')  # 9654885

    # Just in case the memory is modified
    prog = DiagnosticProgram([m for m in init_memory])
    diagnostic_code = prog.run(5)
    print(f'Outputs are {", ".join(map(str, prog.outputs))}')
    print(f'Thermal radiator diagnostic is {diagnostic_code}')  # 7079459
