from copy import copy
from typing import List, Callable

from simple_memory_space import AddressDecoder


class CPU6502:
    RW_READ: int = 1
    RW_WRITE: int = 0

    NEGATIVE_FLAG = 0b10000000
    OVERFLOW_FLAG = 0b01000000
    UNUSED_FLAG = 0b00100000
    BREAK_FLAG = 0b00010000
    DEC_MODE_FLAG = 0b00001000
    INT_DIS_FLAG = 0b00000100
    ZERO_FLAG = 0b00000010
    CARRY_FLAG = 0b00000001

    def __init__(self, mem_space: AddressDecoder):
        super().__init__()
        self.name = "6502"
        self.reset_vector: int = 0xFFFC
        self.interrupt_vector: int = 0xFFFE
        self.NMI_vector: int = 0xfffa

        self.A: int = 0x00  # Y Accumulator
        self.X: int = 0x00  # X register
        self.Y: int = 0x00  # Y register
        self.PC: int = 0x0000
        self.SP: int = 0xFF
        self.stack = []

        self.program_counter_low_byte: int = 0x00
        self.program_counter_high_byte: int = 0x00

        self._instruction_tick_counter: int = 0
        self.current_instruction = 0xEA
        self._instruction_operand_address = [0x00, 0x00]
        self._instruction_tasks: List[List[Callable]] = []

        self.DB: int = 0x00
        self.AB: int = 0x0000
        self._temp_address_low_byte: int = 0x00
        self._temp_address_high_byte: int = 0x00
        self.ind_eff_addr_low_byte: int = 0x00
        self.ind_eff_addr_high_byte: int = 0x00

        self.byte_mask: int = ((1 << 8) - 1)
        self.addr_mask: int = ((1 << 16) - 1)
        self.addr_high_mask: int = (self.byte_mask << 8)

        self.SR: int = 0b00000000  # status register

        self.external_devices = []

        self.mem_space = mem_space

        self.pause = False

    def register_external_device(self, external_device):
        self.external_devices.append(external_device)

    def irq(self):
        self._instruction_tasks.append([push_program_counter_low_byte_to_stack,
                                        decrement_stack_pointer])
        self._instruction_tasks.append([push_program_counter_high_byte_to_stack,
                                        decrement_stack_pointer])
        self._instruction_tasks.append([push_proc_status_after_irq_to_stack, decrement_stack_pointer])

        self._instruction_tasks.append([set_program_counter_to_interrupt_vector])  # WRONG this should take more cycles

        self._instruction_tasks.append([set_flags_after_interrupt])

        return

    def nmi(self) -> None:
        self._instruction_tasks.append([push_program_counter_low_byte_to_stack,
                                        decrement_stack_pointer])
        self._instruction_tasks.append([push_program_counter_high_byte_to_stack,
                                        decrement_stack_pointer])
        self._instruction_tasks.append([push_proc_status_after_irq_to_stack, decrement_stack_pointer])

        self._instruction_tasks.append([set_program_counter_to_nmi_vector])  # WRONG this should take more cycles

        self._instruction_tasks.append([set_flags_after_interrupt])

        return

    def reset(self, initial_program_counter=None) -> None:
        self.SP = 0xFF
        self.SR = self.BREAK_FLAG | self.UNUSED_FLAG

        if initial_program_counter is None:
            self.PC = self.reset_vector
            read_operand_low_address_byte(cpu=self)
            read_operand_high_address_byte(cpu=self)
            self.PC = self.AB
        else:
            self.PC = initial_program_counter

    def get_cpu_status_flag(self, flag) -> int:
        if (self.SR & flag) > 0:
            return 1
        else:
            return 0

    def set_cpu_status_flag(self, flag, value) -> None:
        if value == 1:
            self.SR |= flag
        else:
            self.SR &= ~flag

    def fetch_next_byte(self) -> int:
        byte = self.mem_space.read_byte(address=self.PC)
        self.DB = byte
        self.PC += 1
        return byte

    def tick_complete(self) -> int:
        total_cycles = 0
        while True:
            cycle_counter = self.tick()
            total_cycles += 1

            if cycle_counter == 0:
                return total_cycles

    def tick(self) -> int:
        if self._instruction_tick_counter == 0:
            self._load_instruction()
        else:
            next_cycle_tasks = self._instruction_tasks.pop(0)

            for cycle_task in next_cycle_tasks:
                cycle_task(self)

            self._instruction_tick_counter = len(self._instruction_tasks)

        for ext_dev in self.external_devices:
            ext_dev.tick()

        return self._instruction_tick_counter

    def _load_instruction(self):
        self.RW = CPU6502.RW_READ

        instruction = self.mem_space.read_byte(address=self.PC)
        # self.ControlLines.DB = instruction

        if instruction in ins_dict:
            self.current_instruction = ins_dict[instruction]
            self._instruction_tasks = copy(ins_dict[instruction]["instructions"])
            self._instruction_tick_counter = len(self._instruction_tasks)
            self.PC += 1

            return instruction

        else:
            print_cpu_status(cpu=self)
            print(f"Operation not found [{hex(instruction)}]")
            input("Press Enter to continue.")


def print_cpu_status(cpu: CPU6502):
    print(
        f"PC: {hex(cpu.PC)} / {cpu.PC} "
        f"{cpu.current_instruction['syn']}, "
        f"A: {hex(cpu.A)}, "
        f"X: {hex(cpu.X)}, Y: {hex(cpu.Y)}, AB: {hex(cpu.AB)}, "
        f"ZERO: {hex(cpu.get_cpu_status_flag(cpu.ZERO_FLAG))}, "
        f"NEG: {hex(cpu.get_cpu_status_flag(cpu.NEGATIVE_FLAG))} "
        f"RW: {cpu.RW}")


def pull_program_counter_byte_low_from_stack(cpu: CPU6502) -> None:
    cpu.RW = CPU6502.RW_READ
    sp = SPToAddress(cpu=cpu)
    cpu.program_counter_low_byte = cpu.mem_space.read_byte(address=sp)
    cpu.AB = sp

    cpu.PC = (cpu.program_counter_high_byte << 8) + cpu.program_counter_low_byte


def pull_program_counter_byte_high_from_stack(cpu: CPU6502):
    cpu.RW = CPU6502.RW_READ
    sp = SPToAddress(cpu=cpu)
    cpu.program_counter_high_byte = cpu.mem_space.read_byte(address=sp)
    cpu.AB = sp
    cpu.PC = (cpu.program_counter_high_byte << 8) + cpu.program_counter_low_byte


def increment_program_counter(cpu: CPU6502) -> None:
    cpu.PC += 1
    cpu.PC &= ((1 << 16) - 1)


def push_program_counter_low_byte_to_stack(cpu: CPU6502) -> None:
    sp = SPToAddress(cpu=cpu)
    cpu.mem_space.write_byte(address=sp,
                             byte=(cpu.PC >> 8) & cpu.byte_mask)
    cpu.stack.append(hex(cpu.PC >> 8))
    cpu.RW = CPU6502.RW_WRITE
    cpu.AB = sp


def push_program_counter_high_byte_to_stack(cpu: CPU6502) -> None:
    cpu.mem_space.write_byte(address=SPToAddress(cpu=cpu), byte=cpu.PC & 0xFF)
    cpu.stack.append(hex(cpu.PC & cpu.byte_mask))
    cpu.RW = CPU6502.RW_WRITE


def push_proc_status_to_stack(cpu: CPU6502) -> None:
    proc_status = cpu.SR | cpu.BREAK_FLAG | cpu.UNUSED_FLAG
    cpu.mem_space.write_byte(address=SPToAddress(cpu=cpu), byte=proc_status)
    cpu.RW = CPU6502.RW_WRITE


def push_proc_status_after_irq_to_stack(cpu: CPU6502) -> None:
    proc_status = cpu.SR | cpu.UNUSED_FLAG
    cpu.mem_space.write_byte(address=SPToAddress(cpu=cpu), byte=proc_status)


def set_program_counter_to_reset_vector(cpu: CPU6502) -> None:
    cpu.PC = read_word(cpu=cpu, address=cpu.reset_vector)


def set_program_counter_to_interrupt_vector(cpu: CPU6502) -> None:
    cpu.PC = read_word(cpu=cpu, address=cpu.interrupt_vector)
    cpu.RW = CPU6502.RW_READ


def set_program_counter_to_nmi_vector(cpu: CPU6502) -> None:
    cpu.PC = read_word(cpu=cpu, address=cpu.NMI_vector)


