
import sys

import pygame
from pygame.locals import *

from c64 import screen_code_dict, char_to_ascii
from cpu6502 import CPU6502

"""
COLOR_BLACK = 0
COLOR_WHITE = 1
COLOR_RED = 2
COLOR_CYAN = 3
COLOR_VIOLET = 4
COLOR_GREEN = 5
COLOR_BLUE = 6
COLOR_YELLOW = 7
COLOR_ORANGE = 8
COLOR_BROWN = 9
COLOR_LTRED = 10
COLOR_GREY1 = 11
COLOR_GREY2 = 12
COLOR_LTGREEN = 13
COLOR_LTBLUE = 14
COLOR_GREY3 = 15
"""
colors = {
    0: (0, 0, 0),
    1: (255, 255, 255),
    2: (136, 0, 0),
    3: (170, 255, 238),
    4: (204, 68, 204),
    5: (0, 204, 85),
    6: (0, 0, 170),
    7: (238, 238, 119),
    8: (	221, 136, 85),
    9: (102, 68, 0),
    10: (255, 119, 119	),
    11: (51, 51, 51),
    12: (119, 119, 119),
    13: (170, 255, 102),
    14: (0, 136, 255),
    15: (187, 187, 187),
    255: (187, 187, 187),
}

def get_color(colour_code: int):
    if colour_code in colors:
        return colors[colour_code]
    else:
        return colors[15]


class C64Screen:

    def __init__(self, cpu: CPU6502):
        pygame.init()
        self.cpu = cpu
        self.mem_space = cpu.mem_space

        self.DISPLAYSURF = pygame.display.set_mode((403 * 2, 284 * 2))

        pygame.display.set_caption("Commodore 64")

        # Assign FPS a value
        self.FPS = 300
        self.FramePerSec = pygame.time.Clock()

    @staticmethod
    def screen_code_to_character(screen_code: int):
        if screen_code in screen_code_dict:
            return screen_code_dict[screen_code]
        else:
            return "?"

    @staticmethod
    def memory_location_to_screen_location(memory_location: int, starting_address: int):
        memory_location -= starting_address
        x = memory_location % 40
        memory_location -= x
        y = int(memory_location / 40)
        return x, y

    @staticmethod
    def screen_location_to_memory_location(x: int, y: int, starting_address: int):
        return starting_address + y * 40 + x

    def update(self):
        background_color_code = self.mem_space.memory_data_io[53281]
        border_color_code = self.mem_space.memory_data_io[53280]

        background_color = get_color(background_color_code)
        border_color = get_color(border_color_code)

        self.DISPLAYSURF.fill(background_color)

        pygame.draw.rect(
            self.DISPLAYSURF,
            border_color,
            rect=(0,
                  0, 403 * 2, 284 * 2),
            width=41 * 2)

        font = pygame.font.Font('C64_Pro_Mono-STYLE.ttf', 16)

        for x in range(40):
            for y in range(25):
                mem_loc = self.screen_location_to_memory_location(x=x, y=y, starting_address=1024)
                coloar_mem_loc = self.screen_location_to_memory_location(x=x, y=y, starting_address=0xD800)
                screen_code = self.mem_space.memory_data_ram[mem_loc]
                letter = self.screen_code_to_character(screen_code=screen_code)

                color_code = self.mem_space.memory_data_io[coloar_mem_loc]
                color = get_color(color_code)

                let = font.render(letter, True, color)
                self.DISPLAYSURF.blit(let, (41*2 + x*16, 41*2 + y*16))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                if self.cpu.pause:
                    self.cpu.pause = False
                    print("Setting pause FALSE")
                else:
                    self.cpu.pause = True
                    print("Setting pause TRUE")

            all_keys = pygame.key.get_pressed()

            if all_keys[pygame.K_QUOTE] and (all_keys[pygame.K_LSHIFT] or all_keys[pygame.K_RSHIFT]):
                self.mem_space.memory_data_ram[0x277] = char_to_ascii["\""]
                self.mem_space.memory_data_ram[0xC6] = 1

            elif all_keys[pygame.K_8] and (all_keys[pygame.K_LSHIFT] or all_keys[pygame.K_RSHIFT]):
                self.mem_space.memory_data_ram[0x277] = char_to_ascii["*"]
                self.mem_space.memory_data_ram[0xC6] = 1

            elif all_keys[pygame.K_9] and (all_keys[pygame.K_LSHIFT] or all_keys[pygame.K_RSHIFT]):
                self.mem_space.memory_data_ram[0x277] = char_to_ascii["("]
                self.mem_space.memory_data_ram[0xC6] = 1

            elif all_keys[pygame.K_0] and (all_keys[pygame.K_LSHIFT] or all_keys[pygame.K_RSHIFT]):
                self.mem_space.memory_data_ram[0x277] = char_to_ascii[")"]
                self.mem_space.memory_data_ram[0xC6] = 1

            elif all_keys[pygame.K_4] and (all_keys[pygame.K_LSHIFT] or all_keys[pygame.K_RSHIFT]):
                self.mem_space.memory_data_ram[0x277] = char_to_ascii["$"]
                self.mem_space.memory_data_ram[0xC6] = 1

            elif all_keys[pygame.K_DELETE] and (all_keys[pygame.K_LSHIFT] or all_keys[pygame.K_RSHIFT]):
                self.mem_space.memory_data_ram[0x277] = 147
                self.mem_space.memory_data_ram[0xC6] = 1

            elif all_keys[pygame.K_PAGEUP] and (all_keys[pygame.K_LSHIFT] or all_keys[pygame.K_RSHIFT]):
                self.mem_space.memory_data_ram[0x277] = 156
                self.mem_space.memory_data_ram[0xC6] = 1

            elif all_keys[pygame.K_SEMICOLON] and (all_keys[pygame.K_LSHIFT] or all_keys[pygame.K_RSHIFT]):
                self.mem_space.memory_data_ram[0x277] = 58
                self.mem_space.memory_data_ram[0xC6] = 1

            elif event.type == pygame.KEYDOWN:

                if event.key in pygame_to_ascii:
                    self.mem_space.memory_data_ram[0x277] = pygame_to_ascii[event.key]
                    self.mem_space.memory_data_ram[0xC6] = 1

                if event.key == pygame.K_RETURN:
                    self.mem_space.memory_data_ram[0x277] = 13
                    self.mem_space.memory_data_ram[0xC6] = 1

                if event.key == pygame.K_BACKSPACE:
                    self.mem_space.memory_data_ram[0x277] = 20
                    self.mem_space.memory_data_ram[0xC6] = 1

                if event.key == pygame.K_EQUALS:
                    self.mem_space.memory_data_ram[0x277] = char_to_ascii["="]
                    self.mem_space.memory_data_ram[0xC6] = 1

                if event.key == pygame.K_SEMICOLON:
                    self.mem_space.memory_data_ram[0x277] = 59
                    self.mem_space.memory_data_ram[0xC6] = 1


