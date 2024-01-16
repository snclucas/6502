
cia_register_lookup = {
    0xDC00: "Data Port A",
    0xDC01: "Data Port B",
    0xDC02: "Data Direction Register - Port A",
    0xDC03: "Data Direction Register - Port B",
    0xDC04: "Timer A: Low-Byte",
    0xDC05: "Timer A: High-Byte",
    0xDC06: "Timer B: Low-Byte",
    0xDC07: "Timer B: High-Byte",
    0xDC08: "Time-of-Day Clock: 1/10 Seconds",
    0xDC09: "Time-of-Day Clock: Seconds",
    0xDC0A: "Time-of-Day Clock: Minutes",
    0xDC0B: "Time-of-Day Clock: Hours + AM/PM Flag (Bit 7)",
    0xDC0C: "Synchronous Serial I/O Data Buffer",
    0xDC0D: "CIA Interrupt Control Register (Read IRQs/Write Mask)",
    0xDC0E: "CIA Control Register A",
    0xDC0F: "CIA Control Register B",

    0xDD00: "Data Port A",
    0xDD01: "Data Port B",
    0xDD02: "Data Direction Register - Port A",
    0xDD03: "Data Direction Register - Port B",
    0xDD04: "Timer A: Low-Byte",
    0xDD05: "Timer A: High-Byte",
    0xDD06: "Timer B: Low-Byte",
    0xDD07: "Timer B: High-Byte",
    0xDD08: "Time-of-Day Clock: 1/10 Seconds",
    0xDD09: "Time-of-Day Clock: Seconds",
    0xDD0A: "Time-of-Day Clock: Minutes",
    0xDD0B: "Time-of-Day Clock: Hours + AM/PM Flag (Bit 7)",
    0xDD0C: "Synchronous Serial I/O Data Buffer",
    0xDD0D: "CIA Interrupt Control Register (Read IRQs/Write Mask)",
    0xDD0E: "CIA Control Register A",
    0xDD0F: "CIA Control Register B",
}


class CIA:

    def __init__(self, name: str):
        self.name = name

    def tick(self):
        pass

    def read_register(self, address):
        if address in cia_register_lookup:
            print(f"Read {self.name} {cia_register_lookup[address]} ")
        else:
            print(f"Read {self.name} ? ")

    def write_register(self, address, word):
        if address in cia_register_lookup:
            print(f"Write {self.name} {cia_register_lookup[address]} ")
        else:
            print(f"Write {self.name} ? {hex(address)} ")
