import threading
from threading import Thread
from time import sleep

from c64.c64_kernal_jumptable import c64_jmptbl
from c64.c64_pla import C64PLA, read_binary_file
from c64.cia import CIA
from c64.sid import SID
from c64.vic import VIC
from cpu6502 import CPU6502, print_cpu_status
from c64.screen import C64Screen

lock = threading.Lock()

diag_jmp_table = {
    0x97B8: "output timer values					",
    0x83C5: "output \"BAD\" at corresponding ramchip ",
    0x828D: "screen ram (0400) test                ",
    0x830D: "do ram test 1                         ",
    0x8528: "do RAM TEST2                          ",
    0x8765: "do PLA TEST                           ",
    0x8888: "COLOR RAM test                        ",
    0x890E: "KERNAL/BASIC/CHARAC ROM test          ",
    0x8A44: "CASSETTE test                         ",
    0x8B0F: "KEYBOARD                              ",
    0x8BC3: "CONTROL PORT (joystick)               ",
    0x8CFB: "SERIAL PORT TEST                      ",
    0x8DCD: "USER PORT TEST                        ",
    0x8F7C: "TIMER 1A                              ",
    0x8FCA: " B                                    ",
    0x9018: "TIMER 2A ... jani                     ",
    0x9066: " B                                    ",
    0x9242: "INTERRUPT                             ",
    0x9593: "SOUND TEST                            ",
    0x1857: "PRINT BAD                           ",
    0x8348: "fill mem                            ",
    0x8389: "delay                            ",
    0x8366: "do test                           ",
    0x83AA: "ram test 1 \"BAD\"                         ",
    0x84BC: "U21 \"BAD\"                         ",
    0x9492: "6526 U2 \"BAD\"                         ",
    0x94A4: "6526 U1 \"BAD\"                         ",

}

diag_jmp_table2 = {
    0x814A: "test stack memory",
    0x1334: "PLA test",
    0x1336: "PLA test",
    0x9916: "RED ERROR BORDER",
    0x80F2: "mem test pattern",
    0x8218: "ram test",
    0x821A: "ram test 1",
    0x1255: "ram test 2",
    0x932D: "update timer AM        ",
    0x83EF: "color ram test         ",
    0x83F1: "color ram test         ",
    0x843B: "rom check test         ",
    0x843E: "rom check test         ",
    0x84AD: "casette test           ",
    0x8529: "key port test          ",
    0x85DE: "control port test      ",
    0x86E1: "serial port test       ",
    0x8772: "user port test         ",
    0x88A0: "timer 1 a test         ",
    0x88E0: "timer 1 b test         ",
    0x8920: "timer 2 a test         ",
    0x8960: "timer 2 b test         ",
    0x8AAA: "interrupt test         ",
    0x9299: "sound test             ",
}


def print_jmp_table(program_counter):
    if program_counter in diag_jmp_table:
        print(diag_jmp_table[program_counter])
    # else:
    #    print(hex(program_counter))


def print_cpu_state(cpu_: CPU6502):
    print(
        f"PC: {hex(cpu_.PC)} / {cpu_.PC}, INS: {cpu_.current_instruction['syn']} "
        f"A: {hex(cpu_.A)}, "
        f"X: {hex(cpu_.X)}, Y: {hex(cpu_.Y)}, AB: {hex(cpu_.AB)}, "
        f"ZERO: {hex(cpu_.get_cpu_status_flag(cpu_.ZERO_FLAG))}, "
        f"NEG: {hex(cpu_.get_cpu_status_flag(cpu_.NEGATIVE_FLAG))}")


def print_ins_table(cpu_: CPU6502):
    ins_table = {
        "JSR": f"::: {cpu_.current_instruction['syn']} -> ",
        "JMP_ABS": f"::: {cpu_.current_instruction['syn']} -> ",
        "RTS": f"::: {cpu_.current_instruction['syn']} -> "
    }

    if cpu_.current_instruction["syn"] in ins_table:
        if cpu_.current_instruction["syn"] == "JSR":
            # print(ins_table[cpu_.current_instruction["syn"]], end="")
            print_jmp_table(cpu_.PC)

        elif cpu_.current_instruction["syn"] == "JMP_ABS" or cpu_.current_instruction["syn"] == "JMP_IND":
            # print(ins_table[cpu_.current_instruction["syn"]], end="")
            print_jmp_table(cpu_.PC)

        elif cpu_.current_instruction["syn"] == "RTS":
            pass
            # print("RTS")

        else:
            pass


if __name__ == '__main__':
    verbose = True

    vic = VIC(name="VIC")
    cia1 = CIA(name="CIA1")
    cia2 = CIA(name="CIA2")
    sid = SID(name="SID")

    # with lock:
    memspace = C64PLA(memspace_size=1024 * 64, fill_vals=0x00, verbose=False,
                      vic=vic, cia1=cia1, cia2=cia2, sid=sid)
    cpu = CPU6502(mem_space=memspace)
    memspace.register_with_cpu(cpu=cpu)

    # cpu.register_external_device(external_device=vic)
    # cpu.register_external_device(external_device=cia1)
    # cpu.register_external_device(external_device=cia2)
    # cpu.register_external_device(external_device=sid)

    cpu.register_external_device(external_device=memspace)

    # Load a catridge
    # data = read_binary_file(file_name="roms/diag2.bin")
    # data = read_binary_file(file_name="Diag_410/CommodoreDiagRev410.bin")
    # data = read_binary_file(file_name="Diag_586220/diag-c64_586220.bin")
    # start = 0x8000
    # cpu.mem_space.memory_data_ram[start:start + len(data)] = data
    memspace.EXROM = 1
    memspace.GAME = 1
    cpu.mem_space.write_byte(address=0x0001, byte=0b111)

    cpu.reset()


    def poke_thread(cpu_):
        memspace_ = cpu_.mem_space

        sleep(10)
        print("POKE!")


    def screen_thread(cpu_):
        c64_screen = C64Screen(cpu=cpu_)

        while True:
            c64_screen.update()


    def main_thread(cpu_):

        OK = True
        printing = False
        found = False
        found_counter = 0

        # cpu.mem_space.write_byte(address=0x0001, byte=31)

        while OK and not cpu_.pause:

            cpu_.tick_complete()
            # print_cpu_status(cpu=cpu_)

            if verbose:
                print_ins_table(cpu_)

            if cpu_.PC == 0x8528:
                print("HERE")
                printing = True
                found = True
            # #if cpu_.PC == 0x129c and cpu_.X == 0x26 and cpu_.Y == 0xFF:
            #     print("PLA TEst")
            #     printing = True
            #     found = True
            #
            # found_counter += 1
            # if found_counter % 1000 == 0:
            #     print(f"{cpu.mem_space.read_byte(address=0x8015)} {cpu.mem_space.read_byte(address=0x1015)}")

            if cpu_.PC == 0xff5e:
                cpu_.mem_space.write_byte(address=0xD012, byte=0x00)

            if printing:
                print_cpu_state(cpu_=cpu)


    thread1 = Thread(target=main_thread, args=(cpu,))
    thread2 = Thread(target=screen_thread, args=(cpu,))
    thread3 = Thread(target=poke_thread, args=(cpu,))

    thread1.start()
    thread2.start()
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()
