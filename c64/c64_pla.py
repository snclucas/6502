from c64.cia import CIA
from c64.sid import SID
from c64.vic import VIC
from simple_memory_space import AddressDecoder

rom_memory_map = {
    "page0_15": {
        "start": 0x0000,
        "end": 0x0FFF
    },
    "page16_127": {
        "start": 0x1000,
        "end": 0x7FFF
    },
    "page128_159": {
        "start": 0x8000,
        "end": 0x9FFF
    },
    "basic_rom": {
        "start": 0xA000,
        "end": 0xBFFF,
        "file": "roms/basic.rom"
    },
    "page192_207": {
        "start": 0xC000,
        "end": 0xCFFF
    },
    "char_rom": {
        "start": 0xD000,
        "end": 0xDFFF,
        "file": "roms/char.rom"
    },
    "kernal_rom": {
        "start": 0xE000,
        "end": 0xFFFF,
        "file": "roms/kernal.rom"
    }

}

io_memory_map = {
    "VICII": {
        "start": 0xD000,
        "end": 0xD3FF
    },
    "SID": {
        "start": 0xD400,
        "end": 0xD7FF
    },
    "colour_ram": {
        "start": 0xD800,
        "end": 0xDBFF
    },
    "CIA1": {
        "start": 0xDC00,
        "end": 0xDCFF
    },
    "CIA2": {
        "start": 0xDD00,
        "end": 0xDDFF
    },
    "IO1": {
        "start": 0xDE00,
        "end": 0xDEFF
    },
    "IO2": {
        "start": 0xDF00,
        "end": 0xDFFF
    },
    "SCREEN": {
        "start": 0x0400,
        "end": 0x07e7
    }
}

zero_page_register_lookup = {
    0x00: "On-Chip I/O DATA Direction Register",
    0x01: "Chip I/O port",

    0xC6: "Number of characters in keyboard buffer",
}


color_ram_map = {

}

io1_map = {

}

io2_map = {

}

sid_map = {

}

screen_map = {

}


def read_binary_file(file_name: str):
    file = open(file_name, "rb")
    binary_data = file.read()
    file.close()
    return binary_data


