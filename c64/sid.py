


sid_register_lookup = {
    0xD400: "Freq. voice 1 low byte",
    0xD401: "Freq. voice 1 high byte",
    0xD402: "pulse wave duty cycle voice 1 low byte",
    0xD403: "pulse wave duty cycle voice 1 high byte",
    0xD404: "control register voice 1",
    0xD405: "attack duration - decay duration",
    0xD406: "sustain level - release duration",

    0xD407: "frequency voice 2 low byte",
    0xD408: "frequency voice 2 high byte",
    0xD409: "pulse wave duty cycle voice 2 low byte",
    0xD40a: "pulse wave duty cycle voice 2 high byte",
    0xD40b: "control register voice 2",
    0xD40c: "attack duration - decay duration",
    0xD40d: "sustain level - release duration",

    0xD40e: "frequency voice 3 low byte",
    0xD40f: "frequency voice 3 high byte",
    0xD410: "pulse wave duty cycle voice 3 low byte",
    0xD411: "pulse wave duty cycle voice 3 high byte",
    0xD412: "control register voice 3",
    0xD413: "attack duration - decay duration",
    0xD414: "sustain level - release duration",


    0xD415: "filter cutoff frequency low byte",
    0xD416: "filter cutoff frequency high byte",
    0xD417: "filter resonance and routing",
    0xD418: "filter resonance - external input - voice 3 - voice 2 - voice 1",


    0xD419: "paddle x value (read only)",
    0xD41a: "paddle y value (read only)",
    0xD41b: "oscillator voice 3 (read only)",
    0xD41c: "envelope voice 3 (read only)",


}


class SID:

    def __init__(self, name: str):
        self.name = name

    def tick(self):
        pass

    def read_register(self, address):
        if address in sid_register_lookup:
            print(f"Read {self.name} {sid_register_lookup[address]} ")
        else:
            print(f"Read {self.name} {hex(address)} ")

    def write_register(self, address, word):
        if address in sid_register_lookup:
            print(f"Write {self.name} {sid_register_lookup[address]} ")
        else:
            print(f"Write {self.name} {hex(address)} - {hex(word)} ")

