import time

from cpu6502 import CPU6502, print_cpu_status

from simple_memory_space import SimpleMemorySpace


def read_binary_file(file_name: str):
    file = open(file_name, "rb")
    binary_data = file.read()
    file.close()
    return binary_data


program = read_binary_file(file_name="./6502_functional.bin")

memspace = SimpleMemorySpace(memspace_size=1024 * 64, fill_vals=0x00)
memspace.set_data(start_address=0x000a, data=program)

cpu = CPU6502(mem_space=memspace)
cpu.reset(initial_program_counter=0x0400)

old_pc_address = 0x0

OK = True

total_cycles = 0
total_instructions = 0

print_instructions = True

start = time.time()

while OK:

    cycles = cpu.tick_complete()
    total_cycles += cycles

    total_instructions += 1

    if print_instructions:

        if (total_instructions % 100000) == 0:
            print_cpu_status(cpu=cpu)

        if old_pc_address == cpu.PC:
            OK = False
            print_cpu_status(cpu=cpu)
            break

        old_pc_address = cpu.PC

print(f"Total instructions: {total_instructions}, total cycles: {total_cycles}")
end = time.time()
print(end - start)

# should be 96,241,364
