import logging
from enum import unique, IntEnum
from typing import List, Optional, Dict, Iterable, Any


class BaseParserError(RuntimeError):
    pass


class MemoryFault(BaseParserError):
    pass


class InstructionFault(BaseParserError):
    pass


class InputError(BaseParserError):
    pass


@unique
class OpCode(IntEnum):
    ADD = 1
    MULT = 2
    INPUT = 3
    OUTPUT = 4
    JMP_TRUE = 5
    JMP_FALSE = 6
    LT = 7
    EQ = 8
    ADJ_BASE = 9
    END = 99


@unique
class OpMode(IntEnum):
    POSITION = 0  # address
    IMMEDIATE = 1  # value
    RELATIVE = 2  # on the base pointer


class BaseInstruction:
    code = NotImplemented
    params = 0
    _op_code_size = 100

    @classmethod
    def make_opcode(cls, *args) -> int:
        op_value = cls.code.value
        for i in range(0, cls.params):
            if i < len(args):
                mode = args[i]
            else:
                mode = OpMode.POSITION
            op_value += mode.value * (cls._op_code_size * 10 ** i)

        return op_value

    @classmethod
    def opcode_from_value(cls, op_value: int) -> OpCode:
        try:
            return OpCode(op_value % cls._op_code_size)  # return lowest 2 digits as OP code
        except AttributeError:
            raise InstructionFault(f'Invalid instruction {op_value}')

    def next_pointer(self, pointer):
        return pointer + 1 + self.params

    def param_modes(self, op_value: int) -> List[OpMode]:
        try:
            return [
                OpMode((op_value // (self._op_code_size * 10 ** i)) % 10)
                for i in range(0, self.params)
            ]
        except AttributeError:
            raise InstructionFault(f'Invalid OpMode for {op_value}')

    @classmethod
    def get_values(cls, modes: List[OpMode], args: Iterable[int], program: "Program"):
        rv = []
        for i, a in enumerate(args):
            if modes[i] == OpMode.POSITION:
                rv.append(program.memory[a])
            elif modes[i] == OpMode.IMMEDIATE:
                rv.append(a)
            elif modes[i] == OpMode.RELATIVE:
                rv.append(program.memory[program.data_pointer + a])
            else:
                raise InstructionFault(f'Unexpected OpMode for {cls.code}')

        return rv

    def execute(self, op_value: int, program: "Program", *args):
        raise NotImplementedError

    @classmethod
    def _addr_print(cls, memory: List[int], addr: int) -> str:
        if addr < len(memory):
            return f'*{addr}={memory[addr]}'
        return 'MemoryFault'

    def raw_string(self, op_value: int, *args):
        return f'{op_value} {" ".join(map(str, args))}'

    def params_as_string(self, op_value: int, program: "Program", *args) -> List[str]:
        modes = self.param_modes(op_value)
        params = []
        for i, a in enumerate(args):
            if modes[i] == OpMode.POSITION:
                params.append(self._addr_print(program.memory, a))
            elif modes[i] == OpMode.IMMEDIATE:
                params.append(str(a))

        return params

    def as_string(self, op_value: int, program: "Program", *args):
        params = self.params_as_string(op_value, program, *args)
        return self.raw_string(op_value, *args) + f' # {self.code.name}({", ".join(params)})'


class Base2Inputs1Output(BaseInstruction):
    params = 3

    def get_elements(self, op_value: int, program: "Program", *args):
        modes = self.param_modes(op_value)
        a, b = self.get_values(modes[:-1], args[:-1], program)

        if modes[-1] == OpMode.IMMEDIATE:
            raise InstructionFault(f'Output param of {op_value} cannot be immediate')
        elif modes[-1] == OpMode.POSITION:
            out = args[-1]
        elif modes[-1] == OpMode.RELATIVE:
            out = program.data_pointer + args[-1]
        else:
            raise InstructionFault(f'Unknown output mode for {op_value}')

        return a, b, out

    def as_string(self, op_value: int, program: "Program", *args):
        rv = self.raw_string(op_value, args)
        params = self.params_as_string(op_value, program, *args[:-1])
        rv += f' # *{args[-1]} = {self.code.name}({", ".join(params)})'
        return rv


class AddInstruction(Base2Inputs1Output):
    code = OpCode.ADD

    def execute(self, op_value: int, program: "Program", *args):
        a, b, out = self.get_elements(op_value, program, *args)
        program.memory[out] = a + b
        return True  # continue


class MultInstruction(Base2Inputs1Output):
    code = OpCode.MULT

    def execute(self, op_value: int, program: "Program", *args):
        a, b, out = self.get_elements(op_value, program, *args)
        program.memory[out] = a * b
        return True  # continue


class InputInstruction(BaseInstruction):
    code = OpCode.INPUT
    params = 1  # 1 output

    def execute(self, op_value: int, program: "Program", *args):
        modes = self.param_modes(op_value)

        if modes[0] == OpMode.IMMEDIATE:
            raise InstructionFault(f'Output param of {op_value} cannot be immediate')
        elif modes[0] == OpMode.POSITION:
            program.memory[args[0]] = program.read()
        elif modes[0] == OpMode.RELATIVE:
            program.memory[program.data_pointer + args[0]] = program.read()
        else:
            raise InstructionFault(f'Unknown mode in {op_value}')
        return True  # continue

    def as_string(self, op_value: int, program: "Program", *args):
        rv = self.raw_string(op_value, *args)
        return rv + f' # *{args[-1]} = {self.code.name}()'


class OutputInstruction(BaseInstruction):
    code = OpCode.OUTPUT
    params = 1  # 1 output

    def execute(self, op_value: int, program: "Program", *args):
        modes = self.param_modes(op_value)
        a = self.get_values(modes, args, program)[0]

        program.write(a)
        return True  # continue


class BaseJump(BaseInstruction):

    def __init__(self) -> None:
        super(BaseJump, self).__init__()
        self._changed_pointer_to = None

    def change_pointer(self, pointer: int) -> None:
        if self._changed_pointer_to is not None:
            raise InstructionFault('Still executing a previous JMP')
        self._changed_pointer_to = pointer

    def next_pointer(self, pointer: int) -> int:
        if self._changed_pointer_to is not None:
            rv = self._changed_pointer_to
            self._changed_pointer_to = None
            return rv
        return super(BaseJump, self).next_pointer(pointer)


class JumpIfTrueInstruction(BaseJump):
    code = OpCode.JMP_TRUE
    params = 2  # 2 inputs

    def execute(self, op_value: int, program: "Program", *args):
        modes = self.param_modes(op_value)
        values = self.get_values(modes, args, program)

        if values[0] != 0:
            self.change_pointer(values[1])

        return True  # continue


class JumpIfFalseInstruction(BaseJump):
    code = OpCode.JMP_FALSE
    params = 2  # 2 inputs

    def execute(self, op_value: int, program: "Program", *args):
        modes = self.param_modes(op_value)
        values = self.get_values(modes, args, program)

        if values[0] == 0:
            self.change_pointer(values[1])

        return True  # continue


class LessThanInstruction(Base2Inputs1Output):
    code = OpCode.LT

    def execute(self, op_value: int, program: "Program", *args):
        a, b, out = self.get_elements(op_value, program, *args)
        program.memory[out] = int(a < b)
        return True  # continue


class EqualsInstruction(Base2Inputs1Output):
    code = OpCode.EQ

    def execute(self, op_value: int, program: "Program", *args):
        a, b, out = self.get_elements(op_value, program, *args)
        program.memory[out] = int(a == b)
        return True  # continue


class EndInstruction(BaseInstruction):
    code = OpCode.END

    def execute(self, op_value: int, memory: List[int], *args):
        return False  # stop


class AdjustBaseInstruction(BaseInstruction):
    code = OpCode.ADJ_BASE
    params = 1

    def execute(self, op_value: int, program: "Program", *args):
        modes = self.param_modes(op_value)
        a = self.get_values(modes, args, program)[0]

        program.data_pointer += a
        return True  # continue


class Program:

    class Memory:
        alloc_size = 64

        def __init__(self, init_memory: List[int]):
            self._program = init_memory
            self._memory = []

        def reset(self):
            self._memory = []

        def _allocate(self, mem_offset: int):
            while mem_offset >= len(self._memory):
                self._memory.extend([0] * self.alloc_size)

        def __len__(self):
            return len(self._program) + len(self._memory)

        def __getitem__(self, item: int):
            if item < 0:
                raise MemoryFault('Cannot access negative memory')
            if item < len(self._program):
                return self._program[item]
            mem_offset = item - len(self._program)
            # Allocate on access
            self._allocate(mem_offset)
            # if mem_offset >= len(self._memory):
            # raise MemoryFault(f'Failure when accessing {item} (mem_offset={mem_offset} > {len(self._memory)})')
            try:
                return self._memory[mem_offset]
            except IndexError:
                # That should not happen but just in case...
                raise MemoryFault(f'mem_offset={mem_offset}')

        def __setitem__(self, key: int, value: int):
            if key < 0:
                raise MemoryFault('Cannot set negative memory')

            if key < len(self._program):
                self._program[key] = value
                return

            mem_offset = key - len(self._program)
            self._allocate(mem_offset)
            try:
                self._memory[mem_offset] = value
            except IndexError:
                # That should not happen but just in case...
                raise MemoryFault(f'mem_offset={mem_offset}')

        # TODO(tr) __delitem__?

    @classmethod
    def _add(cls, reg_a: int, reg_b: int):
        return reg_a + reg_b

    @classmethod
    def _mult(cls, reg_a: int, reg_b: int):
        return reg_a * reg_b

    @classmethod
    def _end(cls, *args):
        return

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

    instructions = {
        inst.code: inst()
        for inst in (
            AddInstruction, MultInstruction, EndInstruction,  # day 02
            InputInstruction, OutputInstruction,  # day 05 p1
            JumpIfFalseInstruction, JumpIfTrueInstruction, LessThanInstruction, EqualsInstruction,  # day 05 p2
            AdjustBaseInstruction,  # day 09 p1
        )
    }  # type: Dict[int, BaseInstruction]

    # TODO(tr) make inputs a generator
    def __init__(
        self,
        initial_memory: List[int],
        inputs: List[int]=None,
        dynamic_memory=False,
        verbose=False,
    ) -> None:
        if dynamic_memory:
            self.memory = self.Memory(initial_memory)
        else:
            self.memory = initial_memory
        if verbose:
            self.log = logging.getLogger(self.__class__.__name__)
        else:
            self.log = None

        if inputs is None:
            inputs = []

        self._inputs = inputs
        self._current_input = 0
        self.outputs = []
        self.pointer = 0
        self.data_pointer = 0

    def reset_pointers(self):
        self.pointer = 0
        self.data_pointer = 0

    def reset_inputs(self, inputs=None):
        self._current_input = 0
        if inputs is not None:
            self._inputs = inputs

    def reset_memory(self):
        if isinstance(self.memory, self.Memory):
            self.memory.reset()

    def read(self):
        if self._current_input < len(self._inputs):
            rv = self._inputs[self._current_input]
            self._current_input += 1
            return rv
        raise InputError('No input to read')

    def write(self, value: int):
        self.outputs.append(value)

    def log_debug(self, *args, **kwargs):
        if self.log:
            self.log.debug(*args, **kwargs)

    @property
    def return_code(self) -> Optional[int]:
        if self.memory:
            return self.memory[0]

    def execute(self, pointer: int) -> Optional[int]:
        op_value = None
        parameters = []
        try:
            op_value = self.memory[pointer]
            op = BaseInstruction.opcode_from_value(op_value)

            if op not in self.instructions:
                raise InstructionFault(f'OP {op_value} is not supported - pointer={pointer}')

            instruction = self.instructions[op]

            parameters = []
            for i in range(0, instruction.params):
                parameters.append(self.memory[pointer + 1 + i])

            self.log_debug(f'{pointer}: {instruction.as_string(op_value, self, *parameters)}')
            cont = instruction.execute(op_value, self, *parameters)

            if not cont:
                return None
        except IndexError:
            raise MemoryFault(
                f'On {op_value} PARAM={",".join(map(str, parameters))} - '
                f'pointer={pointer} data_pointer={self.data_pointer}'
            )

        return instruction.next_pointer(pointer)

    def run(self, *args, **kwargs) -> Any:
        self.reset_inputs()
        self.reset_pointers()
        self.reset_memory()
        while self.pointer is not None:
            self.pointer = self.execute(self.pointer)