def increment_stack_pointer(cpu: CPU6502) -> None:
    cpu.SP += 1  # 1 cycle
    cpu.SP &= ((1 << 8) - 1)
    cpu.AB = cpu.SP


def decrement_stack_pointer(cpu: CPU6502) -> None:
    cpu.SP -= 1  # 1 cycle
    cpu.SP &= ((1 << 8) - 1)
    cpu.AB = cpu.SP


def push_accumulator_to_stack(cpu: CPU6502) -> None:
    sp = SPToAddress(cpu=cpu)
    cpu.RW = CPU6502.RW_WRITE
    cpu.AB = sp
    data = cpu.A & cpu.byte_mask
    cpu.DB = data
    cpu.mem_space.write_byte(address=sp, byte=data)


def pull_accumulator_from_stack(cpu: CPU6502) -> None:
    SP = SPToAddress(cpu=cpu)
    cpu.RW = CPU6502.RW_READ
    cpu.AB = SP
    data = cpu.mem_space.read_byte(address=SPToAddress(cpu=cpu))
    cpu.DB = data
    cpu.A = data


def push_status_register_to_stack(cpu: CPU6502) -> None:
    SP = SPToAddress(cpu=cpu)
    cpu.RW = CPU6502.RW_WRITE
    cpu.AB = SP
    data = (cpu.SR | cpu.BREAK_FLAG | cpu.UNUSED_FLAG) & cpu.byte_mask
    cpu.DB = data
    cpu.mem_space.write_byte(address=SP, byte=data)


def pull_status_register_from_stack(cpu: CPU6502) -> None:
    SP = SPToAddress(cpu=cpu)
    cpu.RW = CPU6502.RW_READ
    cpu.AB = SP
    data = cpu.mem_space.read_byte(address=SP) | cpu.BREAK_FLAG | cpu.UNUSED_FLAG
    cpu.DB = data
    cpu.SR = data


def eor_accumulator_and_temp_data(cpu: CPU6502) -> None:
    cpu.A = (cpu.A ^ cpu.DB)


def and_accumulator_and_temp_data(cpu: CPU6502) -> None:
    cpu.A = cpu.A & cpu.DB


def or_accumulator_and_temp_data(cpu: CPU6502) -> None:
    cpu.A = cpu.A | cpu.DB


def bit_compare(cpu: CPU6502) -> None:
    cpu.SR &= ~(cpu.ZERO_FLAG | cpu.NEGATIVE_FLAG | cpu.OVERFLOW_FLAG)
    if (cpu.A & cpu.DB) == 0:
        cpu.SR |= cpu.ZERO_FLAG
    cpu.SR |= cpu.DB & (cpu.NEGATIVE_FLAG | cpu.OVERFLOW_FLAG)


def rotate_temp_address_left(cpu: CPU6502) -> None:
    """
    The contents of the specified address (accumulator or memory)
    are rotated right by one bit position. The carry goes into bit 7. Bit 0
    sets the new value of the carry.
    """

    existing_carry = cpu.get_cpu_status_flag(flag=cpu.CARRY_FLAG)

    new_carry_bit = get_bit_value(value_in=cpu.DB, bit_number=7)
    rotated_value = rol(cpu.DB, 1, 8)

    if existing_carry == 1:
        rotated_value = set_bit(value=rotated_value, bit_number=0)
    else:
        rotated_value = clear_bit(value=rotated_value, bit_number=0)

    cpu.RW = CPU6502.RW_WRITE
    cpu.DB = rotated_value
    cpu.set_cpu_status_flag(flag=cpu.CARRY_FLAG, value=new_carry_bit)


def rotate_temp_address_right(cpu: CPU6502) -> None:
    """
    The contents of the specified address (accumulator or memory)
    are rotated right by one bit position. The carry goes into bit 7. Bit 0
    sets the new value of the carry.
    """

    existing_carry = cpu.get_cpu_status_flag(flag=cpu.CARRY_FLAG)

    new_carry_bit = get_bit_value(value_in=cpu.DB, bit_number=0)
    rotated_value = ror(cpu.DB, 1, 8)

    if existing_carry == 1:
        rotated_value = set_bit(value=rotated_value, bit_number=7)
    else:
        rotated_value = clear_bit(value=rotated_value, bit_number=7)

    cpu.RW = CPU6502.RW_WRITE
    cpu.DB = rotated_value
    cpu.set_cpu_status_flag(flag=cpu.CARRY_FLAG, value=new_carry_bit)


def rotate_accumulator_left(cpu: CPU6502) -> None:
    """
    The contents of the specified address (accumulator or memory)
    are rotated right by one bit position. The carry goes into bit 7. Bit 0
    sets the new value of the carry.
    """

    existing_carry = cpu.get_cpu_status_flag(flag=cpu.CARRY_FLAG)

    new_carry_bit = get_bit_value(value_in=cpu.A, bit_number=7)
    rotated_value = rol(cpu.A, 1, 8)

    if existing_carry == 1:
        rotated_value = set_bit(value=rotated_value, bit_number=0)
    else:
        rotated_value = clear_bit(value=rotated_value, bit_number=0)

    cpu.RW = CPU6502.RW_WRITE
    cpu.DB = rotated_value
    cpu.A = rotated_value
    cpu.set_cpu_status_flag(flag=cpu.CARRY_FLAG, value=new_carry_bit)


def rotate_accumulator_right(cpu: CPU6502) -> None:
    """
    The contents of the specified address (accumulator or memory)
    are rotated right by one bit position. The carry goes into bit 7. Bit 0
    sets the new value of the carry.
    """

    existing_carry = cpu.get_cpu_status_flag(flag=cpu.CARRY_FLAG)

    new_carry_bit = get_bit_value(value_in=cpu.A, bit_number=0)
    rotated_value = ror(cpu.A, 1, 8)

    if existing_carry == 1:
        rotated_value = set_bit(value=rotated_value, bit_number=7)
    else:
        rotated_value = clear_bit(value=rotated_value, bit_number=7)

    cpu.RW = CPU6502.RW_WRITE
    cpu.DB = rotated_value
    cpu.A = rotated_value
    cpu.set_cpu_status_flag(flag=cpu.CARRY_FLAG, value=new_carry_bit)


def logical_shift_accumulator_right(cpu: CPU6502) -> None:
    new_carry_bit = get_bit_value(value_in=cpu.A, bit_number=0)
    rotated = (cpu.A >> 1) & 0xFF
    rotated = clear_bit(value=rotated, bit_number=7)
    cpu.A = rotated
    cpu.set_cpu_status_flag(flag=cpu.CARRY_FLAG, value=new_carry_bit)


def logical_shift_temp_data_right(cpu: CPU6502) -> None:
    new_carry_bit = get_bit_value(value_in=cpu.DB, bit_number=0)
    rotated = (cpu.DB >> 1) & 0xFF
    rotated = clear_bit(value=rotated, bit_number=7)
    cpu.DB = rotated  # bit 8 will now be zero
    cpu.set_cpu_status_flag(flag=cpu.CARRY_FLAG, value=new_carry_bit)


def arithmetic_shift_temp_data_left(cpu: CPU6502) -> None:
    current_sign_bit = get_bit_value(value_in=cpu.DB, bit_number=7)
    rotated = (cpu.DB << 1) & 0xFF
    rotated = clear_bit(value=rotated, bit_number=0)
    cpu.DB = rotated
    cpu.set_cpu_status_flag(flag=cpu.CARRY_FLAG, value=current_sign_bit)


def arithmetic_shift_accumulator_left(cpu: CPU6502) -> None:
    current_sign_bit = get_bit_value(value_in=cpu.A, bit_number=7)
    rotated = (cpu.A << 1) & 0xFF
    rotated = clear_bit(value=rotated, bit_number=0)
    cpu.A = rotated
    cpu.set_cpu_status_flag(flag=cpu.CARRY_FLAG, value=current_sign_bit)


def branch_equal_to_zero(cpu: CPU6502) -> None:
    if cpu.SR & cpu.ZERO_FLAG:
        cpu.fetch_next_byte()
        branch_rel_addr(cpu=cpu)
    else:
        cpu.PC += 1


def branch_not_equal_to_zero(cpu: CPU6502) -> None:
    if cpu.SR & cpu.ZERO_FLAG:
        cpu.PC += 1
    else:
        cpu.fetch_next_byte()
        branch_rel_addr(cpu=cpu)


def read_operand_byte_to_temp_data(cpu: CPU6502) -> None:
    cpu.fetch_next_byte()


