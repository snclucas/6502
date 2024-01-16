from abc import ABC, abstractmethod


class AddressDecoder(ABC):

    @abstractmethod
    def read_byte(self, address):
        pass

    @abstractmethod
    def write_byte(self, address, byte) -> None:
        pass
    #
    # @abstractmethod
    # def write_word(self, start_address, word) -> None:
    #     pass


class SimpleMemorySpace(AddressDecoder):

    def __init__(self, memspace_size, fill_vals=0x00):
        self.memory_data = ([fill_vals] * memspace_size)

    def set_data(self, start_address, data):
        self.memory_data[start_address:start_address + len(data)] = data

    def read_byte(self, address):
        return self.memory_data[address]

    def write_byte(self, address, byte) -> None:
        self.memory_data[address] = byte

    def write_word(self, start_address, word) -> None:

        c = (word >> 8) & 0xff
        f = word & 0xff

        self.memory_data[start_address] = c
        self.memory_data[start_address+1] = f

    def dump_memory(self, file_name: str = "memdump.bin"):

        for i in range(len(self.memory_data)):
            if self.memory_data[i] < 0:
                self.memory_data[i] = 0

        file = open(file_name, "wb")
        file.write(bytearray(self.memory_data))
        file.close()