pygame_to_ascii = {
    pygame.K_a: char_to_ascii["A"],
    pygame.K_b: char_to_ascii["B"],
    pygame.K_c: char_to_ascii["C"],
    pygame.K_d: char_to_ascii["D"],
    pygame.K_e: char_to_ascii["E"],
    pygame.K_f: char_to_ascii["F"],
    pygame.K_g: char_to_ascii["G"],
    pygame.K_h: char_to_ascii["H"],
    pygame.K_i: char_to_ascii["I"],
    pygame.K_j: char_to_ascii["J"],
    pygame.K_k: char_to_ascii["K"],
    pygame.K_l: char_to_ascii["L"],
    pygame.K_m: char_to_ascii["M"],
    pygame.K_n: char_to_ascii["N"],
    pygame.K_o: char_to_ascii["O"],
    pygame.K_p: char_to_ascii["P"],
    pygame.K_q: char_to_ascii["Q"],
    pygame.K_r: char_to_ascii["R"],
    pygame.K_s: char_to_ascii["S"],
    pygame.K_t: char_to_ascii["T"],
    pygame.K_u: char_to_ascii["U"],
    pygame.K_v: char_to_ascii["V"],
    pygame.K_w: char_to_ascii["W"],
    pygame.K_x: char_to_ascii["X"],
    pygame.K_y: char_to_ascii["Y"],
    pygame.K_z: char_to_ascii["Z"],
    pygame.K_0: char_to_ascii["0"],
    pygame.K_1: char_to_ascii["1"],
    pygame.K_2: char_to_ascii["2"],
    pygame.K_3: char_to_ascii["3"],
    pygame.K_4: char_to_ascii["4"],
    pygame.K_5: char_to_ascii["5"],
    pygame.K_6: char_to_ascii["6"],
    pygame.K_7: char_to_ascii["7"],
    pygame.K_8: char_to_ascii["8"],
    pygame.K_9: char_to_ascii["9"],
    pygame.K_COMMA: char_to_ascii[","],
    pygame.K_SPACE: 32,
    pygame.K_QUOTEDBL: 34,
    pygame.K_BACKSPACE: 8,

}
