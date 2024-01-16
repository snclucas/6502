from c64.c64_pla import C64PLA, rom_memory_map
from c64.cia import CIA
from c64.sid import SID
from c64.vic import VIC
from cpu6502 import CPU6502

if __name__ == '__main__':
    verbose = False

    vic = VIC(name="VIC")
    cia1 = CIA(name="CIA1")
    cia2 = CIA(name="CIA2")
    sid = SID(name="SID")

    # with lock:
    memspace = C64PLA(memspace_size=1024 * 64, fill_vals=0xFF, verbose=False,
                      vic=vic, cia1=cia1, cia2=cia2, sid=sid)
    cpu = CPU6502(mem_space=memspace)
    memspace.register_with_cpu(cpu=cpu)

    value_to_write = 0x55

    memspace.write_byte(address=0x0001, byte=7)

    for page_range_name, page_range in rom_memory_map.items():
        memspace.write_byte(address=page_range["start"]+10, byte=value_to_write)
        read_value = memspace.read_byte(address=page_range["start"]+10)

        if read_value == value_to_write:
            status = "Writable"
        else:
            status = "readonly"

        print(f"{status}  {page_range_name} ")






