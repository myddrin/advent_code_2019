import logging
from typing import Optional, Tuple

from common.intcode import BaseParserError, Program


class IntCodeProgram(Program):

    @classmethod
    def run_from_file(cls, filename: str, param_a: int, param_b: int, **kwargs) -> "Program":
        program = cls(cls.load_memory_from_file(filename), **kwargs)
        program.run(param_a, param_b)
        return program

    def run(self, param_a: int = None, param_b: int = None) -> int:
        if param_a is not None:
            self.memory[1] = param_a
            self.log_debug(f'param_a={param_a}')
        if param_b is not None:
            self.memory[2] = param_b
            self.log_debug(f'param_b={param_b}')
        super(IntCodeProgram, self).run()

        return self.memory[0]


def brute_force(init_memory, target: int, r: int) -> Optional[Tuple[int, int]]:
    print(f'Brute forcing to read {target}')
    for noun in range(0, r):
        for verb in range(0, r):
            try:
                program = IntCodeProgram([m for m in init_memory])
                program.run(noun, verb)

                if target == program.return_code:
                    return noun, verb

                print(f'Failed {noun}, {verb} => {program.return_code} != {target}')
            except BaseParserError as e:
                print(f'Exception {e.__class__.__name__} for {noun}, {verb}: {str(e)}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    prog = IntCodeProgram.run_from_file('input.txt', 12, 2, verbose=True)
    print(f'Return code is {prog.return_code}')  # 3765464

    # By decompiling the first part we can find that the first instructions are doing:
    # 0: ADD (12, 2, 3)    # *3 = ADD(1, param_b) <=> *3 = 1 + param_b
    # 4: ADD (1, 2, 3)     # *3 = ADD(param_a, param_b) <=> *3 = param_a + param_b
    # so param_a and param_b should be within the memory of the program, so we can limit the maximum number of
    # elements to try to brute force the program
    memory = IntCodeProgram.load_memory_from_file('input.txt')
    found = brute_force(prog, 19690720, len(memory))
    if found is not None:
        a, b = found
        print(f'Found answer: {a}, {b}: {100 * a + b}')  # 76, 10 => 7610
