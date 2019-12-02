import logging
from enum import unique, IntEnum
from typing import List, Optional, Dict, Tuple


class BaseParserError(RuntimeError):
    pass


class MemoryFault(BaseParserError):
    pass


class InstructionFault(BaseParserError):
    pass


@unique
class OpCode(IntEnum):
    ADD = 1
    MULT = 2
    END = 99


class BaseInstruction:
    code = NotImplemented
    params = 0

    @property
    def size(self):
        return 1 + self.params

    def execute(self, memory: List[int], *args):
        raise NotImplementedError

    @classmethod
    def _addr_print(cls, memory: List[int], addr: int) -> str:
        if addr < len(memory):
            if addr == 1:
                return 'param_a'
            elif addr == 2:
                return 'param_b'
            return str(memory[addr])
        return 'MemoryFault'

    def as_string(self, memory, *args):
        return f'{self.code.name} {" ".join(map(str, args))}'


class AddInstruction(BaseInstruction):
    code = OpCode.ADD
    params = 3  # 2 input, 1 output

    def execute(self, memory: List[int], *args):
        addr_a, addr_b, addr_c = args
        memory[addr_c] = memory[addr_a] + memory[addr_b]
        return True  # continue

    def as_string(self, memory, *args):
        rv = super(AddInstruction, self).as_string(memory, args)
        addr_a, addr_b, addr_c = args
        rv += f' # *{addr_c} = {self.code.name}('
        rv += self._addr_print(memory, addr_a) + ', ' + self._addr_print(memory, addr_b)
        rv += ')'
        return rv


class MultInstruction(BaseInstruction):
    code = OpCode.MULT
    params = 3  # 2 input, 1 output

    def execute(self, memory: List[int], *args):
        addr_a, addr_b, addr_c = args
        memory[addr_c] = memory[addr_a] * memory[addr_b]
        return True  # continue

    def as_string(self, memory, *args):
        rv = super(MultInstruction, self).as_string(memory, args)
        addr_a, addr_b, addr_c = args
        rv += f' # *{addr_c} <= {self.code.name}('
        rv += self._addr_print(memory, addr_a) + ', ' + self._addr_print(memory, addr_b)
        rv += ')'
        return rv


class EndInstruction(BaseInstruction):
    code = OpCode.END

    def execute(self, memory: List[int], *args):
        return False  # stop


class Program:

    instructions = {
        inst.code: inst()
        for inst in (AddInstruction, MultInstruction, EndInstruction)
    }  # type: Dict[int, BaseInstruction]

    def __init__(self, initial_memory: List[int], verbose=False) -> None:
        self.memory = initial_memory
        if verbose:
            self.log = logging.getLogger(self.__class__.__name__)
        else:
            self.log = None

    def log_debug(self, *args, **kwargs):
        if self.log:
            self.log.debug(*args, **kwargs)

    @property
    def return_code(self) -> Optional[int]:
        if self.memory:
            return self.memory[0]

    @classmethod
    def _add(cls, reg_a: int, reg_b: int):
        return reg_a + reg_b

    @classmethod
    def _mult(cls, reg_a: int, reg_b: int):
        return reg_a * reg_b

    @classmethod
    def _end(cls, *args):
        return

    def execute(self, pointer: int) -> Optional[int]:
        op = None
        parameters = []
        try:
            op = OpCode(self.memory[pointer])

            if op not in self.instructions:
                raise InstructionFault(f'Wrong OP {op} - pointer={pointer}')

            instruction = self.instructions[op]

            parameters = []
            for i in range(0, instruction.params):
                parameters.append(self.memory[pointer + 1 + i])

            self.log_debug(f'{pointer}: {instruction.as_string(self.memory, *parameters)}')
            cont = instruction.execute(self.memory, *parameters)

            if not cont:
                return None
        except IndexError:
            raise MemoryFault(f'On OP={op} PARAM={",".join(map(str, parameters))} - pointer={pointer}')

        return pointer + instruction.size

    def run(self, param_a: int = None, param_b: int = None) -> int:
        if param_a is not None:
            self.memory[1] = param_a
            self.log_debug(f'param_a={param_a}')
        if param_b is not None:
            self.memory[2] = param_b
            self.log_debug(f'param_b={param_b}')
        pointer = 0
        while pointer is not None:
            pointer = self.execute(pointer)

        return self.memory[0]

    @classmethod
    def load_memory_from_file(cls, filename: str) -> List[int]:
        rv = []
        with open(filename) as f:
            rv += [
                int(entry)
                for line in f
                for entry in line.split(',')
            ]
        return rv

    @classmethod
    def run_from_file(cls, filename: str, param_a: int, param_b: int, **kwargs) -> "Program":
        program = cls(cls.load_memory_from_file(filename), **kwargs)
        program.run(param_a, param_b)
        return program


def brute_force(init_memory, target: int, r: int) -> Optional[Tuple[int, int]]:
    print(f'Brute forcing to read {target}')
    for noun in range(0, r):
        for verb in range(0, r):
            try:
                program = Program([m for m in init_memory])
                program.run(noun, verb)

                if target == program.return_code:
                    return noun, verb

                print(f'Failed {noun}, {verb} => {program.return_code} != {target}')
            except BaseParserError as e:
                print(f'Exception {e.__class__.__name__} for {noun}, {verb}: {str(e)}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    prog = Program.run_from_file('input.txt', 12, 2, verbose=True)
    print(f'Return code is {prog.return_code}')  # 3765464

    # By decompiling the first part we can find that the first instructions are doing:
    # 0: ADD (12, 2, 3)    # *3 = ADD(1, param_b) <=> *3 = 1 + param_b
    # 4: ADD (1, 2, 3)     # *3 = ADD(param_a, param_b) <=> *3 = param_a + param_b
    # so param_a and param_b should be within the memory of the program, so we can limit the maximum number of
    # elements to try to brute force the program
    found = brute_force(Program.load_memory_from_file('input.txt'), 19690720, len(prog.memory))
    if found is not None:
        a, b = found
        print(f'Found answer: {a}, {b}: {100 * a + b}')  # 76, 10 => 7610