def set_program_counter_to_temp_address_wrap(cpu: CPU6502) -> None:
    cpu.PC = WrapAt(cpu=cpu, addr=cpu.AB)


def set_program_counter_to_temp_address(cpu: CPU6502) -> None:
    cpu.PC = cpu.AB


def read_data_eff_address_low_byte(cpu: CPU6502) -> None:
    cpu.ind_eff_addr_low_byte = cpu.mem_space.read_byte(address=cpu.AB)


def read_data_eff_address_high_byte(cpu: CPU6502) -> None:
    cpu.ind_eff_addr_high_byte = cpu.mem_space.read_byte(address=cpu.AB + 1)


def construct_ind_address(cpu: CPU6502) -> None:
    cpu.AB = (cpu.ind_eff_addr_high_byte << 8) + cpu.ind_eff_addr_low_byte


def WrapAt(cpu: CPU6502, addr):
    wrap = lambda x: (x & cpu.addr_high_mask) + ((x + 1) & cpu.byte_mask)
    return cpu.mem_space.read_byte(address=addr) + (cpu.mem_space.read_byte(address=wrap(addr)) << 8)


def ind_y_extra(cpu: CPU6502):
    a1 = WrapAt(cpu=cpu, addr=cpu.fetch_next_byte())
    cpu.AB = (a1 + cpu.Y) & cpu.byte_mask
    if (a1 & cpu.addr_high_mask) != (cpu.AB & cpu.addr_high_mask):
        # self.excycles += 1
        pass
    cpu.DB = cpu.mem_space.read_byte(address=cpu.AB)


def ind_y(cpu: CPU6502) -> None:
    cpu.AB = (WrapAt(cpu=cpu, addr=cpu.fetch_next_byte()) + cpu.Y) & cpu.addr_mask
    cpu.DB = cpu.mem_space.read_byte(address=cpu.AB)


def add_X_to_address_without_carry(cpu: CPU6502):
    copy_X = copy(cpu.X)

    while copy_X != 0:
        c = cpu._temp_address_low_byte & copy_X
        cpu._temp_address_low_byte = cpu._temp_address_low_byte ^ copy_X
        copy_X = c << 1
    cpu._temp_address_low_byte = 0x00FF & cpu._temp_address_low_byte

    word = (cpu._temp_address_high_byte << 8) + cpu._temp_address_low_byte
    cpu.AB = word


def add_X_to_address(cpu: CPU6502) -> None:
    cpu.AB = (cpu.AB + cpu.X) & cpu.addr_mask


def add_Y_to_address_without_carry(cpu: CPU6502) -> None:
    copy_Y = copy(cpu.Y)

    while copy_Y != 0:
        c = cpu._temp_address_low_byte & copy_Y
        cpu._temp_address_low_byte = cpu._temp_address_low_byte ^ copy_Y
        copy_Y = c << 1
    cpu._temp_address_low_byte = 0x00FF & cpu._temp_address_low_byte

    word = (cpu._temp_address_high_byte << 8) + cpu._temp_address_low_byte
    cpu.AB = word


def add_Y_to_address(cpu: CPU6502) -> None:
    copy_Y = copy(cpu.Y)

    while copy_Y != 0:
        c = cpu.AB & copy_Y
        cpu.AB = cpu.AB ^ copy_Y
        copy_Y = c << 1


def read_operand_low_address_byte(cpu: CPU6502) -> None:
    cpu.RW = CPU6502.RW_READ
    cpu.fetch_next_byte()
    cpu.AB = cpu.PC
    cpu._temp_address_low_byte = cpu.DB
    cpu.AB = (cpu._temp_address_high_byte << 8) + cpu._temp_address_low_byte


def read_operand_high_address_byte(cpu: CPU6502) -> None:
    cpu.RW = CPU6502.RW_READ
    cpu.fetch_next_byte()
    cpu.AB = cpu.PC
    cpu._temp_address_high_byte = cpu.DB
    cpu.AB = (cpu._temp_address_high_byte << 8) + cpu._temp_address_low_byte


def read_zero_to_address_high_byte(cpu: CPU6502) -> None:
    cpu.RW = CPU6502.RW_READ
    cpu._temp_address_high_byte = 0x00
    word = (cpu._temp_address_high_byte << 8) + cpu._temp_address_low_byte
    cpu.AB = word


def save_temp_data_to_temp_address(cpu: CPU6502) -> None:
    cpu.mem_space.write_byte(address=cpu.AB, byte=cpu.DB)


def read_data_from_address(cpu: CPU6502) -> None:
    cpu.RW = CPU6502.RW_READ
    cpu.DB = cpu.mem_space.read_byte(address=cpu.AB)


def save_accumulator_register_to_memory_address(cpu: CPU6502) -> None:
    cpu.RW = CPU6502.RW_WRITE
    cpu.DB = cpu.A
    cpu.mem_space.write_byte(address=cpu.AB, byte=cpu.DB)


def save_temp_data_to_accumulator(cpu: CPU6502) -> None:
    cpu.RW = CPU6502.RW_READ
    cpu.A = cpu.DB


def save_temp_data_to_X_register(cpu: CPU6502) -> None:
    cpu.RW = CPU6502.RW_READ
    cpu.X = cpu.DB


def save_temp_data_to_Y_register(cpu: CPU6502) -> None:
    cpu.RW = CPU6502.RW_READ
    cpu.Y = cpu.DB


def save_X_register_to_memory_address(cpu: CPU6502) -> None:
    cpu.RW = CPU6502.RW_WRITE
    cpu.DB = cpu.X
    cpu.mem_space.write_byte(address=cpu.AB, byte=cpu.DB)


def save_Y_register_to_memory_address(cpu: CPU6502) -> None:
    cpu.RW = CPU6502.RW_WRITE
    cpu.DB = cpu.Y
    cpu.mem_space.write_byte(address=cpu.AB, byte=cpu.DB)


def transfer_X_register_to_accumulator(cpu: CPU6502) -> None:
    cpu.A = cpu.X


def transfer_Y_register_to_accumulator(cpu: CPU6502) -> None:
    cpu.A = cpu.Y


def transfer_accumulator_to_X_register(cpu: CPU6502) -> None:
    cpu.X = cpu.A


def transfer_accumulator_to_Y_register(cpu: CPU6502) -> None:
    cpu.Y = cpu.A


def transfer_stack_pointer_to_X_register(cpu: CPU6502) -> None:
    cpu.X = cpu.SP


def transfer_X_register_to_stack_pointer(cpu: CPU6502) -> None:
    cpu.SP = cpu.X


def increment_temp_data(cpu: CPU6502) -> None:
    cpu.SR &= ~(cpu.ZERO_FLAG | cpu.NEGATIVE_FLAG)
    tbyte = (cpu.DB + 1) & ((1 << 8) - 1)
    if tbyte:
        cpu.SR |= tbyte & cpu.NEGATIVE_FLAG
    else:
        cpu.SR |= cpu.ZERO_FLAG

    cpu.DB = tbyte


def increment_X_register(cpu: CPU6502) -> None:
    if cpu.X == 0xFF:
        cpu.X = 0x00
    else:
        cpu.X += 1


def increment_Y_register(cpu: CPU6502) -> None:
    if cpu.Y == 0xFF:
        cpu.Y = 0x00
    else:
        cpu.Y += 1


def decrement_temp_data(cpu: CPU6502) -> None:
    cpu.SR &= ~(cpu.ZERO_FLAG | cpu.NEGATIVE_FLAG)
    tbyte = (cpu.DB - 1) & ((1 << 8) - 1)
    if tbyte:
        cpu.SR |= tbyte & cpu.NEGATIVE_FLAG
    else:
        cpu.SR |= cpu.ZERO_FLAG

    cpu.DB = tbyte


def decrement_X_register(cpu: CPU6502) -> None:
    if cpu.X == 0x00:
        cpu.X = 0xFF
    else:
        cpu.X -= 1


def decrement_Y_register(cpu: CPU6502) -> None:
    if cpu.Y == 0x00:
        cpu.Y = 0xFF
    else:
        cpu.Y -= 1


def save_temp_data_to_address(cpu: CPU6502) -> None:
    cpu.RW = CPU6502.RW_WRITE
    cpu.mem_space.write_byte(address=cpu.AB, byte=cpu.DB)


def check_temp_data_for_zero_and_neg(cpu: CPU6502) -> None:
    cpu.SR &= ~(cpu.ZERO_FLAG | cpu.NEGATIVE_FLAG)
    if cpu.DB == 0:
        cpu.SR |= CPU6502.ZERO_FLAG
    else:
        cpu.SR |= cpu.DB & cpu.NEGATIVE_FLAG


