

def read_binary_file(file_name: str):
    file = open(file_name, "rb")
    binary_data = file.read()
    file.close()
    return binary_data


def read_t64(file_path: str):
    binary_data = read_binary_file(file_name=file_path)

    signature = binary_data[0:0x20]

    tape_format = (binary_data[0x21] << 8) + binary_data[0x20]
    hex_tape_format = hex(tape_format)

    max_dir_entries = (binary_data[0x23] << 8) + binary_data[0x22]
    hex_max_dir_entries = hex(max_dir_entries)

    used_dir_entries = (binary_data[0x25] << 8) + binary_data[0x24]
    hex_used_dir_entries = hex(used_dir_entries)


    container_name = binary_data[0x28:0x40]

    filetype = binary_data[0x40]
    filetype_1541 = binary_data[0x41]

    d = 4


if __name__ == '__main__':
    file_path = "MISSIMP2.T64"
    read_t64(file_path=file_path)
