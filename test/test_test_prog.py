

from address_bus import AddressBus
from cpu6502 import CPU6502

from simple_memory_space import SimpleMemorySpace


def read_binary_file(file_name: str):
    file = open(file_name, "rb")
    binary_data = file.read()
    file.close()
    return binary_data


def test_decimal_PROG():
    program = read_binary_file(file_name="./6502_decimal_test.bin")

    address_bus = AddressBus()
    memspace = SimpleMemorySpace(memspace_size=1024 * 64, fill_vals=0x00)
    memspace.set_data(start_address=0x0000, data=program)

    cpu = CPU6502(mem_space=memspace, address_bus=address_bus)
    cpu.reset(initial_program_counter=0x0000)

    old_pc_address = 0x0

    total_instructions = 0
    OK = True

    while OK:

        cycle_counter = cpu.tick()

        if cycle_counter == 0:
            total_instructions += 1

            if total_instructions % 1 == 0:
                print(
                    f"{total_instructions} - PC: {hex(cpu.PC)} / {cpu.PC} "
                    f"A: {hex(cpu.A)}, "
                    f"X: {hex(cpu.X)}, Y: {hex(cpu.Y)}, AB: {hex(cpu.ControlLines.AB)}, "
                    f"ZERO: {hex(cpu.get_cpu_status_flag(cpu.ZERO_FLAG))}, "
                    f"NEG: {hex(cpu.get_cpu_status_flag(cpu.NEGATIVE_FLAG))} "
                    f"RW: {cpu.ControlLines.RW}")

            if old_pc_address == cpu.PC:
                OK = False
                print(
                    f"{total_instructions} - PC: {hex(cpu.PC)} / {cpu.PC} "
                    f"A: {hex(cpu.A)}, "
                    f"X: {hex(cpu.X)}, Y: {hex(cpu.Y)}, AB: {hex(cpu.ControlLines.AB)}, "
                    f"ZERO: {hex(cpu.get_cpu_status_flag(cpu.ZERO_FLAG))}, "
                    f"NEG: {hex(cpu.get_cpu_status_flag(cpu.NEGATIVE_FLAG))} "
                    f"RW: {cpu.ControlLines.RW}")
                break

            old_pc_address = cpu.PC




if __name__ == '__main__':
    test_decimal_PROG()