def check_X_register_for_zero_and_neg(cpu: CPU6502) -> None:
    cpu.SR &= ~(cpu.ZERO_FLAG | cpu.NEGATIVE_FLAG)
    if cpu.X == 0:
        cpu.SR |= CPU6502.ZERO_FLAG
    else:
        cpu.SR |= cpu.X & cpu.NEGATIVE_FLAG


def check_Y_register_for_zero_and_neg(cpu: CPU6502) -> None:
    cpu.SR &= ~(cpu.ZERO_FLAG | cpu.NEGATIVE_FLAG)
    if cpu.Y == 0:
        cpu.SR |= CPU6502.ZERO_FLAG
    else:
        cpu.SR |= cpu.Y & cpu.NEGATIVE_FLAG


def check_accumulator_for_zero_and_neg(cpu: CPU6502) -> None:
    cpu.SR &= ~(cpu.ZERO_FLAG | cpu.NEGATIVE_FLAG)
    if cpu.A == 0:
        cpu.SR |= CPU6502.ZERO_FLAG
    else:
        cpu.SR |= cpu.A & cpu.NEGATIVE_FLAG


# @return the stack pointer as a full 16-bit address (in the 1st page) */
def SPToAddress(cpu: CPU6502) -> int:
    return 0x100 | cpu.SP


def read_word(cpu: CPU6502, address):
    low_byte = cpu.mem_space.read_byte(address=address)
    high_byte = cpu.mem_space.read_byte(address=address + 1)
    return low_byte | (high_byte << 8)


def adc_calc(cpu: CPU6502) -> None:
    data = cpu.DB

    if cpu.SR & cpu.DEC_MODE_FLAG:
        halfcarry = 0
        decimalcarry = 0
        adjust0 = 0
        adjust1 = 0
        nibble0 = (data & 0xf) + (cpu.A & 0xf) + (cpu.SR & cpu.CARRY_FLAG)
        if nibble0 > 9:
            adjust0 = 6
            halfcarry = 1
        nibble1 = ((data >> 4) & 0xf) + ((cpu.A >> 4) & 0xf) + halfcarry
        if nibble1 > 9:
            adjust1 = 6
            decimalcarry = 1

        # the ALU outputs are not decimally adjusted
        nibble0 = nibble0 & 0xf
        nibble1 = nibble1 & 0xf
        aluresult = (nibble1 << 4) + nibble0

        # the final A contents will be decimally adjusted
        nibble0 = (nibble0 + adjust0) & 0xf
        nibble1 = (nibble1 + adjust1) & 0xf
        cpu.SR &= ~(cpu.CARRY_FLAG | cpu.OVERFLOW_FLAG | cpu.NEGATIVE_FLAG | cpu.ZERO_FLAG)
        if aluresult == 0:
            cpu.SR |= cpu.ZERO_FLAG
        else:
            cpu.SR |= aluresult & cpu.NEGATIVE_FLAG
        if decimalcarry == 1:
            cpu.SR |= cpu.CARRY_FLAG
        if (~(cpu.A ^ data) & (cpu.A ^ aluresult)) & cpu.NEGATIVE_FLAG:
            cpu.SR |= cpu.OVERFLOW_FLAG
        cpu.A = (nibble1 << 4) + nibble0
    else:
        if cpu.SR & cpu.CARRY_FLAG:
            tmp = 1
        else:
            tmp = 0
        result = data + cpu.A + tmp
        cpu.SR &= ~(cpu.CARRY_FLAG | cpu.OVERFLOW_FLAG | cpu.NEGATIVE_FLAG | cpu.ZERO_FLAG)
        if (~(cpu.A ^ data) & (cpu.A ^ result)) & cpu.NEGATIVE_FLAG:
            cpu.SR |= cpu.OVERFLOW_FLAG
        data = result
        if data > ((1 << 8) - 1):
            cpu.SR |= cpu.CARRY_FLAG
            data &= ((1 << 8) - 1)
        if data == 0:
            cpu.SR |= cpu.ZERO_FLAG
        else:
            cpu.SR |= data & cpu.NEGATIVE_FLAG
        cpu.A = data


def sbc_calc(cpu: CPU6502) -> None:
    data = cpu.DB

    if cpu.SR & cpu.DEC_MODE_FLAG:
        halfcarry = 1
        decimalcarry = 0
        adjust0 = 0
        adjust1 = 0

        nibble0 = (cpu.A & 0xf) + (~data & 0xf) + (cpu.SR & cpu.CARRY_FLAG)
        if nibble0 <= 0xf:
            halfcarry = 0
            adjust0 = 10
        nibble1 = ((cpu.A >> 4) & 0xf) + ((~data >> 4) & 0xf) + halfcarry
        if nibble1 <= 0xf:
            adjust1 = 10 << 4

        # the ALU outputs are not decimally adjusted
        aluresult = cpu.A + (~data & ((1 << 8) - 1)) + (cpu.SR & cpu.CARRY_FLAG)

        if aluresult > ((1 << 8) - 1):
            decimalcarry = 1
        aluresult &= ((1 << 8) - 1)

        # but the final result will be adjusted
        nibble0 = (aluresult + adjust0) & 0xf
        nibble1 = ((aluresult + adjust1) >> 4) & 0xf

        cpu.SR &= ~(cpu.CARRY_FLAG | cpu.ZERO_FLAG | cpu.NEGATIVE_FLAG | cpu.OVERFLOW_FLAG)
        if aluresult == 0:
            cpu.SR |= cpu.ZERO_FLAG
        else:
            cpu.SR |= aluresult & cpu.NEGATIVE_FLAG
        if decimalcarry == 1:
            cpu.SR |= cpu.CARRY_FLAG
        if ((cpu.A ^ data) & (cpu.A ^ aluresult)) & cpu.NEGATIVE_FLAG:
            cpu.SR |= cpu.OVERFLOW_FLAG
        cpu.A = (nibble1 << 4) + nibble0
    else:
        result = cpu.A + (~data & ((1 << 8) - 1)) + (cpu.SR & cpu.CARRY_FLAG)
        cpu.SR &= ~(cpu.CARRY_FLAG | cpu.ZERO_FLAG | cpu.OVERFLOW_FLAG | cpu.NEGATIVE_FLAG)
        if ((cpu.A ^ data) & (cpu.A ^ result)) & cpu.NEGATIVE_FLAG:
            cpu.SR |= cpu.OVERFLOW_FLAG
        data = result & ((1 << 8) - 1)
        if data == 0:
            cpu.SR |= cpu.ZERO_FLAG
        if result > ((1 << 8) - 1):
            cpu.SR |= cpu.CARRY_FLAG
        cpu.SR |= data & cpu.NEGATIVE_FLAG
        cpu.A = data


def set_carry_flag(cpu: CPU6502) -> None:
    cpu.SR |= CPU6502.CARRY_FLAG


def clear_carry_flag(cpu: CPU6502) -> None:
    cpu.SR &= ~CPU6502.CARRY_FLAG


def set_decimal_flag(cpu: CPU6502) -> None:
    cpu.SR |= CPU6502.DEC_MODE_FLAG


def clear_decimal_flag(cpu: CPU6502) -> None:
    cpu.SR &= ~CPU6502.DEC_MODE_FLAG


def set_break_flag(cpu: CPU6502) -> None:
    cpu.SR |= cpu.BREAK_FLAG


def clear_break_flag(cpu: CPU6502) -> None:
    cpu.SR &= ~CPU6502.BREAK_FLAG


def set_interrupt_flag(cpu: CPU6502) -> None:
    cpu.SR |= cpu.INT_DIS_FLAG


def set_flags_after_interrupt(cpu: CPU6502) -> None:
    cpu.SR &= ~cpu.BREAK_FLAG
    cpu.SR |= cpu.INT_DIS_FLAG


def clear_interrupt_flag(cpu: CPU6502) -> None:
    cpu.SR &= ~CPU6502.INT_DIS_FLAG


def clear_overflow_flag(cpu: CPU6502) -> None:
    cpu.SR &= ~CPU6502.OVERFLOW_FLAG


def compare_temp_data_to_accumulator_register(cpu: CPU6502) -> None:
    cpu.SR &= ~(cpu.CARRY_FLAG | cpu.ZERO_FLAG | cpu.NEGATIVE_FLAG)
    if cpu.A == cpu.DB:
        cpu.SR |= cpu.CARRY_FLAG | cpu.ZERO_FLAG
    elif cpu.A > cpu.DB:
        cpu.SR |= cpu.CARRY_FLAG
    cpu.SR |= (cpu.A - cpu.DB) & cpu.NEGATIVE_FLAG


