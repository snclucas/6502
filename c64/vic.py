from enum import Enum

vicii_register_lookup = {
    0xD000: "Sprite 0 X-position",
    0xD001: "Sprite 0 Y-position",
    0xD002: "Sprite 1 X-position",
    0xD003: "Sprite 1 Y-position",
    0xD004: "Sprite 2 X-position",
    0xD005: "Sprite 2 Y-position",
    0xD006: "Sprite 3 X-position",
    0xD007: "Sprite 3 Y-position",
    0xD008: "Sprite 4 X-position",
    0xD009: "Sprite 4 Y-position",
    0xD00A: "Sprite 5 X-position",
    0xD00B: "Sprite 5 Y-position",

    0xD00C: "Sprite 6 X-position",
    0xD00D: "Sprite 6 Y-position",

    0xD00E: "Sprite 2 X-position",
    0xD00F: "Sprite 3 Y-position",
    0xD010: "MSBs of X coordinates",
    0xD011: "VIC Control Register 1",

    0xD012: "RASTER counter",

    0xD013: "Light-Pen Latch X Pos",
    0xD014: "Light-Pen Latch Y Pos",
    0xD015: "Sprite display Enable: 1 = Enable",

    0xD016: "VIC Control Register 2",
    0xD017: "Sprite Y expansion",
    0xD018: "VIC Memory Control Register",
    0xD019: "VIC Interrupt Flag Register",

    0xD01A: "IRQ Mask Register: 1 = Interrupt Enabled",
    0xD01B: "Sprite to Background Display Priority: 1 = Sprite",
    0xD01C: "Sprites 0-7 Multi-Color Mode Select:1 = M.C.M.",
    0xD01D: "Sprites 0-7 Expand 2x Horizontal (X)",

    0xD01E: "Sprite to Sprite Collision Detect",
    0xD01F: "Sprite to Background Collision Detect",

    0xD020: "Border Color",
    0xD021: "Background Color 0",
    0xD022: "Background Color 1",
    0xD023: "Background Color 2",
    0xD024: "Background Color 3",

    0xD025: "Sprite Multi-Color Register 0",
    0xD026: "Sprite Multi-Color Register 1",

    0xD027: "Sprite 0 Color",
    0xD028: "Sprite 1 Color",
    0xD029: "Sprite 2 Color",
    0xD02A: "Sprite 3 Color",
    0xD02B: "Sprite 4 Color",
    0xD02C: "Sprite 5 Color",
    0xD02D: "Sprite 6 Color",
    0xD02E: "Sprite 7 Color"

}


class GraphicMode(Enum):
    CharMode = 0
    MCCharMode = 1
    BitmapMode = 2
    MCBitmapMode = 3
    ExtBgMode = 4
    IllegalMode = 5


class VIC:

    def __init__(self, name: str, addressable_memory=None):
        self.name = name
        self.addressable_memory = addressable_memory
        self.graphic_mode = GraphicMode.CharMode

    def tick(self):
        pass

    def read_register(self, address):
        pass

    def write_register(self, address, word):

        if address in vicii_register_lookup:
            print(f"Write {self.name} {vicii_register_lookup[address]} {hex(word)}")

            if address == 0xD011 or address == 0xD016:
                self.set_graphic_mode()

            if address == 0xD011:
                if 0x00100000 & word:
                    print("Setting BMM")
                if 0x01000000 & word:
                    print("Setting ECM")
                if 0x00000111 & word:
                    print("Setting YSCROLL")

            if address == 0xD016:
                if 0x00010000 & word:
                    print("Setting MCM")
                if 0x00000111 & word:
                    print("Setting XSCROLL")

        else:
            print(f"Write {self.name} {hex(word)} ")

    def set_graphic_mode(self):

        ecm = ((self.addressable_memory[0xD011] & (1 << 6)) != 0)
        bmm = ((self.addressable_memory[0xD011] & (1 << 5)) != 0)
        mcm = ((self.addressable_memory[0xD016] & (1 << 4)) != 0)

        if not ecm and not bmm and not mcm:
            self.graphic_mode = GraphicMode.CharMode
        elif not ecm and not bmm and mcm:
            self.graphic_mode = GraphicMode.MCCharMode
        elif not ecm and bmm and not mcm:
            self.graphic_mode = GraphicMode.BitmapMode
        elif not ecm and bmm and mcm:
            self.graphic_mode = GraphicMode.MCBitmapMode
        elif ecm and not bmm and not mcm:
            self.graphic_mode = GraphicMode.ExtBgMode
        else:
            self.graphic_mode = GraphicMode.IllegalMode

        print(f"Setting grpahics model to {self.graphic_mode}")
