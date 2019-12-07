from itertools import permutations
from operator import itemgetter
from typing import List, Iterable, Dict, Tuple

from common.intcode import Program, InputError


class ThrusterAmplifiers:

    def __init__(self, initial_memory: List[int]):
        self._initial_memory = initial_memory

    def run_serial(self, phase_settings: Iterable[int]) -> int:
        current_input = 0
        for i, setting in enumerate(phase_settings):
            prog = Program(
                [m for m in self._initial_memory],
                [setting, current_input],
            )
            prog.run()
            if not prog.outputs:
                raise RuntimeError(f'Setting {i}: {setting} with input {current_input} did not provide output')
            current_input = prog.outputs[0]

        return current_input

    def try_all_serial(self, initial_code: List[int]) -> Tuple[List[int], int]:
        rv: Dict[List[int], int] = {
            sequence: self.run_serial(sequence)
            for sequence in permutations(initial_code)
        }

        print(f'Generated {len(rv)} combinations [serial]')
        # Return the biggest combinaison of setting-output
        sorted_rv = sorted(rv.items(), key=itemgetter(1))  # type: List[Tuple[List[int], int]]
        return sorted_rv[-1]

    def run_parallel(self, phase_settings: List[int], feedback=True) -> int:
        # TODO(tr) Linkling the input to output like that is a bit disgusting, we should create a special generator
        #  so that we can reset the output on the start of run()
        programs = [
            Program([m for m in self._initial_memory]),
        ]
        for i, setting in enumerate(phase_settings[1:], start=1):
            programs[i - 1].outputs = [setting]

            prog = Program([m for m in self._initial_memory], inputs=programs[i - 1].outputs)
            programs.append(prog)

        if feedback:
            programs[-1].outputs = [phase_settings[0], 0]
            programs[0].reset_inputs(programs[-1].outputs)
        else:
            programs[0].reset_inputs([phase_settings[0], 0])

        input_errors = {
            i: False
            for i in range(0, len(programs))
        }
        finished = {
            i: False
            for i in range(0, len(programs))
        }

        global_pointer = 1
        while not all(finished.values()):
            for i, p in enumerate(programs):
                try:
                    if p.pointer is not None:
                        p.pointer = p.execute(p.pointer)
                    else:
                        # print(f'Skipping program {i}')
                        finished[i] = True
                except InputError:
                    # print(f'Ignoring input error from program {i}')  # IO wait
                    input_errors[i] = True
                else:
                    input_errors[i] = False

            if all(input_errors.values()):
                raise RuntimeError('Deadlock')

            global_pointer += 1

        print(f'Done in {global_pointer} iterations')
        return programs[-1].outputs[-1]

    def try_all_parallel(self, initial_code: List[int], feedback=True) -> Tuple[List[int], int]:
        rv: Dict[List[int], int] = {
            settings: self.run_parallel(settings, feedback)
            for settings in permutations(initial_code)
        }

        print(f'Generated {len(rv)} combinations [parallel]')
        # Return the biggest combinaison of setting-output
        sorted_rv = sorted(rv.items(), key=itemgetter(1))  # type: List[Tuple[List[int], int]]
        return sorted_rv[-1]


if __name__ == '__main__':

    thrusters_program = ThrusterAmplifiers(Program.load_memory_from_file('input.txt'))

    settings, output = thrusters_program.try_all_serial([0, 1, 2, 3, 4])
    print(f'Best settings in serial were {", ".join(map(str, settings))} giving {output} to the thrusters')  # 116680

    settings, output = thrusters_program.try_all_parallel([5, 6, 7, 8, 9], feedback=True)
    print(f'Best settings in parallel were {", ".join(map(str, settings))} giving {output} to the thrusters')
    # 89603079