def compare_temp_data_to_X_register(cpu: CPU6502) -> None:

    cpu.SR &= ~(cpu.CARRY_FLAG | cpu.ZERO_FLAG | cpu.NEGATIVE_FLAG)
    if cpu.X == cpu.DB:
        cpu.SR |= cpu.CARRY_FLAG | cpu.ZERO_FLAG
    elif cpu.X > cpu.DB:
        cpu.SR |= cpu.CARRY_FLAG
    cpu.SR |= (cpu.X - cpu.DB) & cpu.NEGATIVE_FLAG


def compare_temp_data_to_Y_register(cpu: CPU6502) -> None:
    cpu.SR &= ~(cpu.CARRY_FLAG | cpu.ZERO_FLAG | cpu.NEGATIVE_FLAG)
    if cpu.Y == cpu.DB:
        cpu.SR |= cpu.CARRY_FLAG | cpu.ZERO_FLAG
    elif cpu.Y > cpu.DB:
        cpu.SR |= cpu.CARRY_FLAG
    cpu.SR |= (cpu.Y - cpu.DB) & cpu.NEGATIVE_FLAG


def dummy_op(cpu: CPU6502) -> None:
    cpu.A = cpu.A


def branch_if_negative_set(cpu: CPU6502) -> None:
    if cpu.SR & cpu.NEGATIVE_FLAG:
        cpu.fetch_next_byte()
        branch_rel_addr(cpu=cpu)
    else:
        cpu.PC += 1


def branch_if_negative_clear(cpu: CPU6502) -> None:
    if cpu.SR & cpu.NEGATIVE_FLAG:
        cpu.PC += 1
    else:
        cpu.fetch_next_byte()
        branch_rel_addr(cpu=cpu)


def branch_if_carry_set(cpu: CPU6502) -> None:
    if cpu.SR & cpu.CARRY_FLAG:
        cpu.fetch_next_byte()
        branch_rel_addr(cpu=cpu)
    else:
        cpu.PC += 1


def branch_if_carry_clear(cpu: CPU6502) -> None:
    if cpu.SR & cpu.CARRY_FLAG:
        cpu.PC += 1
    else:
        cpu.fetch_next_byte()
        branch_rel_addr(cpu=cpu)


def branch_if_overflow_set(cpu: CPU6502) -> None:
    if cpu.SR & cpu.OVERFLOW_FLAG:
        cpu.fetch_next_byte()
        branch_rel_addr(cpu=cpu)
    else:
        cpu.PC += 1


def branch_if_overflow_clear(cpu: CPU6502) -> None:
    if cpu.SR & cpu.OVERFLOW_FLAG:
        cpu.PC += 1
    else:
        cpu.fetch_next_byte()
        branch_rel_addr(cpu=cpu)


def branch_rel_addr(cpu: CPU6502) -> None:
    # self.excycles += 1
    # addr = self.ImmediateByte()
    # cpu.PC += 1

    if cpu.DB & cpu.NEGATIVE_FLAG:
        cpu.DB = cpu.PC - (cpu.DB ^ ((1 << 8) - 1)) - 1
    else:
        cpu.DB = cpu.PC + cpu.DB

    # addrHighMask = (((1 << 8) - 1) << 8)

    if (cpu.PC & cpu.addr_high_mask) != (cpu.DB & cpu.addr_high_mask):
        cpu._instruction_tasks.append([dummy_op])

    cpu.PC = cpu.DB & ((1 << 16) - 1)


class imdict(dict):
    def __hash__(self):
        return id(self)

    def _immutable(self, *args, **kws):
        raise TypeError('object is immutable')

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear       = _immutable
    update      = _immutable
    setdefault  = _immutable
    pop         = _immutable
    popitem     = _immutable


s = imdict({})