class C64PLA(AddressDecoder):

    def __init__(self, memspace_size, fill_vals=0x00, verbose=True,
                 vic=None, cia1=None, cia2=None, sid=None):
        self.verbose = verbose
        self.cpu = None

        self.cpu_port_byte = 0b11111
        self.memory_data_ram = ([fill_vals] * memspace_size)
        self.memory_data_rom = ([fill_vals] * memspace_size)
        self.memory_data_io = ([fill_vals] * memspace_size)

        self.vic = vic
        if self.vic is not None:
            self.vic.addressable_memory = self.memory_data_ram
        self.cia1 = cia1
        self.cia2 = cia2
        self.sid = sid
        self.EXROM = 1
        self.GAME = 1

        for mem_space_id, mem_space in rom_memory_map.items():
            if "file" in mem_space:
                data = read_binary_file(file_name=mem_space["file"])
                start = mem_space["start"]
                self.memory_data_rom[start:start + len(data)] = data

    def register_with_cpu(self, cpu):
        self.cpu = cpu
        self.write_byte(address=0x0000, byte=0xEF)  # set the C64 output port defaults
        self.write_byte(address=0x0001, byte=0b111)  # set the C64 output port defaults
        self.cpu_port_byte = self.memory_data_ram[0x0001]

    def set_data(self, start_address, data):
        pass

    def tick(self):
        egg = False
        # pass
        if egg:
            if self.cpu.RW == self.cpu.RW_READ:
                self.cpu.DB = self.read_byte(address=self.cpu.AB)
            else:
                self.write_byte(address=self.cpu.AB, byte=self.cpu.DB)
        else:
            pass

    def _check_device(self, address, read_or_write, word=None):

        # in_VICII_range = io_memory_map['VICII']['start'] <= address <= io_memory_map['VICII']['end']
        # if in_VICII_range:
        #     if read_or_write == "write":
        #         self.vic.write_register(address=address, word=word)
        #     else:
        #         self.vic.read_register(address=address)
        #
        #     return
        #
        # in_CIA1_range = io_memory_map['CIA1']['start'] <= address <= io_memory_map['CIA1']['end']
        # if in_CIA1_range:
        #     if read_or_write == "write":
        #         self.cia1.write_register(address=address, word=word)
        #     else:
        #         self.cia1.read_register(address=address)
        #
        #     return
        #
        # in_CIA2_range = io_memory_map['CIA2']['start'] <= address <= io_memory_map['CIA2']['end']
        # if in_CIA2_range:
        #     if read_or_write == "write":
        #         self.cia2.write_register(address=address, word=word)
        #     else:
        #         self.cia2.read_register(address=address)
        #
        #     return
        #
        # in_SID_range = io_memory_map['SID']['start'] <= address <= io_memory_map['SID']['end']
        # if in_SID_range:
        #     if read_or_write == "write":
        #         self.sid.write_register(address=address, word=word)
        #     else:
        #         self.sid.read_register(address=address)
        #
        #     return
        #
        # if io_memory_map['IO1']['start'] <= address <= io_memory_map['IO1']['end']:
        #     if address in io1_map:
        #         print(f"{read_or_write} IO 1 {io1_map[address]} ")
        #     else:
        #         print(f"{read_or_write} IO 1 {hex(address)} ")
        #
        #     return
        #
        # elif io_memory_map['IO2']['start'] <= address <= io_memory_map['IO2']['end']:
        #     if address in io2_map:
        #         print(f"{read_or_write} IO 2 {io2_map[address]} ")
        #     else:
        #         print(f"{read_or_write} IO 2 {hex(address)} ")
        #
        #     return

        if io_memory_map['colour_ram']['start'] <= address <= io_memory_map['colour_ram']['end']:
            if address in color_ram_map:
                print(f"{read_or_write} color RAM {color_ram_map[address]} ")
            else:
                print(f"{read_or_write} color RAM {hex(address)} ")

            return

        elif io_memory_map['SCREEN']['start'] <= address <= io_memory_map['SCREEN']['end']:
            if address in screen_map:
                print(f"{read_or_write} SCREEN {screen_map[address]} ")
            else:
                print(f"{read_or_write} SCREEN {hex(address)} ")

            return

    #
    # def readdy(self, address):
    #     kBaseAddrBasic = 0xa000
    #     kBaseAddrKernal = 0xe000
    #     kBaseAddrStack = 0x0100
    #     kBaseAddrScreen = 0x0400
    #     kBaseAddrChars = 0xd000
    #     kBaseAddrBitmap = 0x0000
    #     kBaseAddrColorRAM = 0xd800
    #     kAddrResetVector = 0xfffc
    #     kAddrIRQVector = 0xfffe
    #     kAddrNMIVector = 0xfffa
    #     kAddrDataDirection = 0x0000
    #     kAddrMemoryLayout = 0x0001
    #     kAddrColorRAM = 0xd800
    #     kAddrZeroPage = 0x0000
    #     kAddrVicFirstPage = 0xd000
    #     kAddrVicLastPage = 0xd300
    #     kAddrCIA1Page = 0xdc00
    #     kAddrCIA2Page = 0xdd00
    #     kAddrBasicFirstPage = 0xa000
    #     kAddrBasicLastPage = 0xbf00
    #     kAddrKernalFirstPage = 0xe000
    #     kAddrKernalLastPage = 0xff00
    #
    #     kBankBasic = 3
    #     kBankCharen = 5
    #     kBankKernal = 6
    #
    #     page = address & 0xff00
    #
    #     # VIC - II DMA or Character ROM
    #
    #     if page >= kAddrVicFirstPage and page <= kAddrVicLastPage:
    #         if banks_[kBankCharen] == kIO:
    #             retval = vic_->read_register(addr & 0x7f)
    #         elif (banks_[kBankCharen] == kROM):
    #             retval = mem_rom_[addr]
    #         else:
    #             retval = mem_ram_[addr]
    #
    #     # CIA1 * /
    #     elif (page == kAddrCIA1Page):
    #         if (banks_[kBankCharen] == kIO):
    #             retval = cia1_->read_register(addr & 0x0f)
    #         else:
    #             retval = mem_ram_[addr]
    #
    #     # CIA2 * /
    #     elif (page == kAddrCIA2Page):
    #         if (banks_[kBankCharen] == kIO):
    #             retval = cia2_->read_register(addr & 0x0f)
    #         else:
    #             retval = mem_ram_[addr]
    #
    #     # *BASIC or RAM * /
    #     elif (page >= kAddrBasicFirstPage & & page <= kAddrBasicLastPage):
    #         if (banks_[kBankBasic] == kROM):
    #             retval = mem_rom_[addr]
    #         else:
    #             retval = mem_ram_[addr]
    #
    #     # *KERNAL * /
    #     elif (page >= kAddrKernalFirstPage & & page <= kAddrKernalLastPage):
    #         if (banks_[kBankKernal] == kROM):
    #             retval = mem_rom_[addr]
    #         else:
    #             retval = mem_ram_[addr]
    #
    #     # *default * /
    #     else:
    #         retval = mem_ram_[addr]
    #
    #     return retval;




    def mem_select(self, address):
        control_port = self.memory_data_ram[0x0001] & 0x07
        if self.GAME == 1:
            control_port |= (1 << 3)
        else:
            control_port &= ~ (1 << 3)

        if self.EXROM == 1:
            control_port |= (1 << 4)
        else:
            control_port &= ~ (1 << 4)

        #print(f"read: control_port [{control_port}]")

        # control_port &= ~ (1 << 3)
        # control_port &= ~ (1 << 4)
        # control_port &= 0x1F

        readonly = True

        target = None

        in_basic_range = rom_memory_map['basic_rom']['start'] <= address <= rom_memory_map['basic_rom']['end']
        in_kernal_range = rom_memory_map['kernal_rom']['start'] <= address <= rom_memory_map['kernal_rom']['end']
        in_char_or_io_range = rom_memory_map['char_rom']['start'] <= address <= rom_memory_map['char_rom']['end']
        in_cart_low_range = rom_memory_map['page128_159']['start'] <= address <= rom_memory_map['page128_159']['end']

        if control_port == 0 or control_port == 1 or \
                control_port == 4 or control_port == 8 or \
                control_port == 12 or control_port == 24 or control_port == 28:
            target = self.memory_data_ram
            readonly = False

        elif control_port == 2:
            if in_char_or_io_range or in_kernal_range or in_basic_range:
                target = self.memory_data_rom
                readonly = True
            else:
                target = self.memory_data_ram
                readonly = False

        elif control_port == 3:
            if in_char_or_io_range or in_kernal_range or in_basic_range or in_cart_low_range:
                target = self.memory_data_rom
                readonly = True
            else:
                target = self.memory_data_ram
                readonly = False

        elif control_port == 5 or control_port == 13 or control_port == 29:
            if in_char_or_io_range:
                target = self.memory_data_io
                readonly = False
            else:
                target = self.memory_data_ram
                readonly = False

        elif control_port == 6:
            if in_kernal_range or in_basic_range:
                target = self.memory_data_rom
                readonly = True
            elif in_char_or_io_range:
                target = self.memory_data_io
                readonly = False
            else:
                target = self.memory_data_ram
                readonly = False

        elif control_port == 7:
            if in_kernal_range or in_basic_range or in_cart_low_range:
                target = self.memory_data_rom
                readonly = True
            elif in_char_or_io_range:
                target = self.memory_data_io
                readonly = False
            else:
                target = self.memory_data_ram
                readonly = False

        elif control_port == 9 or control_port == 25:
            if in_char_or_io_range:
                target = self.memory_data_rom
                readonly = True
            else:
                target = self.memory_data_ram
                readonly = False

        elif control_port == 10 or control_port == 26:
            if in_char_or_io_range or in_kernal_range:
                target = self.memory_data_rom
                readonly = True
            else:
                target = self.memory_data_ram
                readonly = False

        elif control_port == 11:
            if in_kernal_range or in_basic_range or in_char_or_io_range or in_cart_low_range:
                target = self.memory_data_rom
                readonly = True
            else:
                target = self.memory_data_ram
                readonly = False

        elif control_port == 14:
            if in_char_or_io_range:
                target = self.memory_data_io
                readonly = False
            elif in_kernal_range:
                target = self.memory_data_rom
                readonly = True
            else:
                target = self.memory_data_ram
                readonly = False

        elif control_port == 15:
            if in_char_or_io_range:
                target = self.memory_data_io
                readonly = False
            elif in_kernal_range or in_basic_range or in_cart_low_range:
                target = self.memory_data_rom
                readonly = True
            else:
                target = self.memory_data_ram
                readonly = False

        elif control_port == 16 or control_port == 17 or \
                control_port == 18 or control_port == 19 or \
                control_port == 20 or control_port == 21 or \
                control_port == 22 or control_port == 23:

            if in_char_or_io_range:
                target = self.memory_data_io
                readonly = False
            elif in_kernal_range or in_cart_low_range:
                target = self.memory_data_rom
                readonly = True
            else:
                target = self.memory_data_ram
                readonly = False

        elif control_port == 27:
            if in_basic_range or in_char_or_io_range or in_kernal_range:
                target = self.memory_data_rom
                readonly = True
            else:
                target = self.memory_data_ram
                readonly = False


        elif control_port == 30:
            if in_char_or_io_range:
                target = self.memory_data_io
                readonly = False
            elif in_kernal_range:
                target = self.memory_data_rom
                readonly = True
            else:
                target = self.memory_data_ram
                readonly = False

        elif control_port == 31:
            if in_basic_range or in_kernal_range:
                target = self.memory_data_rom
                readonly = True
            elif in_char_or_io_range:
                target = self.memory_data_io
                readonly = False
            else:
                target = self.memory_data_ram
                readonly = False




        return target, readonly

    def read_byte(self, address):


        #print(f"read: control_port [{control_port}]")
        target, readonly = self.mem_select(address=address)
        return target[address]

        # kLORAM = 1 << 0
        # kHIRAM = 1 << 1
        # kCHAREN = 1 << 2
        # _GAME = 1 << 3
        # _EXROM = 1 << 4
        #
        # hiram = ((control_port & kHIRAM) != 0)
        # loram = ((control_port & kLORAM) != 0)
        # charen = ((control_port & kCHAREN) != 0)
        # game = ((control_port & _GAME) != 0)
        # exrom = ((control_port & _EXROM) != 0)
        #
        # in_basic_range = rom_memory_map['basic_rom']['start'] <= address <= rom_memory_map['basic_rom']['end']
        #
        # if in_basic_range:
        #     if loram and hiram:
        #         return self.memory_data_rom[address]
        #     else:
        #         return self.memory_data_ram[address]
        #
        # in_kernal_range = rom_memory_map['kernal_rom']['start'] <= address <= rom_memory_map['kernal_rom']['end']
        #
        # if in_kernal_range:
        #     if hiram:
        #         return self.memory_data_rom[address]
        #     else:
        #         return self.memory_data_ram[address]
        #
        # in_char_or_io_range = rom_memory_map['char_rom']['start'] <= address <= rom_memory_map['char_rom']['end']
        #
        # if in_char_or_io_range:
        #     if self.verbose:
        #         self._check_device(address=address, read_or_write="read")
        #
        #     if charen and (loram or hiram):
        #         return self.memory_data_io[address]
        #     elif charen and (not loram) and (not hiram):
        #         return self.memory_data_ram[address]
        #     else:
        #         return self.memory_data_rom[address]
        #
        # return self.memory_data_ram[address]

    def write_byte(self, address, byte) -> None:

        #print(f"write: control_port [{byte}]")
        target, readonly = self.mem_select(address=address)
        if not readonly:
            target[address] = byte

        # kLORAM = 1 << 0
        # kHIRAM = 1 << 1
        # kCHAREN = 1 << 2
        #
        # hiram = ((control_port & kHIRAM) != 0)
        # loram = ((control_port & kLORAM) != 0)
        # charen = ((control_port & kCHAREN) != 0)
        #
        # in_basic_range = rom_memory_map['basic_rom']['start'] <= address <= rom_memory_map['basic_rom']['end']
        #
        # if in_basic_range:
        #     if loram and hiram:
        #         # Cannot write to the ROMs
        #         return
        #     else:
        #         self.memory_data_ram[address] = byte
        #         return
        #
        # in_kernal_range = rom_memory_map['kernal_rom']['start'] <= address <= rom_memory_map['kernal_rom']['end']
        #
        # if in_kernal_range:
        #     # if self.memory_data_ram[0x0001] & 0x02:
        #     if hiram:
        #         # Cannot write to the ROMs
        #         return
        #     else:
        #         self.memory_data_ram[address] = byte
        #         return
        #
        # in_char_or_io_range = rom_memory_map['char_rom']['start'] <= address <= rom_memory_map['char_rom']['end']
        # if in_char_or_io_range:
        #     # if self.verbose:
        #     #     self._check_device(address=address, read_or_write="write", word=byte)
        #
        #     if charen and (loram or hiram):
        #         self.memory_data_io[address] = byte
        #         return
        #     elif charen and (not loram) and (not hiram):
        #         self.memory_data_ram[address] = byte
        #         return
        #     else:
        #         # Cannot write to the ROMs
        #         return
        #
        #     # self.memory_data_io[address] = byte
        #     # return
        # #else:
        #     # print(f"Writing {hex(address)} - {hex(byte)}")
        # self.memory_data_ram[address] = byte
        # return

    # def write_word(self, start_address, word) -> None:
    #     in_basic_range = rom_memory_map['basic_rom']['start'] <= start_address <= rom_memory_map['basic_rom']['end']
    #     in_kernal_range = rom_memory_map['kernal_rom']['start'] <= start_address <= rom_memory_map['kernal_rom']['end']
    #     in_char_or_io_range = rom_memory_map['char_rom']['start'] <= start_address <= rom_memory_map['char_rom']['end']
    #
    #     if in_basic_range or in_kernal_range or in_char_or_io_range:
    #         return
    #
    #     c = (word >> 8) & 0xff
    #     f = word & 0xff
    #
    #     if in_char_or_io_range:
    #         self.memory_data_io[start_address] = c
    #     else:
    #         self.memory_data_ram[start_address + 1] = f


# if __name__ == '__main__':
#     pla = C64PLA(memspace_size=1024 * 64)
#     pla.write_byte(address=0x0000, byte=0xEF)  # set the C64 output port defaults
#     pla.write_byte(address=0x0001, byte=0b0111)
#
#     addr = 0xE000
#     pla.write_byte(address=addr, byte=0x53)
#     print(hex(pla.read_byte(address=addr)))