ins_dict = imdict({

    0xE0: {
        "syn": "CPX_IMM",
        "instructions": [
            [read_operand_byte_to_temp_data, compare_temp_data_to_X_register]
        ]
    },

    0xEC: {
        "syn": "CPX_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [read_data_from_address, compare_temp_data_to_X_register]
        ]
    },

    0xE4: {
        "syn": "CPX_ZERO",
        "instructions": [

            [read_operand_low_address_byte, read_zero_to_address_high_byte, read_data_from_address],
            [compare_temp_data_to_X_register]
        ]
    },

    0xC9: {
        "syn": "CMP_IMM",
        "instructions": [
            [read_operand_byte_to_temp_data, compare_temp_data_to_accumulator_register]
        ]
    },

    0xCD: {
        "syn": "CMP_ABS",
        "instructions": [

            [read_operand_low_address_byte],
            [read_operand_high_address_byte, read_data_from_address],
            [compare_temp_data_to_accumulator_register]
        ]
    },

    0xC5: {
        "syn": "CMP_ZERO",
        "instructions": [

            [read_operand_low_address_byte, read_zero_to_address_high_byte, read_data_from_address],
            [compare_temp_data_to_accumulator_register]
        ]
    },

    0xDD: {
        "syn": "CMP_ABS_X",
        "instructions": [

            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                add_X_to_address,
                read_data_from_address],
            [compare_temp_data_to_accumulator_register]
        ]
    },

    0xD9: {
        "syn": "CMP_ABS_Y",
        "instructions": [

            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                add_Y_to_address,
                read_data_from_address],
            [compare_temp_data_to_accumulator_register]
        ]
    },

    0xD5: {
        "syn": "CMP_ZERO_X",
        "instructions": [

            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [
                add_X_to_address_without_carry,
                read_data_from_address
            ],
            [compare_temp_data_to_accumulator_register]
        ]
    },

    0xC1: {
        "syn": "CMP_IND_X",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [add_X_to_address_without_carry],
            [read_data_eff_address_low_byte, read_data_eff_address_high_byte],
            [construct_ind_address, read_data_from_address],
            [compare_temp_data_to_accumulator_register]
        ]
    },

    0xD1: {
        "syn": "CMP_IND_Y",
        "instructions": [
            [ind_y],
            [compare_temp_data_to_accumulator_register]
        ]
    },

    0xCC: {
        "syn": "CPY_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte, read_data_from_address],
            [compare_temp_data_to_Y_register]
        ]
    },

    0xC0: {
        "syn": "CPY_IMM",
        "instructions": [
            [read_operand_byte_to_temp_data, compare_temp_data_to_Y_register]
        ]
    },

    0xC4: {
        "syn": "CPY_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte, read_data_from_address],
            [compare_temp_data_to_Y_register]
        ]
    },

    0x6D: {
        "syn": "ADC_ABS",
        "instructions": [

            [read_operand_low_address_byte],
            [read_operand_high_address_byte, read_data_from_address],
            [adc_calc]
        ]
    },

    0x69: {
        "syn": "ADC_IMM",
        "instructions": [
            [read_operand_byte_to_temp_data, adc_calc]
        ]
    },

    0x65: {
        "syn": "ADC_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte, read_data_from_address],
            [adc_calc]
        ]
    },

    0x7D: {
        "syn": "ADC_ABS_X",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                add_X_to_address,
                read_data_from_address],
            [adc_calc]
        ]
    },

    0x79: {
        "syn": "ADC_ABS_Y",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [add_Y_to_address, read_data_from_address],
            [adc_calc]
        ]
    },

    0x75: {
        "syn": "ADC_ZERO_X",
        "instructions": [
            [read_operand_low_address_byte],
            [read_zero_to_address_high_byte],
            [
                add_X_to_address_without_carry,
                read_data_from_address
            ],
            [adc_calc]
        ]
    },

    0x61: {
        "syn": "ADC_IND_X",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [add_X_to_address_without_carry],
            [read_data_eff_address_low_byte, read_data_eff_address_high_byte],
            [construct_ind_address, read_data_from_address],
            [adc_calc]
        ]
    },

    0x71: {
        "syn": "ADC_IND_Y",
        "instructions": [
            [ind_y],
            [adc_calc]
        ]
    },

    0xED: {
        "syn": "SBC_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte, read_data_from_address],
            [sbc_calc]
        ]
    },

    0xE9: {
        "syn": "SBC_IMM",
        "instructions": [
            [read_operand_byte_to_temp_data, sbc_calc]
        ]
    },

    0xE5: {
        "syn": "SBC_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte, read_data_from_address],
            [sbc_calc]
        ]
    },

    0xFD: {
        "syn": "SBC_ABS_X",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                add_X_to_address,
                read_data_from_address],
            [sbc_calc]
        ]
    },

    0xF9: {
        "syn": "SBC_ABS_Y",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                add_Y_to_address,
                read_data_from_address],
            [sbc_calc]
        ]
    },

    0xF5: {
        "syn": "SBC_ZERO_X",
        "instructions": [
            [read_operand_low_address_byte],
            [read_zero_to_address_high_byte],
            [
                add_X_to_address_without_carry,
                read_data_from_address
            ],
            [sbc_calc]
        ]
    },

    0xE1: {
        "syn": "SBC_IND_Y",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [add_X_to_address_without_carry],
            [read_data_eff_address_low_byte, read_data_eff_address_high_byte],
            [construct_ind_address, read_data_from_address],
            [sbc_calc]
        ]
    },

    0xF1: {
        "syn": "SBC_IND_Y",
        "instructions": [
            [ind_y],
            [sbc_calc]
        ]
    },

    0x90: {
        "syn": "BCC",
        "instructions": [
            [branch_if_carry_clear]

        ]
    },

    0xB0: {
        "syn": "BCS",
        "instructions": [

            [branch_if_carry_set]

        ]
    },

    0xF0: {
        "syn": "BEQ",
        "instructions": [

            [branch_equal_to_zero]

        ]
    },

    0x30: {
        "syn": "BMI",
        "instructions": [

            [branch_if_negative_set]

        ]
    },

    0x8A: {
        "syn": "TXA",
        "instructions": [

            [transfer_X_register_to_accumulator,
             check_accumulator_for_zero_and_neg]

        ]
    },

    0xAA: {
        "syn": "TAX",
        "instructions": [

            [transfer_accumulator_to_X_register,
             check_X_register_for_zero_and_neg]

        ]
    },

    0x98: {
        "syn": "TYA",
        "instructions": [

            [transfer_Y_register_to_accumulator,
             check_accumulator_for_zero_and_neg]

        ]
    },

    0xA8: {
        "syn": "TAY",
        "instructions": [

            [transfer_accumulator_to_Y_register,
             check_Y_register_for_zero_and_neg]

        ]
    },

    0xBA: {
        "syn": "TSX",
        "instructions": [

            [transfer_stack_pointer_to_X_register,
             check_X_register_for_zero_and_neg]

        ]
    },

    0x9A: {
        "syn": "TXS",
        "instructions": [

            [transfer_X_register_to_stack_pointer]

        ]
    },

    0xCE: {
        "syn": "DEC_ABS",
        "instructions": [

            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [read_data_from_address],
            [decrement_temp_data],
            [check_temp_data_for_zero_and_neg, save_temp_data_to_address]

        ]
    },

    0xC6: {
        "syn": "DEC_ZERO",
        "instructions": [

            [read_operand_low_address_byte, read_zero_to_address_high_byte, read_data_from_address],
            [decrement_temp_data],
            [check_temp_data_for_zero_and_neg, save_temp_data_to_address]

        ]
    },

    0xDE: {
        "syn": "DEC_ABS_X",
        "instructions": [

            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                add_X_to_address,
                read_data_from_address],
            [decrement_temp_data],
            [check_temp_data_for_zero_and_neg, save_temp_data_to_address]

        ]
    },

    0xD6: {
        "syn": "DEC_ZERO_X",
        "instructions": [

            [read_operand_low_address_byte],
            [read_zero_to_address_high_byte],
            [
                add_X_to_address_without_carry,
                read_data_from_address
            ],
            [decrement_temp_data],
            [check_temp_data_for_zero_and_neg, save_temp_data_to_address]

        ]
    },

    0x00: {
        "syn": "BRK",
        "instructions": [
            [read_operand_byte_to_temp_data],
            [push_program_counter_low_byte_to_stack,
             decrement_stack_pointer],
            [push_program_counter_high_byte_to_stack,
             decrement_stack_pointer],

            [set_break_flag],
            [push_proc_status_to_stack, decrement_stack_pointer, set_interrupt_flag],
            [set_program_counter_to_interrupt_vector]

        ]
    },

    0x40: {
        "syn": "RTI",
        "instructions": [
            [read_operand_byte_to_temp_data],
            [increment_stack_pointer],
            [pull_status_register_from_stack, increment_stack_pointer],
            [pull_program_counter_byte_low_from_stack, increment_stack_pointer],
            [pull_program_counter_byte_high_from_stack]
        ]
    },

    0xD0: {
        "syn": "BNE",
        "instructions": [[branch_not_equal_to_zero]]
    },

    0x10: {
        "syn": "BPL",
        "instructions": [[branch_if_negative_clear]]
    },

    0x50: {
        "syn": "BVC",
        "instructions": [[branch_if_overflow_clear]]
    },

    0x70: {
        "syn": "BVS",
        "instructions": [[branch_if_overflow_set]]
    },

    0xCA: {
        "syn": "DEX",
        "instructions": [
            [decrement_X_register, check_X_register_for_zero_and_neg]
        ]
    },

    0x88: {
        "syn": "DEY",
        "instructions": [
            [decrement_Y_register, check_Y_register_for_zero_and_neg]
        ]
    },

    0x2D: {
        "syn": "AND_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                read_data_from_address,
                and_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x29: {
        "syn": "AND_IMM",
        "instructions": [
            [
                read_operand_byte_to_temp_data,
                and_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x25: {
        "syn": "AND_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte, read_data_from_address],
            [
                and_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x35: {
        "syn": "AND_ZERO_X",
        "instructions": [

            [read_operand_low_address_byte],
            [read_zero_to_address_high_byte],
            [
                add_X_to_address_without_carry,
                read_data_from_address
            ],

            [
                and_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]

        ]
    },

    0x3D: {
        "syn": "AND_ABS_X",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                add_X_to_address,
                read_data_from_address],
            [
                and_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x39: {
        "syn": "AND_ABS_Y",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                add_Y_to_address,
                read_data_from_address],
            [
                and_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x21: {
        "syn": "AND_IND_X",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [add_X_to_address_without_carry],
            [read_data_eff_address_low_byte, read_data_eff_address_high_byte],
            [construct_ind_address, read_data_from_address],
            [
                and_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x31: {
        "syn": "AND_IND_Y",
        "instructions": [
            [ind_y],
            [
                and_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x0D: {
        "syn": "ORA_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                read_data_from_address,
                or_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x09: {
        "syn": "ORA_IMM",
        "instructions": [
            [
                read_operand_byte_to_temp_data,
                or_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x05: {
        "syn": "ORA_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte, read_data_from_address],
            [
                or_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x15: {
        "syn": "ORA_ZERO_X",
        "instructions": [

            [read_operand_low_address_byte],
            [read_zero_to_address_high_byte],
            [
                add_X_to_address_without_carry,
                read_data_from_address
            ],

            [
                or_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]

        ]
    },

    0x1D: {
        "syn": "ORA_ABS_X",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                add_X_to_address,
                read_data_from_address],
            [
                or_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x19: {
        "syn": "ORA_ABS_Y",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                add_Y_to_address,
                read_data_from_address],
            [
                or_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x01: {
        "syn": "ORA_IND_X",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [add_X_to_address_without_carry],
            [read_data_eff_address_low_byte, read_data_eff_address_high_byte],
            [construct_ind_address, read_data_from_address],
            [
                or_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x11: {
        "syn": "ORA_IND_Y",
        "instructions": [
            [ind_y],
            [
                or_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    # -------------------------------------------------------------------------------------------------------------

    0x4D: {
        "syn": "EOR_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                read_data_from_address,
                eor_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x49: {
        "syn": "EOR_IMM",
        "instructions": [
            [
                read_operand_byte_to_temp_data,
                eor_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x45: {
        "syn": "EOR_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte, read_data_from_address],
            [
                eor_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x55: {
        "syn": "EOR_ZERO_X",
        "instructions": [

            [read_operand_low_address_byte],
            [read_zero_to_address_high_byte],
            [
                add_X_to_address_without_carry,
                read_data_from_address
            ],

            [
                eor_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]

        ]
    },

    0x5D: {
        "syn": "EOR_ABS_X",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                add_X_to_address,
                read_data_from_address],
            [
                eor_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x59: {
        "syn": "EOR_ABS_Y",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                add_Y_to_address,
                read_data_from_address],
            [
                eor_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x41: {
        "syn": "EOR_IND_X",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [add_X_to_address_without_carry],
            [read_data_eff_address_low_byte, read_data_eff_address_high_byte],
            [construct_ind_address, read_data_from_address],
            [
                eor_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x51: {
        "syn": "EOR_IND_Y",
        "instructions": [
            [ind_y],
            [
                eor_accumulator_and_temp_data,
                check_accumulator_for_zero_and_neg
            ]
        ]
    },

    0x8D: {
        "syn": "STA_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                save_accumulator_register_to_memory_address
            ]
        ]
    },

    0x85: {
        "syn": "STA_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte,
             read_data_from_address],
            [
                save_accumulator_register_to_memory_address
            ]
        ]
    },

    0x95: {
        "syn": "STA_ZERO_X",
        "instructions": [
            [read_operand_low_address_byte],
            [read_zero_to_address_high_byte],
            [
                add_X_to_address_without_carry,
                read_data_from_address
            ],
            [
                save_accumulator_register_to_memory_address
            ]
        ]
    },

    0x9D: {
        "syn": "STA_ABS_X",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [add_X_to_address, read_data_from_address],
            [save_accumulator_register_to_memory_address]
        ]
    },

    0x99: {
        "syn": "STA_ABS_Y",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                add_Y_to_address,
                read_data_from_address],

            [
                save_accumulator_register_to_memory_address
            ]]
    },

    0x81: {
        "syn": "STA_IND_X",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [add_X_to_address_without_carry],
            [read_data_eff_address_low_byte, read_data_eff_address_high_byte],
            [construct_ind_address, read_data_from_address],
            [save_accumulator_register_to_memory_address]
        ]
    },

    0x91: {
        "syn": "STA_IND_Y",
        "instructions": [
            [ind_y],
            [
                read_data_from_address,
                save_accumulator_register_to_memory_address
            ]
        ]
    },

    0x8E: {
        "syn": "STX_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                save_X_register_to_memory_address
            ]
        ]
    },

    0x86: {
        "syn": "STX_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte, read_data_from_address],
            [
                save_X_register_to_memory_address
            ]
        ]
    },

    0x96: {
        "syn": "STX_ZERO_Y",
        "instructions": [
            [read_operand_low_address_byte,
             read_zero_to_address_high_byte],
            [
                add_Y_to_address_without_carry,
                read_data_from_address
            ],

            [
                save_X_register_to_memory_address
            ]

        ]
    },

    0x8C: {
        "syn": "STY_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                read_data_from_address, save_Y_register_to_memory_address]
        ]
    },

    0x84: {
        "syn": "STY_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte, read_data_from_address],
            [
                save_Y_register_to_memory_address
            ]
        ]
    },

    0x94: {
        "syn": "STY_ZERO_X",
        "instructions": [
            [read_operand_low_address_byte],
            [read_zero_to_address_high_byte],
            [
                add_X_to_address_without_carry,
                read_data_from_address, save_Y_register_to_memory_address
            ]

        ]
    },

    0xAE: {
        "syn": "LDX_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                read_data_from_address,
                save_temp_data_to_X_register,
                check_X_register_for_zero_and_neg
            ]
        ]
    },

    0xA2: {
        "syn": "LDX_IMM",
        "instructions": [
            [read_operand_byte_to_temp_data, save_temp_data_to_X_register,
             check_X_register_for_zero_and_neg],

        ]
    },

    0xA6: {
        "syn": "LDX_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte, read_data_from_address],
            [
                save_temp_data_to_X_register,
                check_X_register_for_zero_and_neg
            ]
        ]
    },

    0xBE: {
        "syn": "LDX_ABS_Y",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                add_Y_to_address,
                read_data_from_address, save_temp_data_to_X_register,
                check_X_register_for_zero_and_neg]
        ]
    },

    0xB6: {
        "syn": "LDX_ZERO_Y",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [
                add_Y_to_address_without_carry, read_data_from_address],
            [
                save_temp_data_to_X_register,
                check_X_register_for_zero_and_neg]
        ]
    },

    0xAC: {
        "syn": "LDY_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                read_data_from_address,
                save_temp_data_to_Y_register,
                check_Y_register_for_zero_and_neg
            ]
        ]
    },

    0xA0: {
        "syn": "LDY_IMM",
        "instructions": [
            [read_operand_byte_to_temp_data, save_temp_data_to_Y_register,
             check_Y_register_for_zero_and_neg],

        ]
    },

    0xA4: {
        "syn": "LDY_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte, read_data_from_address],
            [
                save_temp_data_to_Y_register,
                check_Y_register_for_zero_and_neg
            ]
        ]
    },

    0xBC: {
        "syn": "LDY_ABS_X",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [add_X_to_address,
             read_data_from_address,
             save_temp_data_to_Y_register,
             check_Y_register_for_zero_and_neg]
        ]
    },

    0xB4: {
        "syn": "LDY_ZERO_X",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [add_X_to_address_without_carry],
            [read_data_from_address,
             save_temp_data_to_Y_register,
             check_Y_register_for_zero_and_neg]
        ]
    },

    0xAD: {
        "syn": "LDA_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                read_data_from_address,
                save_temp_data_to_accumulator,
                check_accumulator_for_zero_and_neg
            ]

        ]
    },

    0xA9: {
        "syn": "LDA_IMM",
        "instructions": [
            [read_operand_byte_to_temp_data, save_temp_data_to_accumulator,
             check_accumulator_for_zero_and_neg]
        ]
    },

    0xBD: {
        "syn": "LDA_ABS_X",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                add_X_to_address,
                read_data_from_address
            ],
            [save_temp_data_to_accumulator,
             check_accumulator_for_zero_and_neg]

        ]
    },

    0xB9: {
        "syn": "LDA_ABS_Y",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [
                add_Y_to_address, read_data_from_address],
            [save_temp_data_to_accumulator,
             check_accumulator_for_zero_and_neg]
        ]
    },

    0xA5: {
        "syn": "LDA_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte, read_data_from_address],
            [save_temp_data_to_accumulator,
             check_accumulator_for_zero_and_neg]

        ]
    },

    0xB5: {
        "syn": "LDA_ZERO_X",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [add_X_to_address_without_carry],
            [read_data_from_address],
            [save_temp_data_to_accumulator,
             check_accumulator_for_zero_and_neg]
        ]
    },

    0xA1: {
        "syn": "LDA_IND_X",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [add_X_to_address_without_carry],
            [read_data_eff_address_low_byte, read_data_eff_address_high_byte],
            [construct_ind_address, read_data_from_address],
            [save_temp_data_to_accumulator,
             check_accumulator_for_zero_and_neg]
        ]
    },

    0xB1: {
        "syn": "LDA_IND_Y",
        "instructions": [
            [ind_y],
            [save_temp_data_to_accumulator,
             check_accumulator_for_zero_and_neg]
        ]
    },

    0x38: {
        "syn": "SEC",
        "instructions": [[set_carry_flag]]
    },

    0xF8: {
        "syn": "SED",
        "instructions": [[set_decimal_flag]]
    },

    0x78: {
        "syn": "SEI",
        "instructions": [[set_interrupt_flag]]
    },

    0x18: {
        "syn": "CLC",
        "instructions": [[clear_carry_flag]]
    },

    0xD8: {
        "syn": "CLD",
        "instructions": [[clear_decimal_flag]]
    },

    0x58: {
        "syn": "CLI",
        "instructions": [[clear_interrupt_flag]]
    },

    0xB8: {
        "syn": "CLV",
        "instructions": [[clear_overflow_flag]]
    },

    0xEA: {
        "syn": "NOP",
        "instructions": [
            [dummy_op]
        ]
    },

    0xe2: {
        "syn": "NOP",
        "instructions": [
            [dummy_op]
        ]
    },

    0xFC: {
        "syn": "NOP",
        "instructions": [
            [dummy_op]
        ]
    },

    0x4C: {
        "syn": "JMP_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [
                read_operand_high_address_byte, read_data_from_address,
                set_program_counter_to_temp_address
            ]
        ]
    },

    0x6C: {
        "syn": "JMP_IND",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [read_data_from_address],
            [set_program_counter_to_temp_address_wrap],

        ]
    },

    0x20: {
        "syn": "JSR",
        "instructions": [
            [read_operand_low_address_byte],
            [push_program_counter_low_byte_to_stack, decrement_stack_pointer],
            [push_program_counter_high_byte_to_stack, decrement_stack_pointer],
            [read_operand_high_address_byte],
            [set_program_counter_to_temp_address]
        ]
    },

    0x60: {
        "syn": "RTS",
        "instructions": [
            [dummy_op],
            [increment_stack_pointer],
            [pull_program_counter_byte_low_from_stack, increment_stack_pointer],
            [pull_program_counter_byte_high_from_stack],
            [increment_program_counter]
        ]
    },

    0x2E: {
        "syn": "ROL_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [read_data_from_address],
            [rotate_temp_address_left],
            [save_temp_data_to_temp_address,
             check_temp_data_for_zero_and_neg]
        ]
    },

    0x26: {
        "syn": "ROL_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [read_data_from_address],
            [rotate_temp_address_left],
            [save_temp_data_to_temp_address,
             check_temp_data_for_zero_and_neg]
        ]
    },

    0x3E: {
        "syn": "ROL_ABS_X",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [add_X_to_address_without_carry],
            [read_data_from_address],
            [rotate_temp_address_left],
            [save_temp_data_to_temp_address,
             check_temp_data_for_zero_and_neg]
        ]
    },

    0x36: {
        "syn": "ROL_ZERO_X",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [add_X_to_address_without_carry],
            [read_data_from_address],
            [rotate_temp_address_left],
            [save_temp_data_to_temp_address,
             check_temp_data_for_zero_and_neg]
        ]
    },

    0x2A: {
        "syn": "ROL_ACC",
        "instructions": [
            [rotate_accumulator_left,
             check_accumulator_for_zero_and_neg]
        ]
    },

    0x6E: {
        "syn": "ROR_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [read_data_from_address],
            [rotate_temp_address_right],
            [save_temp_data_to_temp_address,
             check_temp_data_for_zero_and_neg]
        ]
    },

    0x66: {
        "syn": "ROR_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [read_data_from_address],
            [rotate_temp_address_right],
            [save_temp_data_to_temp_address,
             check_temp_data_for_zero_and_neg]
        ]
    },

    0x7E: {
        "syn": "ROR_ABS_X",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [add_X_to_address_without_carry],
            [read_data_from_address],
            [rotate_temp_address_right],
            [save_temp_data_to_temp_address,
             check_temp_data_for_zero_and_neg]
        ]
    },

    0x76: {
        "syn": "ROR_ZERO_X",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [add_X_to_address_without_carry],
            [read_data_from_address],
            [rotate_temp_address_right],
            [save_temp_data_to_temp_address,
             check_temp_data_for_zero_and_neg]
        ]
    },

    0x6A: {
        "syn": "ROR_ACC",
        "instructions": [
            [rotate_accumulator_right, check_accumulator_for_zero_and_neg]    # cycle 2
        ]
    },

    0xEE: {
        "syn": "INC_ABS",
        "instructions": [
            [read_operand_low_address_byte],    # cycle 2
            [read_operand_high_address_byte],   # cycle 3
            [read_data_from_address],           # cycle 5
            [increment_temp_data],              # cycle 6
            [check_temp_data_for_zero_and_neg,  # cycle 7
             save_temp_data_to_address]
        ]
    },

    0xE6: {
        "syn": "INC_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [read_data_from_address],
            [increment_temp_data],
            [check_temp_data_for_zero_and_neg,
             save_temp_data_to_address]
        ]
    },

    0xFE: {
        "syn": "INC_ABS_X",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [add_X_to_address_without_carry],
            [read_data_from_address],
            [increment_temp_data],
            [check_temp_data_for_zero_and_neg,
             save_temp_data_to_address]
        ]
    },

    0xF6: {
        "syn": "INC_ZERO_X",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [add_X_to_address_without_carry],
            [read_data_from_address],
            [increment_temp_data],
            [check_temp_data_for_zero_and_neg,
             save_temp_data_to_address]
        ]
    },

    0xE8: {
        "syn": "INX",
        "instructions": [
            [increment_X_register, check_X_register_for_zero_and_neg]
        ]
    },

    0xC8: {
        "syn": "INY",
        "instructions": [
            [increment_Y_register, check_Y_register_for_zero_and_neg]
        ]
    },

    0x48: {
        "syn": "PHA",
        "instructions": [
            [dummy_op],  # WRONG
            [push_accumulator_to_stack, decrement_stack_pointer]
        ]
    },

    0x08: {
        "syn": "PHP",
        "instructions": [
            [dummy_op],  # WRONG
            [push_status_register_to_stack, decrement_stack_pointer]
        ]
    },

    0x68: {
        "syn": "PLA",
        "instructions": [
            [increment_stack_pointer, pull_accumulator_from_stack],
            [check_accumulator_for_zero_and_neg],
            [dummy_op],  # WRONG
        ]
    },

    0x28: {
        "syn": "PLP",
        "instructions": [
            [increment_stack_pointer],
            [pull_status_register_from_stack],
            [dummy_op],  # WRONG
        ]
    },

    0x4E: {
        "syn": "LSR_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [read_data_from_address],
            [logical_shift_temp_data_right],
            [save_temp_data_to_temp_address,
             check_temp_data_for_zero_and_neg]
        ]
    },

    0x46: {
        "syn": "LSR_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [read_data_from_address],
            [logical_shift_temp_data_right],
            [save_temp_data_to_temp_address,
             check_temp_data_for_zero_and_neg]
        ]
    },

    0x5E: {
        "syn": "LSR_ABS_X",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [add_X_to_address_without_carry],
            [read_data_from_address],
            [logical_shift_temp_data_right],
            [save_temp_data_to_temp_address,
             check_temp_data_for_zero_and_neg]

        ]
    },

    0x56: {
        "syn": "LSR_ZERO_X",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [add_X_to_address_without_carry],
            [read_data_from_address],
            [logical_shift_temp_data_right],
            [save_temp_data_to_temp_address,
             check_temp_data_for_zero_and_neg]
        ]
    },

    0x4A: {
        "syn": "LSR_ACC",
        "instructions": [
            [logical_shift_accumulator_right,
             check_accumulator_for_zero_and_neg]
        ]
    },

    0x0E: {
        "syn": "ASL_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [read_data_from_address],
            [arithmetic_shift_temp_data_left],
            [save_temp_data_to_temp_address,
             check_temp_data_for_zero_and_neg]
        ]
    },

    0x06: {
        "syn": "ASL_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [read_data_from_address],
            [arithmetic_shift_temp_data_left],
            [save_temp_data_to_temp_address,
             check_temp_data_for_zero_and_neg]
        ]
    },

    0x0A: {
        "syn": "ASL_ACC",
        "instructions": [
            [arithmetic_shift_accumulator_left,
             save_temp_data_to_temp_address,
             check_accumulator_for_zero_and_neg]
        ]
    },
    0x16: {
        "syn": "ASL_ZERO_X",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [add_X_to_address_without_carry],
            [read_data_from_address],
            [arithmetic_shift_temp_data_left],
            [save_temp_data_to_temp_address,
             check_temp_data_for_zero_and_neg]
        ]
    },

    0x1E: {
        "syn": "ASL_ABS_X",
        "instructions": [[read_operand_low_address_byte],
                         [read_operand_high_address_byte],
                         [add_X_to_address_without_carry],
                         [read_data_from_address],
                         [arithmetic_shift_temp_data_left],
                         [save_temp_data_to_temp_address,
                          check_temp_data_for_zero_and_neg]]
    },

    0x24: {
        "syn": "BIT_ZERO",
        "instructions": [
            [read_operand_low_address_byte, read_zero_to_address_high_byte],
            [read_data_from_address, bit_compare]
        ]
    },
    0x2C: {
        "syn": "BIT_ABS",
        "instructions": [
            [read_operand_low_address_byte],
            [read_operand_high_address_byte],
            [read_data_from_address, bit_compare]
        ]
    },
})


def load_prog(cpu: CPU6502, program_code):
    at = 0
    Lo = program_code[at]
    at += 1
    Hi = program_code[at] << 8
    at += 1
    load_address = Lo | Hi

    cpu.mem_space.set_data(start_address=load_address, data=program_code[2:])


# Rotate left: 0b1001 --> 0b0011
rol = lambda val, r_bits, max_bits: \
    (val << r_bits % max_bits) & (2 ** max_bits - 1) | \
    ((val & (2 ** max_bits - 1)) >> (max_bits - (r_bits % max_bits)))

# Rotate right: 0b1001 --> 0b1100
ror = lambda val, r_bits, max_bits: \
    ((val & (2 ** max_bits - 1)) >> r_bits % max_bits) | \
    (val << (max_bits - (r_bits % max_bits)) & (2 ** max_bits - 1))


def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)  # compute negative value
    return val  # return positive value as is


def set_bit(value, bit_number):
    return value | (1 << bit_number)


def clear_bit(value, bit_number):
    return value & ~(1 << bit_number)


def get_bit_value(value_in, bit_number):
    return value_in >> bit_number & 1
