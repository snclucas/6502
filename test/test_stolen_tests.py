import unittest

from cpu6502 import CPU6502
from simple_memory_space import SimpleMemorySpace


# noinspection PyUnusedLocal
class Common6502Tests(unittest.TestCase):
    """Tests common to 6502-based microprocessors"""

    def setUp(self):
        self.memspace = SimpleMemorySpace(memspace_size=1024 * 64)

    def step(self, cpu: CPU6502):
        cycles = 0
        cycle_counter = -1
        while cycle_counter != 0:
            cycle_counter = cpu.tick()
            cycles += 1

        return cycles

    # Reset

    def test_reset_sets_registers_to_initial_states(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.reset()
        self.assertEqual(0xFF, mpu.SP)
        self.assertEqual(0, mpu.A)
        self.assertEqual(0, mpu.X)
        self.assertEqual(0, mpu.Y)
        self.assertEqual(mpu.BREAK_FLAG | mpu.UNUSED_FLAG, mpu.SR)

    # ADC Absolute

    def test_adc_bcd_off_absolute_carry_clear_in_accumulator_zeroes(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0
        # $0000 ADC $C000
        self._write(mpu.mem_space, 0x0000, (0x6D, 0x00, 0xC0))
        self.assertEqual(0x10000, len(mpu.mem_space.memory_data))

        mpu.mem_space.memory_data[0xC000] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(4, SRrocessorCycles)

    def test_adc_bcd_off_absolute_carry_set_in_accumulator_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ADC $C000
        self._write(mpu.mem_space, 0x0000, (0x6D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertNotEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    def test_adc_bcd_off_absolute_carry_clear_in_no_carry_clear_out(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x01
        # $0000 ADC $C000
        self._write(mpu.mem_space, 0x0000, (0x6D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000] = 0xFE
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_absolute_carry_clear_in_carry_set_out(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x02
        # $0000 ADC $C000
        self._write(mpu.mem_space, 0x0000, (0x6D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_absolute_overflow_clr_no_carry_01_plus_01(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x01
        # $0000 ADC $C000
        self._write(mpu.mem_space, 0x0000, (0x6D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x02, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_absolute_overflow_clr_no_carry_01_plus_ff(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x01
        # $0000 ADC $C000
        self._write(mpu.mem_space, 0x0000, (0x6D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000] = 0xff
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_absolute_overflow_set_no_carry_7f_plus_01(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x7f
        # $0000 ADC $C000
        self._write(mpu.mem_space, 0x0000, (0x6D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_absolute_overflow_set_no_carry_80_plus_ff(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x80
        # $0000 ADC $C000
        self._write(mpu.mem_space, 0x0000, (0x6D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000] = 0xff
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x7f, mpu.A)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_absolute_overflow_set_on_40_plus_40(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.OVERFLOW_FLAG
        mpu.A = 0x40
        # $0000 ADC $C000
        self._write(mpu.mem_space, 0x0000, (0x6D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000] = 0x40
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # ADC Zero Page

    def test_adc_bcd_off_zp_carry_clear_in_accumulator_zeroes(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0
        # $0000 ADC $00B0
        self._write(mpu.mem_space, 0x0000, (0x65, 0xB0))
        mpu.mem_space.memory_data[0x00B0] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(3, SRrocessorCycles)

    def test_adc_bcd_off_zp_carry_set_in_accumulator_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ADC $00B0
        self._write(mpu.mem_space, 0x0000, (0x65, 0xB0))
        mpu.mem_space.memory_data[0x00B0] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertNotEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    def test_adc_bcd_off_zp_carry_clear_in_no_carry_clear_out(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x01
        # $0000 ADC $00B0
        self._write(mpu.mem_space, 0x0000, (0x65, 0xB0))
        mpu.mem_space.memory_data[0x00B0] = 0xFE
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_zp_carry_clear_in_carry_set_out(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x02
        # $0000 ADC $00B0
        self._write(mpu.mem_space, 0x0000, (0x65, 0xB0))
        mpu.mem_space.memory_data[0x00B0] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_zp_overflow_clr_no_carry_01_plus_01(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x01
        # $0000 ADC $00B0
        self._write(mpu.mem_space, 0x0000, (0x65, 0xB0))
        mpu.mem_space.memory_data[0x00B0] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x02, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_zp_overflow_clr_no_carry_01_plus_ff(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x01
        # $0000 ADC $00B0
        self._write(mpu.mem_space, 0x0000, (0x65, 0xB0))
        mpu.mem_space.memory_data[0x00B0] = 0xff
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_zp_overflow_set_no_carry_7f_plus_01(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x7f
        # $0000 ADC $00B0
        self._write(mpu.mem_space, 0x0000, (0x65, 0xB0))
        mpu.mem_space.memory_data[0x00B0] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_zp_overflow_set_no_carry_80_plus_ff(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x80
        # $0000 ADC $00B0
        self._write(mpu.mem_space, 0x0000, (0x65, 0xB0))
        mpu.mem_space.memory_data[0x00B0] = 0xff
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x7f, mpu.A)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_zp_overflow_set_on_40_plus_40(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x40
        mpu.SR &= ~mpu.OVERFLOW_FLAG
        # $0000 ADC $00B0
        self._write(mpu.mem_space, 0x0000, (0x65, 0xB0))
        mpu.mem_space.memory_data[0x00B0] = 0x40
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # ADC Immediate

    def test_adc_bcd_off_immediate_carry_clear_in_accumulator_zeroes(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0
        # $0000 ADC #$00
        self._write(mpu.mem_space, 0x0000, (0x69, 0x00))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(2, SRrocessorCycles)

    def test_adc_bcd_off_immediate_carry_set_in_accumulator_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ADC #$00
        self._write(mpu.mem_space, 0x0000, (0x69, 0x00))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertNotEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    def test_adc_bcd_off_immediate_carry_clear_in_no_carry_clear_out(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x01
        # $0000 ADC #$FE
        self._write(mpu.mem_space, 0x0000, (0x69, 0xFE))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_immediate_carry_clear_in_carry_set_out(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x02
        # $0000 ADC #$FF
        self._write(mpu.mem_space, 0x0000, (0x69, 0xFF))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_immediate_overflow_clr_no_carry_01_plus_01(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x01
        # $0000 ADC #$01
        self._write(mpu.mem_space, 0x000, (0x69, 0x01))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x02, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_immediate_overflow_clr_no_carry_01_plus_ff(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x01
        # $0000 ADC #$FF
        self._write(mpu.mem_space, 0x000, (0x69, 0xff))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_immediate_overflow_set_no_carry_7f_plus_01(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x7f
        # $0000 ADC #$01
        self._write(mpu.mem_space, 0x000, (0x69, 0x01))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_immediate_overflow_set_no_carry_80_plus_ff(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x80
        # $0000 ADC #$FF
        self._write(mpu.mem_space, 0x000, (0x69, 0xff))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x7f, mpu.A)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_immediate_overflow_set_on_40_plus_40(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x40
        # $0000 ADC #$40
        self._write(mpu.mem_space, 0x0000, (0x69, 0x40))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_on_immediate_79_plus_00_carry_set(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.DEC_MODE_FLAG
        mpu.SR |= mpu.CARRY_FLAG
        mpu.A = 0x79
        # $0000 ADC #$00
        self._write(mpu.mem_space, 0x0000, (0x69, 0x00))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_adc_bcd_on_immediate_6f_plus_00_carry_set(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.DEC_MODE_FLAG
        mpu.SR |= mpu.CARRY_FLAG
        mpu.A = 0x6f
        # $0000 ADC #$00
        self._write(mpu.mem_space, 0x0000, (0x69, 0x00))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x76, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_adc_bcd_on_immediate_9c_plus_9d(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.DEC_MODE_FLAG
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x9c
        # $0000 ADC #$9d
        # $0002 ADC #$9d
        self._write(mpu.mem_space, 0x0000, (0x69, 0x9d))
        self._write(mpu.mem_space, 0x0002, (0x69, 0x9d))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x9f, mpu.A)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0004, mpu.PC)
        self.assertEqual(0x93, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # ADC Absolute, X-Indexed

    def test_adc_bcd_off_abs_x_carry_clear_in_accumulator_zeroes(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.X = 0x03
        # $0000 ADC $C000,X
        self._write(mpu.mem_space, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        # self.assertEqual(4, SRrocessorCycles)

    def test_adc_bcd_off_abs_x_carry_set_in_accumulator_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0
        mpu.X = 0x03
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ADC $C000,X
        self._write(mpu.mem_space, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertNotEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    def test_adc_bcd_off_abs_x_carry_clear_in_no_carry_clear_out(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x01
        mpu.X = 0x03
        # $0000 ADC $C000,X
        self._write(mpu.mem_space, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.X] = 0xFE
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_abs_x_carry_clear_in_carry_set_out(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x02
        mpu.X = 0x03
        # $0000 ADC $C000,X
        self._write(mpu.mem_space, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.X] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_abs_x_overflow_clr_no_carry_01_plus_01(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x01
        # $0000 ADC $C000,X
        self._write(mpu.mem_space, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.X] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x02, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_abs_x_overflow_clr_no_carry_01_plus_ff(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x01
        # $0000 ADC $C000,X
        self._write(mpu.mem_space, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.X] = 0xff
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_abs_x_overflow_set_no_carry_7f_plus_01(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x7f
        # $0000 ADC $C000,X
        self._write(mpu.mem_space, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.X] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_abs_x_overflow_set_no_carry_80_plus_ff(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x80
        # $0000 ADC $C000,X
        self._write(mpu.mem_space, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.X] = 0xff
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x7f, mpu.A)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_abs_x_overflow_set_on_40_plus_40(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.OVERFLOW_FLAG
        mpu.A = 0x40
        mpu.X = 0x03
        # $0000 ADC $C000,X
        self._write(mpu.mem_space, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.X] = 0x40
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # ADC Absolute, Y-Indexed

    def test_adc_bcd_off_abs_y_carry_clear_in_accumulator_zeroes(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.Y = 0x03
        # $0000 ADC $C000,Y
        self._write(mpu.mem_space, 0x0000, (0x79, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_abs_y_carry_set_in_accumulator_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0
        mpu.Y = 0x03
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ADC $C000,Y
        self._write(mpu.mem_space, 0x0000, (0x79, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertNotEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    def test_adc_bcd_off_abs_y_carry_clear_in_no_carry_clear_out(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x01
        mpu.Y = 0x03
        # $0000 ADC $C000,Y
        self._write(mpu.mem_space, 0x0000, (0x79, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.Y] = 0xFE
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_abs_y_carry_clear_in_carry_set_out(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x02
        mpu.Y = 0x03
        # $0000 ADC $C000,Y
        self._write(mpu.mem_space, 0x0000, (0x79, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.Y] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_abs_y_overflow_clr_no_carry_01_plus_01(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x01
        # $0000 ADC $C000,Y
        self._write(mpu.mem_space, 0x0000, (0x79, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.Y] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x02, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_abs_y_overflow_clr_no_carry_01_plus_ff(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x01
        # $0000 ADC $C000,Y
        self._write(mpu.mem_space, 0x0000, (0x79, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.Y] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_abs_y_overflow_set_no_carry_7f_plus_01(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x7f
        # $0000 ADC $C000,Y
        self._write(mpu.mem_space, 0x0000, (0x79, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.Y] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_abs_y_overflow_set_no_carry_80_plus_ff(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x80
        # $0000 ADC $C000,Y
        self._write(mpu.mem_space, 0x0000, (0x79, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.Y] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x7f, mpu.A)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_abs_y_overflow_set_on_40_plus_40(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.OVERFLOW_FLAG
        mpu.A = 0x40
        mpu.Y = 0x03
        # $0000 ADC $C000,Y
        self._write(mpu.mem_space, 0x0000, (0x79, 0x00, 0xC0))
        mpu.mem_space.memory_data[0xC000 + mpu.Y] = 0x40
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # ADC Zero Page, X-Indexed

    def test_adc_bcd_off_zp_x_carry_clear_in_accumulator_zeroes(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.X = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.mem_space, 0x0000, (0x75, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_zp_x_carry_set_in_accumulator_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0
        mpu.X = 0x03
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ADC $0010,X
        self._write(mpu.mem_space, 0x0000, (0x75, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertNotEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    def test_adc_bcd_off_zp_x_carry_clear_in_no_carry_clear_out(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x01
        mpu.X = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.mem_space, 0x0000, (0x75, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0xFE
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_zp_x_carry_clear_in_carry_set_out(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x02
        mpu.X = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.mem_space, 0x0000, (0x75, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_zp_x_overflow_clr_no_carry_01_plus_01(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x01
        mpu.X = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.mem_space, 0x0000, (0x75, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x02, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_zp_x_overflow_clr_no_carry_01_plus_ff(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x01
        mpu.X = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.mem_space, 0x0000, (0x75, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_zp_x_overflow_set_no_carry_7f_plus_01(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x7f
        mpu.X = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.mem_space, 0x0000, (0x75, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_zp_x_overflow_set_no_carry_80_plus_ff(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x80
        mpu.X = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.mem_space, 0x0000, (0x75, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0xff
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x7f, mpu.A)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_zp_x_overflow_set_on_40_plus_40(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.OVERFLOW_FLAG
        mpu.A = 0x40
        mpu.X = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.mem_space, 0x0000, (0x75, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x40
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # ADC Indirect, Indexed (X)

    def test_adc_bcd_off_ind_indexed_carry_clear_in_accumulator_zeroes(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.X = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x61, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_ind_indexed_carry_set_in_accumulator_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0
        mpu.X = 0x03
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x61, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertNotEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    def test_adc_bcd_off_ind_indexed_carry_clear_in_no_carry_clear_out(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x01
        mpu.X = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x61, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0xFE
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_ind_indexed_carry_clear_in_carry_set_out(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x02
        mpu.X = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x61, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_ind_indexed_overflow_clr_no_carry_01_plus_01(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x01
        mpu.X = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x61, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x02, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_ind_indexed_overflow_clr_no_carry_01_plus_ff(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x01
        mpu.X = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x61, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_ind_indexed_overflow_set_no_carry_7f_plus_01(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x7f
        mpu.X = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x61, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_ind_indexed_overflow_set_no_carry_80_plus_ff(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x80
        mpu.X = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x61, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x7f, mpu.A)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_ind_indexed_overflow_set_on_40_plus_40(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.OVERFLOW_FLAG
        mpu.A = 0x40
        mpu.X = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x61, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x40
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # ADC Indexed, Indirect (Y)

    def test_adc_bcd_off_indexed_ind_carry_clear_in_accumulator_zeroes(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.Y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x71, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_indexed_ind_carry_set_in_accumulator_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0
        mpu.Y = 0x03
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x71, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertNotEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    def test_adc_bcd_off_indexed_ind_carry_clear_in_no_carry_clear_out(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x01
        mpu.Y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x71, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0xFE
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_indexed_ind_carry_clear_in_carry_set_out(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x02
        mpu.Y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x71, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_adc_bcd_off_indexed_ind_overflow_clr_no_carry_01_plus_01(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x01
        mpu.Y = 0x03
        # $0000 $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x71, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x02, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_indexed_ind_overflow_clr_no_carry_01_plus_ff(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x01
        mpu.Y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x71, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_indexed_ind_overflow_set_no_carry_7f_plus_01(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x7f
        mpu.Y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x71, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_indexed_ind_overflow_set_no_carry_80_plus_ff(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.A = 0x80
        mpu.Y = 0x03
        # $0000 $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x71, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x7f, mpu.A)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_adc_bcd_off_indexed_ind_overflow_set_on_40_plus_40(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.OVERFLOW_FLAG
        mpu.A = 0x40
        mpu.Y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x71, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x40
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # AND (Absolute)

    def test_and_absolute_all_zeros_setting_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        # $0000 AND $ABCD
        self._write(mpu.mem_space, 0x0000, (0x2D, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_and_absolute_zeros_and_ones_setting_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        # $0000 AND $ABCD
        self._write(mpu.mem_space, 0x0000, (0x2D, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0xAA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xAA, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # AND (Absolute)

    def test_and_zp_all_zeros_setting_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        # $0000 AND $0010
        self._write(mpu.mem_space, 0x0000, (0x25, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_and_zp_zeros_and_ones_setting_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        # $0000 AND $0010
        self._write(mpu.mem_space, 0x0000, (0x25, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0xAA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xAA, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # AND (Immediate)

    def test_and_immediate_all_zeros_setting_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        # $0000 AND #$00
        self._write(mpu.mem_space, 0x0000, (0x29, 0x00))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_and_immediate_zeros_and_ones_setting_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        # $0000 AND #$AA
        self._write(mpu.mem_space, 0x0000, (0x29, 0xAA))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xAA, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # AND (Absolute, X-Indexed)

    def test_and_abs_x_all_zeros_setting_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.X = 0x03
        # $0000 AND $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x3d, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_and_abs_x_zeros_and_ones_setting_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.X = 0x03
        # $0000 AND $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x3d, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0xAA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xAA, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # AND (Absolute, Y-Indexed)

    def test_and_abs_y_all_zeros_setting_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.Y = 0x03
        # $0000 AND $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x39, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_and_abs_y_zeros_and_ones_setting_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.Y = 0x03
        # $0000 AND $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x39, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0xAA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xAA, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # AND Indirect, Indexed (X)

    def test_and_ind_indexed_x_all_zeros_setting_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.X = 0x03
        # $0000 AND ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x21, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_and_ind_indexed_x_zeros_and_ones_setting_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.X = 0x03
        # $0000 AND ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x21, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0xAA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xAA, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # AND Indexed, Indirect (Y)

    def test_and_indexed_ind_y_all_zeros_setting_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.Y = 0x03
        # $0000 AND ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x31, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_and_indexed_ind_y_zeros_and_ones_setting_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.Y = 0x03
        # $0000 AND ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x31, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0xAA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xAA, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # AND Zero Page, X-Indexed

    def test_and_zp_x_all_zeros_setting_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.X = 0x03
        # $0000 AND $0010,X
        self._write(mpu.mem_space, 0x0000, (0x35, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_and_zp_x_all_zeros_and_ones_setting_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.X = 0x03
        # $0000 AND $0010,X
        self._write(mpu.mem_space, 0x0000, (0x35, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0xAA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xAA, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # ASL Accumulator

    def test_asl_accumulator_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        # $0000 ASL A
        mpu.mem_space.memory_data[0x0000] = 0x0A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_asl_accumulator_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x40
        # $0000 ASL A
        mpu.mem_space.memory_data[0x0000] = 0x0A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_asl_accumulator_shifts_out_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x7F
        # $0000 ASL A
        mpu.mem_space.memory_data[0x0000] = 0x0A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0xFE, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_asl_accumulator_shifts_out_one(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        # $0000 ASL A
        mpu.mem_space.memory_data[0x0000] = 0x0A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0xFE, mpu.A)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    def test_asl_accumulator_80_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x80
        mpu.SR &= ~mpu.ZERO_FLAG
        # $0000 ASL A
        mpu.mem_space.memory_data[0x0000] = 0x0A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    # ASL Absolute

    def test_asl_absolute_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 ASL $ABCD
        self._write(mpu.mem_space, 0x0000, (0x0E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_asl_absolute_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 ASL $ABCD
        self._write(mpu.mem_space, 0x0000, (0x0E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x40
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_asl_absolute_shifts_out_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xAA
        # $0000 ASL $ABCD
        self._write(mpu.mem_space, 0x0000, (0x0E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x7F
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xAA, mpu.A)
        self.assertEqual(0xFE, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_asl_absolute_shifts_out_one(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xAA
        # $0000 ASL $ABCD
        self._write(mpu.mem_space, 0x0000, (0x0E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xAA, mpu.A)
        self.assertEqual(0xFE, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # ASL Zero Page

    def test_asl_zp_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 ASL $0010
        self._write(mpu.mem_space, 0x0000, (0x06, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_asl_zp_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 ASL $0010
        self._write(mpu.mem_space, 0x0000, (0x06, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x40
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_asl_zp_shifts_out_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xAA
        # $0000 ASL $0010
        self._write(mpu.mem_space, 0x0000, (0x06, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x7F
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xAA, mpu.A)
        self.assertEqual(0xFE, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_asl_zp_shifts_out_one(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xAA
        # $0000 ASL $0010
        self._write(mpu.mem_space, 0x0000, (0x06, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xAA, mpu.A)
        self.assertEqual(0xFE, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # ASL Absolute, X-Indexed

    def test_asl_abs_x_indexed_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        # $0000 ASL $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x1E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_asl_abs_x_indexed_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        # $0000 ASL $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x1E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x40
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_asl_abs_x_indexed_shifts_out_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xAA
        mpu.X = 0x03
        # $0000 ASL $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x1E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x7F
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xAA, mpu.A)
        self.assertEqual(0xFE, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_asl_abs_x_indexed_shifts_out_one(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xAA
        mpu.X = 0x03
        # $0000 ASL $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x1E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xAA, mpu.A)
        self.assertEqual(0xFE, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # ASL Zero Page, X-Indexed

    def test_asl_zp_x_indexed_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        # $0000 ASL $0010,X
        self._write(mpu.mem_space, 0x0000, (0x16, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_asl_zp_x_indexed_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        # $0000 ASL $0010,X
        self._write(mpu.mem_space, 0x0000, (0x16, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x40
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_asl_zp_x_indexed_shifts_out_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.A = 0xAA
        # $0000 ASL $0010,X
        self._write(mpu.mem_space, 0x0000, (0x16, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x7F
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xAA, mpu.A)
        self.assertEqual(0xFE, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_asl_zp_x_indexed_shifts_out_one(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.A = 0xAA
        # $0000 ASL $0010,X
        self._write(mpu.mem_space, 0x0000, (0x16, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xAA, mpu.A)
        self.assertEqual(0xFE, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # BCC

    def test_bcc_carry_clear_branches_relative_forward(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 BCC +6
        self._write(mpu.mem_space, 0x0000, (0x90, 0x06))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002 + 0x06, mpu.PC)

    def test_bcc_carry_clear_branches_relative_backward(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.PC = 0x0050
        rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
        # $0000 BCC -6
        self._write(mpu.mem_space, 0x0050, (0x90, rel))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0052 - 0x06, mpu.PC)

    def test_bcc_carry_set_does_not_branch(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 BCC +6
        self._write(mpu.mem_space, 0x0000, (0x90, 0x06))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)

    # BCS

    def test_bcs_carry_set_branches_relative_forward(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 BCS +6
        self._write(mpu.mem_space, 0x0000, (0xB0, 0x06))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002 + 0x06, mpu.PC)

    def test_bcs_carry_set_branches_relative_backward(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        mpu.PC = 0x0050
        rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
        # $0000 BCS -6
        self._write(mpu.mem_space, 0x0050, (0xB0, rel))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0052 - 0x06, mpu.PC)

    def test_bcs_carry_clear_does_not_branch(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 BCS +6
        self._write(mpu.mem_space, 0x0000, (0xB0, 0x06))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)

    # BEQ

    def test_beq_zero_set_branches_relative_forward(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.ZERO_FLAG
        # $0000 BEQ +6
        self._write(mpu.mem_space, 0x0000, (0xF0, 0x06))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002 + 0x06, mpu.PC)

    def test_beq_zero_set_branches_relative_backward(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.ZERO_FLAG
        mpu.PC = 0x0050
        rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
        # $0000 BEQ -6
        self._write(mpu.mem_space, 0x0050, (0xF0, rel))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0052 - 0x06, mpu.PC)

    def test_beq_zero_clear_does_not_branch(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        # $0000 BEQ +6
        self._write(mpu.mem_space, 0x0000, (0xF0, 0x06))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)

    # BIT (Absolute)

    def test_bit_abs_copies_bit_7_of_memory_to_n_flag_when_0(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        # $0000 BIT $FEED
        self._write(mpu.mem_space, 0x0000, (0x2C, 0xED, 0xFE))
        mpu.mem_space.memory_data[0xFEED] = 0xFF
        mpu.A = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_bit_abs_copies_bit_7_of_memory_to_n_flag_when_1(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.NEGATIVE_FLAG
        # $0000 BIT $FEED
        self._write(mpu.mem_space, 0x0000, (0x2C, 0xED, 0xFE))
        mpu.mem_space.memory_data[0xFEED] = 0x00
        mpu.A = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_bit_abs_copies_bit_6_of_memory_to_v_flag_when_0(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.OVERFLOW_FLAG
        # $0000 BIT $FEED
        self._write(mpu.mem_space, 0x0000, (0x2C, 0xED, 0xFE))
        mpu.mem_space.memory_data[0xFEED] = 0xFF
        mpu.A = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_bit_abs_copies_bit_6_of_memory_to_v_flag_when_1(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.OVERFLOW_FLAG
        # $0000 BIT $FEED
        self._write(mpu.mem_space, 0x0000, (0x2C, 0xED, 0xFE))
        mpu.mem_space.memory_data[0xFEED] = 0x00
        mpu.A = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_bit_abs_stores_result_of_and_in_z_preserves_a_when_1(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        # $0000 BIT $FEED
        self._write(mpu.mem_space, 0x0000, (0x2C, 0xED, 0xFE))
        mpu.mem_space.memory_data[0xFEED] = 0x00
        mpu.A = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xFEED])

    def test_bit_abs_stores_result_of_and_when_nonzero_in_z_preserves_a(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.ZERO_FLAG
        # $0000 BIT $FEED
        self._write(mpu.mem_space, 0x0000, (0x2C, 0xED, 0xFE))
        mpu.mem_space.memory_data[0xFEED] = 0x01
        mpu.A = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)  # result of AND is non-zero
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(0x01, mpu.mem_space.memory_data[0xFEED])

    def test_bit_abs_stores_result_of_and_when_zero_in_z_preserves_a(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        # $0000 BIT $FEED
        self._write(mpu.mem_space, 0x0000, (0x2C, 0xED, 0xFE))
        mpu.mem_space.memory_data[0xFEED] = 0x00
        mpu.A = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)  # result of AND is zero
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xFEED])

    # BIT (Zero Page)

    def test_bit_zp_copies_bit_7_of_memory_to_n_flag_when_0(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        # $0000 BIT $0010
        self._write(mpu.mem_space, 0x0000, (0x24, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0xFF
        mpu.A = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(3, SRrocessorCycles)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_bit_zp_copies_bit_7_of_memory_to_n_flag_when_1(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.NEGATIVE_FLAG
        # $0000 BIT $0010
        self._write(mpu.mem_space, 0x0000, (0x24, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        mpu.A = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(3, SRrocessorCycles)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_bit_zp_copies_bit_6_of_memory_to_v_flag_when_0(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.OVERFLOW_FLAG
        # $0000 BIT $0010
        self._write(mpu.mem_space, 0x0000, (0x24, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0xFF
        mpu.A = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(3, SRrocessorCycles)
        self.assertEqual(mpu.OVERFLOW_FLAG, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_bit_zp_copies_bit_6_of_memory_to_v_flag_when_1(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.OVERFLOW_FLAG
        # $0000 BIT $0010
        self._write(mpu.mem_space, 0x0000, (0x24, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        mpu.A = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(3, SRrocessorCycles)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    def test_bit_zp_stores_result_of_and_in_z_preserves_a_when_1(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        # $0000 BIT $0010
        self._write(mpu.mem_space, 0x0000, (0x24, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        mpu.A = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(3, SRrocessorCycles)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010])

    def test_bit_zp_stores_result_of_and_when_nonzero_in_z_preserves_a(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.ZERO_FLAG
        # $0000 BIT $0010
        self._write(mpu.mem_space, 0x0000, (0x24, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x01
        mpu.A = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(3, SRrocessorCycles)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)  # result of AND is non-zero
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(0x01, mpu.mem_space.memory_data[0x0010])

    def test_bit_zp_stores_result_of_and_when_zero_in_z_preserves_a(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        # $0000 BIT $0010
        self._write(mpu.mem_space, 0x0000, (0x24, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        mpu.A = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(3, SRrocessorCycles)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)  # result of AND is zero
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010])

    # BMI

    def test_bmi_negative_set_branches_relative_forward(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.NEGATIVE_FLAG
        # $0000 BMI +06
        self._write(mpu.mem_space, 0x0000, (0x30, 0x06))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002 + 0x06, mpu.PC)

    def test_bmi_negative_set_branches_relative_backward(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.NEGATIVE_FLAG
        mpu.PC = 0x0050
        # $0000 BMI -6
        rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
        self._write(mpu.mem_space, 0x0050, (0x30, rel))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0052 - 0x06, mpu.PC)

    def test_bmi_negative_clear_does_not_branch(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        # $0000 BEQ +6
        self._write(mpu.mem_space, 0x0000, (0x30, 0x06))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)

    # BNE

    def test_bne_zero_clear_branches_relative_forward(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        # $0000 BNE +6
        self._write(mpu.mem_space, 0x0000, (0xD0, 0x06))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002 + 0x06, mpu.PC)

    def test_bne_zero_clear_branches_relative_backward(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.PC = 0x0050
        # $0050 BNE -6
        rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
        self._write(mpu.mem_space, 0x0050, (0xD0, rel))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0052 - 0x06, mpu.PC)

    def test_bne_zero_set_does_not_branch(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.ZERO_FLAG
        # $0000 BNE +6
        self._write(mpu.mem_space, 0x0000, (0xD0, 0x06))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)

    # BPL

    def test_bpl_negative_clear_branches_relative_forward(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        # $0000 BPL +06
        self._write(mpu.mem_space, 0x0000, (0x10, 0x06))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002 + 0x06, mpu.PC)

    def test_bpl_negative_clear_branches_relative_backward(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        mpu.PC = 0x0050
        # $0050 BPL -6
        rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
        self._write(mpu.mem_space, 0x0050, (0x10, rel))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0052 - 0x06, mpu.PC)

    def test_bpl_negative_set_does_not_branch(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.NEGATIVE_FLAG
        # $0000 BPL +6
        self._write(mpu.mem_space, 0x0000, (0x10, 0x06))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)

    # BRK

    def test_brk_pushes_pc_plus_2_and_status_then_sets_pc_to_irq_vector(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = mpu.UNUSED_FLAG
        self._write(mpu.mem_space, 0xFFFE, (0xCD, 0xAB))
        # $C000 BRK
        mpu.mem_space.memory_data[0xC000] = 0x00
        mpu.PC = 0xC000
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0xABCD, mpu.PC)

        self.assertEqual(0xC0, mpu.mem_space.memory_data[0x1FF])  # PCH
        self.assertEqual(0x02, mpu.mem_space.memory_data[0x1FE])  # PCL
        self.assertEqual(mpu.BREAK_FLAG | mpu.UNUSED_FLAG, mpu.mem_space.memory_data[0x1FD])  # Status
        self.assertEqual(0xFC, mpu.SP)

        self.assertEqual(mpu.BREAK_FLAG | mpu.UNUSED_FLAG | mpu.INT_DIS_FLAG, mpu.SR)

    # IRQ and NMI handling (very similar to BRK)

    def test_irq_pushes_pc_and_correct_status_then_sets_pc_to_irq_vector(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = mpu.UNUSED_FLAG
        self._write(mpu.mem_space, 0xFFFA, (0x88, 0x77))
        self._write(mpu.mem_space, 0xFFFE, (0xCD, 0xAB))
        mpu.PC = 0xC123
        mpu._instruction_tick_counter = 1
        mpu.irq()
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0xABCD, mpu.PC)
        self.assertEqual(hex(0xC1), hex(mpu.mem_space.memory_data[0x1FF]))  # PCH
        self.assertEqual(hex(0x23), hex(mpu.mem_space.memory_data[0x1FE]))  # PCL
        self.assertEqual(mpu.UNUSED_FLAG, mpu.mem_space.memory_data[0x1FD])  # Status
        self.assertEqual(0xFC, mpu.SP)
        self.assertEqual(mpu.UNUSED_FLAG | mpu.INT_DIS_FLAG, mpu.SR)
        # self.assertEqual(7, SRrocessorCycles)

    def test_nmi_pushes_pc_and_correct_status_then_sets_pc_to_nmi_vector(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = mpu.UNUSED_FLAG
        self._write(mpu.mem_space, 0xFFFA, (0x88, 0x77))
        self._write(mpu.mem_space, 0xFFFE, (0xCD, 0xAB))
        mpu.PC = 0xC123
        mpu._instruction_tick_counter = 1
        mpu.nmi()
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x7788, mpu.PC)
        self.assertEqual(0xC1, mpu.mem_space.memory_data[0x1FF])  # PCH
        self.assertEqual(0x23, mpu.mem_space.memory_data[0x1FE])  # PCL
        self.assertEqual(mpu.UNUSED_FLAG, mpu.mem_space.memory_data[0x1FD])  # Status
        self.assertEqual(0xFC, mpu.SP)
        self.assertEqual(mpu.UNUSED_FLAG | mpu.INT_DIS_FLAG, mpu.SR)
        # self.assertEqual(7, SRrocessorCycles)

    # BVC

    def test_bvc_overflow_clear_branches_relative_forward(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.OVERFLOW_FLAG
        # $0000 BVC +6
        self._write(mpu.mem_space, 0x0000, (0x50, 0x06))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002 + 0x06, mpu.PC)

    def test_bvc_overflow_clear_branches_relative_backward(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.OVERFLOW_FLAG
        mpu.PC = 0x0050
        rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
        # $0050 BVC -6
        self._write(mpu.mem_space, 0x0050, (0x50, rel))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0052 - 0x06, mpu.PC)

    def test_bvc_overflow_set_does_not_branch(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.OVERFLOW_FLAG
        # $0000 BVC +6
        self._write(mpu.mem_space, 0x0000, (0x50, 0x06))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)

    # BVS

    def test_bvs_overflow_set_branches_relative_forward(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.OVERFLOW_FLAG
        # $0000 BVS +6
        self._write(mpu.mem_space, 0x0000, (0x70, 0x06))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002 + 0x06, mpu.PC)

    def test_bvs_overflow_set_branches_relative_backward(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.OVERFLOW_FLAG
        mpu.PC = 0x0050
        rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
        # $0050 BVS -6
        self._write(mpu.mem_space, 0x0050, (0x70, rel))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0052 - 0x06, mpu.PC)

    def test_bvs_overflow_clear_does_not_branch(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.OVERFLOW_FLAG
        # $0000 BVS +6
        self._write(mpu.mem_space, 0x0000, (0x70, 0x06))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)

    # CLC

    def test_clc_clears_carry_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 CLC
        mpu.mem_space.memory_data[0x0000] = 0x18
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    # CLD

    def test_cld_clears_decimal_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.DEC_MODE_FLAG
        # $0000 CLD
        mpu.mem_space.memory_data[0x0000] = 0xD8
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0, mpu.SR & mpu.DEC_MODE_FLAG)

    # CLI

    def test_cli_clears_interrupt_mask_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.INT_DIS_FLAG
        # $0000 CLI
        mpu.mem_space.memory_data[0x0000] = 0x58
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0, mpu.SR & mpu.INT_DIS_FLAG)

    # CLV

    def test_clv_clears_overflow_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.OVERFLOW_FLAG
        # $0000 CLV
        mpu.mem_space.memory_data[0x0000] = 0xB8
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)

    # Compare instructions

    # See http://6502.org/tutorials/compare_instructions.html
    # and http://www.6502.org/tutorials/compare_beyond.html
    # Cheat sheet:
    #
    #    - Comparison is actually subtraction "register - memory"
    #    - Z contains equality result (1 equal, 0 not equal)
    #    - C contains result of unsigned comparison (0 if A<m, 1 if A>=m)
    #    - N holds MSB of subtraction result (*NOT* of signed subtraction)
    #    - V is not affected by comparison
    #    - D has no effect on comparison

    # CMP Immediate

    def test_cmp_imm_sets_zero_carry_clears_neg_flags_if_equal(self):
        """Comparison: A == m"""
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 CMP #10 , A will be 10
        self._write(mpu.mem_space, 0x0000, (0xC9, 10))
        mpu.A = 10
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    def test_cmp_imm_clears_zero_carry_takes_neg_if_less_unsigned(self):
        """Comparison: A < m (unsigned)"""
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 CMP #10 , A will be 1
        self._write(mpu.mem_space, 0x0000, (0xC9, 10))
        mpu.A = 1
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)  # 0x01-0x0A=0xF7
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_cmp_imm_clears_zero_sets_carry_takes_neg_if_less_signed(self):
        """Comparison: A < #nn (signed), A negative"""
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 CMP #1, A will be -1 (0xFF)
        self._write(mpu.mem_space, 0x0000, (0xC9, 1))
        mpu.A = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)  # 0xFF-0x01=0xFE
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)  # A>m unsigned

    def test_cmp_imm_clears_zero_carry_takes_neg_if_less_signed_nega(self):
        """Comparison: A < m (signed), A and m both negative"""
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 CMP #0xFF (-1), A will be -2 (0xFE)
        self._write(mpu.mem_space, 0x0000, (0xC9, 0xFF))
        mpu.A = 0xFE
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)  # 0xFE-0xFF=0xFF
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)  # A<m unsigned

    def test_cmp_imm_clears_zero_sets_carry_takes_neg_if_more_unsigned(self):
        """Comparison: A > m (unsigned)"""
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 CMP #1 , A will be 10
        self._write(mpu.mem_space, 0x0000, (0xC9, 1))
        mpu.A = 10
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)  # 0x0A-0x01 = 0x09
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)  # A>m unsigned

    def test_cmp_imm_clears_zero_carry_takes_neg_if_more_signed(self):
        """Comparison: A > m (signed), memory negative"""
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 CMP #$FF (-1), A will be 2
        self._write(mpu.mem_space, 0x0000, (0xC9, 0xFF))
        mpu.A = 2
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)  # 0x02-0xFF=0x01
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)  # A<m unsigned

    def test_cmp_imm_clears_zero_carry_takes_neg_if_more_signed_nega(self):
        """Comparison: A > m (signed), A and m both negative"""
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 CMP #$FE (-2), A will be -1 (0xFF)
        self._write(mpu.mem_space, 0x0000, (0xC9, 0xFE))
        mpu.A = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)  # 0xFF-0xFE=0x01
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)  # A>m unsigned

    # CPX Immediate

    def test_cpx_imm_sets_zero_carry_clears_neg_flags_if_equal(self):
        """Comparison: X == m"""
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 CPX #$20
        self._write(mpu.mem_space, 0x0000, (0xE0, 0x20))
        mpu.X = 0x20
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # CPY Immediate

    def test_cpy_imm_sets_zero_carry_clears_neg_flags_if_equal(self):
        """Comparison: Y == m"""
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 CPY #$30
        self._write(mpu.mem_space, 0x0000, (0xC0, 0x30))
        mpu.Y = 0x30
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # DEC Absolute

    def test_dec_abs_decrements_memory(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 DEC 0xABCD
        self._write(mpu.mem_space, 0x0000, (0xCE, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x10
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x0F, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_dec_abs_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 DEC 0xABCD
        self._write(mpu.mem_space, 0x0000, (0xCE, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_dec_abs_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 DEC 0xABCD
        self._write(mpu.mem_space, 0x0000, (0xCE, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # DEC Zero Page

    def test_dec_zp_decrements_memory(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 DEC 0x0010
        self._write(mpu.mem_space, 0x0000, (0xC6, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x10
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x0F, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_dec_zp_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 DEC 0x0010
        self._write(mpu.mem_space, 0x0000, (0xC6, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_dec_zp_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 DEC 0x0010
        self._write(mpu.mem_space, 0x0000, (0xC6, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # DEC Absolute, X-Indexed

    def test_dec_abs_x_decrements_memory(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 DEC 0xABCD,X
        self._write(mpu.mem_space, 0x0000, (0xDE, 0xCD, 0xAB))
        mpu.X = 0x03
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x10
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x0F, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_dec_abs_x_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 DEC 0xABCD,X
        self._write(mpu.mem_space, 0x0000, (0xDE, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_dec_abs_x_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 DEC 0xABCD,X
        self._write(mpu.mem_space, 0x0000, (0xDE, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # DEC Zero Page, X-Indexed

    def test_dec_zp_x_decrements_memory(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 DEC 0x0010,X
        self._write(mpu.mem_space, 0x0000, (0xD6, 0x10))
        mpu.X = 0x03
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x10
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x0F, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_dec_zp_x_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 DEC 0x0010,X
        self._write(mpu.mem_space, 0x0000, (0xD6, 0x10))
        mpu.X = 0x03
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_dec_zp_x_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 DEC 0x0010,X
        self._write(mpu.mem_space, 0x0000, (0xD6, 0x10))
        mpu.X = 0x03
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # DEX

    def test_dex_decrements_x(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x10
        # $0000 DEX
        mpu.mem_space.memory_data[0x0000] = 0xCA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x0F, mpu.X)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_dex_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x00
        # $0000 DEX
        mpu.mem_space.memory_data[0x0000] = 0xCA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0xFF, mpu.X)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_dex_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x01
        # $0000 DEX
        mpu.mem_space.memory_data[0x0000] = 0xCA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x00, mpu.X)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # DEY

    def test_dey_decrements_y(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0x10
        # $0000 DEY
        mpu.mem_space.memory_data[0x0000] = 0x88
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x0F, mpu.Y)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_dey_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0x00
        # $0000 DEY
        mpu.mem_space.memory_data[0x0000] = 0x88
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0xFF, mpu.Y)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_dey_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0x01
        # $0000 DEY
        mpu.mem_space.memory_data[0x0000] = 0x88
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x00, mpu.Y)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    # EOR Absolute

    def test_eor_absolute_flips_bits_over_setting_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        self._write(mpu.mem_space, 0x0000, (0x4D, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_eor_absolute_flips_bits_over_setting_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        self._write(mpu.mem_space, 0x0000, (0x4D, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # EOR Zero Page

    def test_eor_zp_flips_bits_over_setting_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        self._write(mpu.mem_space, 0x0000, (0x45, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_eor_zp_flips_bits_over_setting_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        self._write(mpu.mem_space, 0x0000, (0x45, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # EOR Immediate

    def test_eor_immediate_flips_bits_over_setting_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        self._write(mpu.mem_space, 0x0000, (0x49, 0xFF))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_eor_immediate_flips_bits_over_setting_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        self._write(mpu.mem_space, 0x0000, (0x49, 0xFF))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # EOR Absolute, X-Indexed

    def test_eor_abs_x_indexed_flips_bits_over_setting_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.X = 0x03
        self._write(mpu.mem_space, 0x0000, (0x5D, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_eor_abs_x_indexed_flips_bits_over_setting_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.X = 0x03
        self._write(mpu.mem_space, 0x0000, (0x5D, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # EOR Absolute, Y-Indexed

    def test_eor_abs_y_indexed_flips_bits_over_setting_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.Y = 0x03
        self._write(mpu.mem_space, 0x0000, (0x59, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD + mpu.Y])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_eor_abs_y_indexed_flips_bits_over_setting_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.Y = 0x03
        self._write(mpu.mem_space, 0x0000, (0x59, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD + mpu.Y])
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # EOR Indirect, Indexed (X)

    def test_eor_ind_indexed_x_flips_bits_over_setting_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.X = 0x03
        self._write(mpu.mem_space, 0x0000, (0x41, 0x10))  # => EOR ($0010,X)
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))  # => Vector to $ABCD
        mpu.mem_space.memory_data[0xABCD] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_eor_ind_indexed_x_flips_bits_over_setting_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.X = 0x03
        self._write(mpu.mem_space, 0x0000, (0x41, 0x10))  # => EOR ($0010,X)
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))  # => Vector to $ABCD
        mpu.mem_space.memory_data[0xABCD] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # EOR Indexed, Indirect (Y)

    def test_eor_indexed_ind_y_flips_bits_over_setting_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.Y = 0x03
        self._write(mpu.mem_space, 0x0000, (0x51, 0x10))  # => EOR ($0010),Y
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))  # => Vector to $ABCD
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD + mpu.Y])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_eor_indexed_ind_y_flips_bits_over_setting_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.Y = 0x03
        self._write(mpu.mem_space, 0x0000, (0x51, 0x10))  # => EOR ($0010),Y
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))  # => Vector to $ABCD
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD + mpu.Y])
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # EOR Zero Page, X-Indexed

    def test_eor_zp_x_indexed_flips_bits_over_setting_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.X = 0x03
        self._write(mpu.mem_space, 0x0000, (0x55, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_eor_zp_x_indexed_flips_bits_over_setting_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.X = 0x03
        self._write(mpu.mem_space, 0x0000, (0x55, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # INC Absolute

    def test_inc_abs_increments_memory(self):
        mpu = CPU6502(mem_space=self.memspace)
        self._write(mpu.mem_space, 0x0000, (0xEE, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x09
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x0A, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_inc_abs_increments_memory_rolls_over_and_sets_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        self._write(mpu.mem_space, 0x0000, (0xEE, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_inc_abs_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = CPU6502(mem_space=self.memspace)
        self._write(mpu.mem_space, 0x0000, (0xEE, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x7F
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    # INC Zero Page

    def test_inc_zp_increments_memory(self):
        mpu = CPU6502(mem_space=self.memspace)
        self._write(mpu.mem_space, 0x0000, (0xE6, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x09
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x0A, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_inc_zp_increments_memory_rolls_over_and_sets_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        self._write(mpu.mem_space, 0x0000, (0xE6, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_inc_zp_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = CPU6502(mem_space=self.memspace)
        self._write(mpu.mem_space, 0x0000, (0xE6, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x7F
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    # INC Absolute, X-Indexed

    def test_inc_abs_x_increments_memory(self):
        mpu = CPU6502(mem_space=self.memspace)
        self._write(mpu.mem_space, 0x0000, (0xFE, 0xCD, 0xAB))
        mpu.X = 0x03
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x09
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x0A, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_inc_abs_x_increments_memory_rolls_over_and_sets_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        self._write(mpu.mem_space, 0x0000, (0xFE, 0xCD, 0xAB))
        mpu.X = 0x03
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_inc_abs_x_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = CPU6502(mem_space=self.memspace)
        self._write(mpu.mem_space, 0x0000, (0xFE, 0xCD, 0xAB))
        mpu.X = 0x03
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x7F
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    # INC Zero Page, X-Indexed

    def test_inc_zp_x_increments_memory(self):
        mpu = CPU6502(mem_space=self.memspace)
        self._write(mpu.mem_space, 0x0000, (0xF6, 0x10))
        mpu.X = 0x03
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x09
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x0A, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_inc_zp_x_increments_memory_rolls_over_and_sets_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        self._write(mpu.mem_space, 0x0000, (0xF6, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_inc_zp_x_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = CPU6502(mem_space=self.memspace)
        self._write(mpu.mem_space, 0x0000, (0xF6, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x7F
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    # INX

    def test_inx_increments_x(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x09
        mpu.mem_space.memory_data[0x0000] = 0xE8  # => INX
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x0A, mpu.X)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_inx_above_FF_rolls_over_and_sets_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0xFF
        mpu.mem_space.memory_data[0x0000] = 0xE8  # => INX
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x00, mpu.X)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_inx_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x7f
        mpu.mem_space.memory_data[0x0000] = 0xE8  # => INX
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x80, mpu.X)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    # INY

    def test_iny_increments_y(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0x09
        mpu.mem_space.memory_data[0x0000] = 0xC8  # => INY
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x0A, mpu.Y)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_iny_above_FF_rolls_over_and_sets_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0xFF
        mpu.mem_space.memory_data[0x0000] = 0xC8  # => INY
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x00, mpu.Y)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_iny_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0x7f
        mpu.mem_space.memory_data[0x0000] = 0xC8  # => INY
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x80, mpu.Y)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    # JMP Absolute

    def test_jmp_abs_jumps_to_absolute_address(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 JMP $ABCD
        self._write(mpu.mem_space, 0x0000, (0x4C, 0xCD, 0xAB))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0xABCD, mpu.PC)

    # JMP Indirect

    def test_jmp_ind_jumps_to_indirect_address(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 JMP ($ABCD)
        self._write(mpu.mem_space, 0x0000, (0x6C, 0x00, 0x02))
        self._write(mpu.mem_space, 0x0200, (0xCD, 0xAB))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0xABCD, mpu.PC)

    # JSR

    def test_jsr_pushes_pc_plus_2_and_sets_pc(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $C000 JSR $FFD2
        self._write(mpu.mem_space, 0xC000, (0x20, 0xD2, 0xFF))
        mpu.PC = 0xC000
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0xFFD2, mpu.PC)
        self.assertEqual(0xFD, mpu.SP)
        self.assertEqual(0xC0, mpu.mem_space.memory_data[0x01FF])  # PCH
        self.assertEqual(0x02, mpu.mem_space.memory_data[0x01FE])  # PCL+2

    # LDA Absolute

    def test_lda_absolute_loads_a_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        # $0000 LDA $ABCD
        self._write(mpu.mem_space, 0x0000, (0xAD, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_lda_absolute_loads_a_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        # $0000 LDA $ABCD
        self._write(mpu.mem_space, 0x0000, (0xAD, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LDA Zero Page

    def test_lda_zp_loads_a_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        # $0000 LDA $0010
        self._write(mpu.mem_space, 0x0000, (0xA5, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_lda_zp_loads_a_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        # $0000 LDA $0010
        self._write(mpu.mem_space, 0x0000, (0xA5, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LDA Immediate

    def test_lda_immediate_loads_a_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        # $0000 LDA #$80
        self._write(mpu.mem_space, 0x0000, (0xA9, 0x80))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_lda_immediate_loads_a_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        # $0000 LDA #$00
        self._write(mpu.mem_space, 0x0000, (0xA9, 0x00))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LDA Absolute, X-Indexed

    def test_lda_abs_x_indexed_loads_a_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.X = 0x03
        # $0000 LDA $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0xBD, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_lda_abs_x_indexed_loads_a_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.X = 0x03
        # $0000 LDA $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0xBD, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_lda_abs_x_indexed_does_not_page_wrap(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0
        mpu.X = 0xFF
        # $0000 LDA $0080,X
        self._write(mpu.mem_space, 0x0000, (0xBD, 0x80, 0x00))
        mpu.mem_space.memory_data[0x0080 + mpu.X] = 0x42
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x42, mpu.A)

    # LDA Absolute, Y-Indexed

    def test_lda_abs_y_indexed_loads_a_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.Y = 0x03
        # $0000 LDA $ABCD,Y
        self._write(mpu.mem_space, 0x0000, (0xB9, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_lda_abs_y_indexed_loads_a_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.Y = 0x03
        # $0000 LDA $ABCD,Y
        self._write(mpu.mem_space, 0x0000, (0xB9, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_lda_abs_y_indexed_does_not_page_wrap(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0
        mpu.Y = 0xFF
        # $0000 LDA $0080,X
        self._write(mpu.mem_space, 0x0000, (0xB9, 0x80, 0x00))
        mpu.mem_space.memory_data[0x0080 + mpu.Y] = 0x42
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x42, mpu.A)

    # LDA Indirect, Indexed (X)

    def test_lda_ind_indexed_x_loads_a_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.X = 0x03
        # $0000 LDA ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0xA1, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_lda_ind_indexed_x_loads_a_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.X = 0x03
        # $0000 LDA ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0xA1, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LDA Indexed, Indirect (Y)

    def test_lda_indexed_ind_y_loads_a_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.Y = 0x03
        # $0000 LDA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0xB1, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_lda_indexed_ind_y_loads_a_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.Y = 0x03
        # $0000 LDA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0xB1, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LDA Zero Page, X-Indexed

    def test_lda_zp_x_indexed_loads_a_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.X = 0x03
        # $0000 LDA $10,X
        self._write(mpu.mem_space, 0x0000, (0xB5, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_lda_zp_x_indexed_loads_a_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.X = 0x03
        # $0000 LDA $10,X
        self._write(mpu.mem_space, 0x0000, (0xB5, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LDX Absolute

    def test_ldx_absolute_loads_x_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x00
        # $0000 LDX $ABCD
        self._write(mpu.mem_space, 0x0000, (0xAE, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.X)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_ldx_absolute_loads_x_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0xFF
        # $0000 LDX $ABCD
        self._write(mpu.mem_space, 0x0000, (0xAE, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.X)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LDX Zero Page

    def test_ldx_zp_loads_x_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x00
        # $0000 LDX $0010
        self._write(mpu.mem_space, 0x0000, (0xA6, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.X)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_ldx_zp_loads_x_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0xFF
        # $0000 LDX $0010
        self._write(mpu.mem_space, 0x0000, (0xA6, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.X)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LDX Immediate

    def test_ldx_immediate_loads_x_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x00
        # $0000 LDX #$80
        self._write(mpu.mem_space, 0x0000, (0xA2, 0x80))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.X)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_ldx_immediate_loads_x_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0xFF
        # $0000 LDX #$00
        self._write(mpu.mem_space, 0x0000, (0xA2, 0x00))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.X)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LDX Absolute, Y-Indexed

    def test_ldx_abs_y_indexed_loads_x_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x00
        mpu.Y = 0x03
        # $0000 LDX $ABCD,Y
        self._write(mpu.mem_space, 0x0000, (0xBE, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.X)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_ldx_abs_y_indexed_loads_x_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0xFF
        mpu.Y = 0x03
        # $0000 LDX $ABCD,Y
        self._write(mpu.mem_space, 0x0000, (0xBE, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.X)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LDX Zero Page, Y-Indexed

    def test_ldx_zp_y_indexed_loads_x_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x00
        mpu.Y = 0x03
        # $0000 LDX $0010,Y
        self._write(mpu.mem_space, 0x0000, (0xB6, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.Y] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.X)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_ldx_zp_y_indexed_loads_x_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0xFF
        mpu.Y = 0x03
        # $0000 LDX $0010,Y
        self._write(mpu.mem_space, 0x0000, (0xB6, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.X)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LDY Absolute

    def test_ldy_absolute_loads_y_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0x00
        # $0000 LDY $ABCD
        self._write(mpu.mem_space, 0x0000, (0xAC, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.Y)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_ldy_absolute_loads_y_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0xFF
        # $0000 LDY $ABCD
        self._write(mpu.mem_space, 0x0000, (0xAC, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.Y)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LDY Zero Page

    def test_ldy_zp_loads_y_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0x00
        # $0000 LDY $0010
        self._write(mpu.mem_space, 0x0000, (0xA4, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.Y)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_ldy_zp_loads_y_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0xFF
        # $0000 LDY $0010
        self._write(mpu.mem_space, 0x0000, (0xA4, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.Y)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LDY Immediate

    def test_ldy_immediate_loads_y_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0x00
        # $0000 LDY #$80
        self._write(mpu.mem_space, 0x0000, (0xA0, 0x80))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.Y)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_ldy_immediate_loads_y_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0xFF
        # $0000 LDY #$00
        self._write(mpu.mem_space, 0x0000, (0xA0, 0x00))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.Y)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LDY Absolute, X-Indexed

    def test_ldy_abs_x_indexed_loads_x_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0x00
        mpu.X = 0x03
        # $0000 LDY $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0xBC, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.Y)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_ldy_abs_x_indexed_loads_x_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0xFF
        mpu.X = 0x03
        # $0000 LDY $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0xBC, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.Y)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LDY Zero Page, X-Indexed

    def test_ldy_zp_x_indexed_loads_x_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0x00
        mpu.X = 0x03
        # $0000 LDY $0010,X
        self._write(mpu.mem_space, 0x0000, (0xB4, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.Y)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_ldy_zp_x_indexed_loads_x_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0xFF
        mpu.X = 0x03
        # $0000 LDY $0010,X
        self._write(mpu.mem_space, 0x0000, (0xB4, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.Y)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LSR Accumulator

    def test_lsr_accumulator_rotates_in_zero_not_carry(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 LSR A
        mpu.mem_space.memory_data[0x0000] = (0x4A)
        mpu.A = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_lsr_accumulator_sets_carry_and_zero_flags_after_rotation(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 LSR A
        mpu.mem_space.memory_data[0x0000] = (0x4A)
        mpu.A = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_lsr_accumulator_rotates_bits_right(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 LSR A
        mpu.mem_space.memory_data[0x0000] = (0x4A)
        mpu.A = 0x04
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x02, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LSR Absolute

    def test_lsr_absolute_rotates_in_zero_not_carry(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 LSR $ABCD
        self._write(mpu.mem_space, 0x0000, (0x4E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_lsr_absolute_sets_carry_and_zero_flags_after_rotation(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 LSR $ABCD
        self._write(mpu.mem_space, 0x0000, (0x4E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_lsr_absolute_rotates_bits_right(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 LSR $ABCD
        self._write(mpu.mem_space, 0x0000, (0x4E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x04
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x02, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LSR Zero Page

    def test_lsr_zp_rotates_in_zero_not_carry(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 LSR $0010
        self._write(mpu.mem_space, 0x0000, (0x46, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_lsr_zp_sets_carry_and_zero_flags_after_rotation(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 LSR $0010
        self._write(mpu.mem_space, 0x0000, (0x46, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_lsr_zp_rotates_bits_right(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 LSR $0010
        self._write(mpu.mem_space, 0x0000, (0x46, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x04
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x02, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LSR Absolute, X-Indexed

    def test_lsr_abs_x_indexed_rotates_in_zero_not_carry(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        mpu.X = 0x03
        # $0000 LSR $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x5E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_lsr_abs_x_indexed_sets_c_and_z_flags_after_rotation(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.X = 0x03
        # $0000 LSR $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x5E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_lsr_abs_x_indexed_rotates_bits_right(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 LSR $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x5E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x04
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x02, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # LSR Zero Page, X-Indexed

    def test_lsr_zp_x_indexed_rotates_in_zero_not_carry(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        mpu.X = 0x03
        # $0000 LSR $0010,X
        self._write(mpu.mem_space, 0x0000, (0x56, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_lsr_zp_x_indexed_sets_carry_and_zero_flags_after_rotation(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.X = 0x03
        # $0000 LSR $0010,X
        self._write(mpu.mem_space, 0x0000, (0x56, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_lsr_zp_x_indexed_rotates_bits_right(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        mpu.X = 0x03
        # $0000 LSR $0010,X
        self._write(mpu.mem_space, 0x0000, (0x56, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x04
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x02, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    # NOP

    def test_nop_does_nothing(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 NOP
        mpu.mem_space.memory_data[0x0000] = 0xEA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)

    # ORA Absolute

    def test_ora_absolute_zeroes_or_zeros_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.A = 0x00
        # $0000 ORA $ABCD
        self._write(mpu.mem_space, 0x0000, (0x0D, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_ora_absolute_turns_bits_on_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        mpu.A = 0x03
        # $0000 ORA $ABCD
        self._write(mpu.mem_space, 0x0000, (0x0D, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x82
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x83, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # ORA Zero Page

    def test_ora_zp_zeroes_or_zeros_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.A = 0x00
        # $0000 ORA $0010
        self._write(mpu.mem_space, 0x0000, (0x05, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_ora_zp_turns_bits_on_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        mpu.A = 0x03
        # $0000 ORA $0010
        self._write(mpu.mem_space, 0x0000, (0x05, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x82
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x83, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # ORA Immediate

    def test_ora_immediate_zeroes_or_zeros_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.A = 0x00
        # $0000 ORA #$00
        self._write(mpu.mem_space, 0x0000, (0x09, 0x00))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_ora_immediate_turns_bits_on_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        mpu.A = 0x03
        # $0000 ORA #$82
        self._write(mpu.mem_space, 0x0000, (0x09, 0x82))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x83, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # ORA Absolute, X

    def test_ora_abs_x_indexed_zeroes_or_zeros_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.A = 0x00
        mpu.X = 0x03
        # $0000 ORA $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x1D, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_ora_abs_x_indexed_turns_bits_on_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        mpu.A = 0x03
        mpu.X = 0x03
        # $0000 ORA $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x1D, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x82
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x83, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # ORA Absolute, Y

    def test_ora_abs_y_indexed_zeroes_or_zeros_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.A = 0x00
        mpu.Y = 0x03
        # $0000 ORA $ABCD,Y
        self._write(mpu.mem_space, 0x0000, (0x19, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_ora_abs_y_indexed_turns_bits_on_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        mpu.A = 0x03
        mpu.Y = 0x03
        # $0000 ORA $ABCD,Y
        self._write(mpu.mem_space, 0x0000, (0x19, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x82
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x83, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # ORA Indirect, Indexed (X)

    def test_ora_ind_indexed_x_zeroes_or_zeros_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.A = 0x00
        mpu.X = 0x03
        # $0000 ORA ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x01, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_ora_ind_indexed_x_turns_bits_on_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        mpu.A = 0x03
        mpu.X = 0x03
        # $0000 ORA ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x01, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x82
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x83, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # ORA Indexed, Indirect (Y)

    def test_ora_indexed_ind_y_zeroes_or_zeros_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.A = 0x00
        mpu.Y = 0x03
        # $0000 ORA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x11, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_ora_indexed_ind_y_turns_bits_on_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        mpu.A = 0x03
        mpu.Y = 0x03
        # $0000 ORA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.mem_space, 0x0000, (0x11, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x82
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x83, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # ORA Zero Page, X

    def test_ora_zp_x_indexed_zeroes_or_zeros_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.A = 0x00
        mpu.X = 0x03
        # $0000 ORA $0010,X
        self._write(mpu.mem_space, 0x0000, (0x15, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_ora_zp_x_indexed_turns_bits_on_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        mpu.A = 0x03
        mpu.X = 0x03
        # $0000 ORA $0010,X
        self._write(mpu.mem_space, 0x0000, (0x15, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x82
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x83, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # PHA

    def test_pha_pushes_a_and_updates_sp(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xAB
        # $0000 PHA
        mpu.mem_space.memory_data[0x0000] = 0x48
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0xAB, mpu.A)
        self.assertEqual(0xAB, mpu.mem_space.memory_data[0x01FF])
        self.assertEqual(0xFE, mpu.SP)

    # PHP

    def test_php_pushes_processor_status_and_updates_sp(self):
        for flags in range(0x100):
            mpu = CPU6502(mem_space=self.memspace)
            mpu.SR = flags | mpu.BREAK_FLAG | mpu.UNUSED_FLAG
            # $0000 PHP
            mpu.mem_space.memory_data[0x0000] = 0x08
            SRrocessorCycles = self.step(cpu=mpu)
            self.assertEqual(0x0001, mpu.PC)
            self.assertEqual((flags | mpu.BREAK_FLAG | mpu.UNUSED_FLAG),
                             mpu.mem_space.memory_data[0x1FF])
            self.assertEqual(0xFE, mpu.SP)

    # PLA

    def test_pla_pulls_top_byte_from_stack_into_a_and_updates_sp(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 PLA
        mpu.mem_space.memory_data[0x0000] = 0x68
        mpu.mem_space.memory_data[0x01FF] = 0xAB
        mpu.SP = 0xFE
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0xAB, mpu.A)
        self.assertEqual(0xFF, mpu.SP)

    # PLP

    def test_plp_pulls_top_byte_from_stack_into_flags_and_updates_sp(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 PLP
        mpu.mem_space.memory_data[0x0000] = 0x28
        mpu.mem_space.memory_data[0x01FF] = 0xBA  # must have BREAK and UNUSED set
        mpu.SP = 0xFE
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0xBA, mpu.SR)
        self.assertEqual(0xFF, mpu.SP)

    # ROL Accumulator

    def test_rol_accumulator_zero_and_carry_zero_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROL A
        mpu.mem_space.memory_data[0x0000] = 0x2A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_rol_accumulator_80_and_carry_zero_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x80
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.SR &= ~mpu.ZERO_FLAG
        # $0000 ROL A
        mpu.mem_space.memory_data[0x0000] = 0x2A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_rol_accumulator_zero_and_carry_one_clears_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROL A
        mpu.mem_space.memory_data[0x0000] = 0x2A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_rol_accumulator_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x40
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROL A
        mpu.mem_space.memory_data[0x0000] = 0x2A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x81, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_rol_accumulator_shifts_out_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x7F
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROL A
        mpu.mem_space.memory_data[0x0000] = 0x2A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0xFE, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_rol_accumulator_shifts_out_one(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xFF
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROL A
        mpu.mem_space.memory_data[0x0000] = 0x2A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0xFE, mpu.A)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # ROL Absolute

    def test_rol_absolute_zero_and_carry_zero_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROL $ABCD
        self._write(mpu.mem_space, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_rol_absolute_80_and_carry_zero_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.SR &= ~mpu.ZERO_FLAG
        # $0000 ROL $ABCD
        self._write(mpu.mem_space, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_rol_absolute_zero_and_carry_one_clears_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROL $ABCD
        self._write(mpu.mem_space, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x01, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_rol_absolute_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROL $ABCD
        self._write(mpu.mem_space, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x40
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x81, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_rol_absolute_shifts_out_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROL $ABCD
        self._write(mpu.mem_space, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x7F
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFE, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_rol_absolute_shifts_out_one(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROL $ABCD
        self._write(mpu.mem_space, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFE, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # ROL Zero Page

    def test_rol_zp_zero_and_carry_zero_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROL $0010
        self._write(mpu.mem_space, 0x0000, (0x26, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_rol_zp_80_and_carry_zero_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.SR &= ~mpu.ZERO_FLAG
        # $0000 ROL $0010
        self._write(mpu.mem_space, 0x0000, (0x26, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_rol_zp_zero_and_carry_one_clears_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROL $0010
        self._write(mpu.mem_space, 0x0000, (0x26, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x01, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_rol_zp_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROL $0010
        self._write(mpu.mem_space, 0x0000, (0x26, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x40
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x81, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_rol_zp_shifts_out_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROL $0010
        self._write(mpu.mem_space, 0x0000, (0x26, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x7F
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFE, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_rol_zp_shifts_out_one(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROL $0010
        self._write(mpu.mem_space, 0x0000, (0x26, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFE, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # ROL Absolute, X-Indexed

    def test_rol_abs_x_indexed_zero_and_carry_zero_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.X = 0x03
        # $0000 ROL $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_rol_abs_x_indexed_80_and_carry_zero_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.X = 0x03
        # $0000 ROL $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_rol_abs_x_indexed_zero_and_carry_one_clears_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROL $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x01, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_rol_abs_x_indexed_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROL $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x40
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x81, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_rol_abs_x_indexed_shifts_out_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROL $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x7F
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFE, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_rol_abs_x_indexed_shifts_out_one(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROL $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFE, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # ROL Zero Page, X-Indexed

    def test_rol_zp_x_indexed_zero_and_carry_zero_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.X = 0x03
        self._write(mpu.mem_space, 0x0000, (0x36, 0x10))
        # $0000 ROL $0010,X
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_rol_zp_x_indexed_80_and_carry_zero_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.X = 0x03
        self._write(mpu.mem_space, 0x0000, (0x36, 0x10))
        # $0000 ROL $0010,X
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x80
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_rol_zp_x_indexed_zero_and_carry_one_clears_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.SR |= mpu.CARRY_FLAG
        self._write(mpu.mem_space, 0x0000, (0x36, 0x10))
        # $0000 ROL $0010,X
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x01, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_rol_zp_x_indexed_sets_n_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROL $0010,X
        self._write(mpu.mem_space, 0x0000, (0x36, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x40
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x81, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    def test_rol_zp_x_indexed_shifts_out_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROL $0010,X
        self._write(mpu.mem_space, 0x0000, (0x36, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x7F
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFE, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_rol_zp_x_indexed_shifts_out_one(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROL $0010,X
        self._write(mpu.mem_space, 0x0000, (0x36, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFE, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # ROR Accumulator

    def test_ror_accumulator_zero_and_carry_zero_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROR A
        mpu.mem_space.memory_data[0x0000] = 0x6A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_ror_accumulator_zero_and_carry_one_rotates_in_sets_n_flags(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROR A
        mpu.mem_space.memory_data[0x0000] = 0x6A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_ror_accumulator_shifts_out_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x02
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROR A
        mpu.mem_space.memory_data[0x0000] = 0x6A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x81, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_ror_accumulator_shifts_out_one(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x03
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROR A
        mpu.mem_space.memory_data[0x0000] = 0x6A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x81, mpu.A)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # ROR Absolute

    def test_ror_absolute_zero_and_carry_zero_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROR $ABCD
        self._write(mpu.mem_space, 0x0000, (0x6E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_ror_absolute_zero_and_carry_one_rotates_in_sets_n_flags(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROR $ABCD
        self._write(mpu.mem_space, 0x0000, (0x6E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_ror_absolute_shifts_out_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROR $ABCD
        self._write(mpu.mem_space, 0x0000, (0x6E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x02
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x81, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_ror_absolute_shifts_out_one(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROR $ABCD
        self._write(mpu.mem_space, 0x0000, (0x6E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x03
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x81, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # ROR Zero Page

    def test_ror_zp_zero_and_carry_zero_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROR $0010
        self._write(mpu.mem_space, 0x0000, (0x66, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_ror_zp_zero_and_carry_one_rotates_in_sets_n_flags(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROR $0010
        self._write(mpu.mem_space, 0x0000, (0x66, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_ror_zp_zero_absolute_shifts_out_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROR $0010
        self._write(mpu.mem_space, 0x0000, (0x66, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x02
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x81, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_ror_zp_shifts_out_one(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROR $0010
        self._write(mpu.mem_space, 0x0000, (0x66, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x03
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x81, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # ROR Absolute, X-Indexed

    def test_ror_abs_x_indexed_zero_and_carry_zero_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROR $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x7E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_ror_abs_x_indexed_z_and_c_1_rotates_in_sets_n_flags(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROR $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x7E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x80, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_ror_abs_x_indexed_shifts_out_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROR $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x7E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x02
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x81, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_ror_abs_x_indexed_shifts_out_one(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROR $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x7E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x03
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x81, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # ROR Zero Page, X-Indexed

    def test_ror_zp_x_indexed_zero_and_carry_zero_sets_z_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 ROR $0010,X
        self._write(mpu.mem_space, 0x0000, (0x76, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_ror_zp_x_indexed_zero_and_carry_one_rotates_in_sets_n_flags(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROR $0010,X
        self._write(mpu.mem_space, 0x0000, (0x76, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x80, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_ror_zp_x_indexed_zero_absolute_shifts_out_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROR $0010,X
        self._write(mpu.mem_space, 0x0000, (0x76, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x02
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x81, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_ror_zp_x_indexed_shifts_out_one(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0x03
        mpu.SR |= mpu.CARRY_FLAG
        # $0000 ROR $0010,X
        self._write(mpu.mem_space, 0x0000, (0x76, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x03
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x81, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # RTI

    def test_rti_restores_status_and_pc_and_updates_sp(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 RTI
        mpu.mem_space.memory_data[0x0000] = 0x40
        self._write(mpu.mem_space, 0x01FD, (0xFC, 0x03, 0xC0))  # Status, PCL, PCH
        mpu.SP = 0xFC

        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0xC003, mpu.PC)
        self.assertEqual(0xFC, mpu.SR)
        self.assertEqual(0xFF, mpu.SP)

    def test_rti_forces_break_and_unused_flags_high(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 RTI
        mpu.mem_space.memory_data[0x0000] = 0x40
        self._write(mpu.mem_space, 0x01FD, (0x00, 0x03, 0xC0))  # Status, PCL, PCH
        mpu.SP = 0xFC

        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(mpu.BREAK_FLAG, mpu.SR & mpu.BREAK_FLAG)
        self.assertEqual(mpu.UNUSED_FLAG, mpu.SR & mpu.UNUSED_FLAG)

    # RTS

    def test_rts_restores_pc_and_increments_then_updates_sp(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $0000 RTS
        mpu.mem_space.memory_data[0x0000] = 0x60
        self._write(mpu.mem_space, 0x01FE, (0x03, 0xC0))  # PCL, PCH
        mpu.PC = 0x0000
        mpu.SP = 0xFD

        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0xC004, mpu.PC)
        self.assertEqual(0xFF, mpu.SP)

    def test_rts_wraps_around_top_of_memory(self):
        mpu = CPU6502(mem_space=self.memspace)
        # $1000 RTS
        mpu.mem_space.memory_data[0x1000] = 0x60
        self._write(mpu.mem_space, 0x01FE, (0xFF, 0xFF))  # PCL, PCH
        mpu.PC = 0x1000
        mpu.SP = 0xFD

        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0000, mpu.PC)
        self.assertEqual(0xFF, mpu.SP)

    # SBC Absolute

    def test_sbc_abs_all_zeros_and_no_borrow_is_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR |= mpu.CARRY_FLAG  # borrow = 0
        mpu.A = 0x00
        # $0000 SBC $ABCD
        self._write(mpu.mem_space, 0x0000, (0xED, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_abs_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR |= mpu.CARRY_FLAG  # borrow = 0
        mpu.A = 0x01
        # $0000 SBC $ABCD
        self._write(mpu.mem_space, 0x0000, (0xED, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_abs_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR &= ~mpu.CARRY_FLAG  # borrow = 1
        mpu.A = 0x01
        # $0000 SBC $ABCD
        self._write(mpu.mem_space, 0x0000, (0xED, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_abs_downto_four_with_borrow_clears_z_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR &= ~mpu.CARRY_FLAG  # borrow = 1
        mpu.A = 0x07
        # $0000 SBC $ABCD
        self._write(mpu.mem_space, 0x0000, (0xED, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x02
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x04, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)

    # SBC Zero Page

    def test_sbc_zp_all_zeros_and_no_borrow_is_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR |= mpu.CARRY_FLAG  # borrow = 0
        mpu.A = 0x00
        # $0000 SBC $10
        self._write(mpu.mem_space, 0x0000, (0xE5, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_zp_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR |= mpu.CARRY_FLAG  # borrow = 0
        mpu.A = 0x01
        # $0000 SBC $10
        self._write(mpu.mem_space, 0x0000, (0xE5, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_zp_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR &= ~mpu.CARRY_FLAG  # borrow = 1
        mpu.A = 0x01
        # => SBC $10
        self._write(mpu.mem_space, 0x0000, (0xE5, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_zp_downto_four_with_borrow_clears_z_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR &= ~mpu.CARRY_FLAG  # borrow = 1
        mpu.A = 0x07
        # => SBC $10
        self._write(mpu.mem_space, 0x0000, (0xE5, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x02
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x04, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)

    # SBC Immediate

    def test_sbc_imm_all_zeros_and_no_borrow_is_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR |= mpu.CARRY_FLAG  # borrow = 0
        mpu.A = 0x00
        # $0000 SBC #$00
        self._write(mpu.mem_space, 0x0000, (0xE9, 0x00))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_imm_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR |= mpu.CARRY_FLAG  # borrow = 0
        mpu.A = 0x01
        # $0000 SBC #$01
        self._write(mpu.mem_space, 0x0000, (0xE9, 0x01))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_imm_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR &= ~mpu.CARRY_FLAG  # borrow = 1
        mpu.A = 0x01
        # $0000 SBC #$00
        self._write(mpu.mem_space, 0x0000, (0xE9, 0x00))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_imm_downto_four_with_borrow_clears_z_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR &= ~mpu.CARRY_FLAG  # borrow = 1
        mpu.A = 0x07
        # $0000 SBC #$02
        self._write(mpu.mem_space, 0x0000, (0xE9, 0x02))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x04, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)

    def test_sbc_bcd_on_immediate_0a_minus_00_carry_set(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.DEC_MODE_FLAG
        mpu.SR |= mpu.CARRY_FLAG
        mpu.A = 0x0a
        # $0000 SBC #$00
        self._write(mpu.mem_space, 0x0000, (0xe9, 0x00))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x0a, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    def test_sbc_bcd_on_immediate_9a_minus_00_carry_set(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.DEC_MODE_FLAG
        mpu.SR |= mpu.CARRY_FLAG
        mpu.A = 0x9a
        # $0000 SBC #$00
        self._write(mpu.mem_space, 0x0000, (0xe9, 0x00))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x9a, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    def test_sbc_bcd_on_immediate_00_minus_01_carry_set(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.DEC_MODE_FLAG
        mpu.SR |= mpu.OVERFLOW_FLAG
        mpu.SR |= mpu.ZERO_FLAG
        mpu.SR |= mpu.CARRY_FLAG
        mpu.A = 0x00
        # => $0000 SBC #$00
        self._write(mpu.mem_space, 0x0000, (0xe9, 0x01))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x99, mpu.A)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0, mpu.SR & mpu.CARRY_FLAG)

    def test_sbc_bcd_on_immediate_20_minus_0a_carry_unset(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR |= mpu.DEC_MODE_FLAG
        mpu.A = 0x20
        # $0000 SBC #$00
        self._write(mpu.mem_space, 0x0000, (0xe9, 0x0a))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x1f, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.OVERFLOW_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # SBC Absolute, X-Indexed

    def test_sbc_abs_x_all_zeros_and_no_borrow_is_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR |= mpu.CARRY_FLAG  # borrow = 0
        mpu.A = 0x00
        # $0000 SBC $FEE0,X
        self._write(mpu.mem_space, 0x0000, (0xFD, 0xE0, 0xFE))
        mpu.X = 0x0D
        mpu.mem_space.memory_data[0xFEED] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_abs_x_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR |= mpu.CARRY_FLAG  # borrow = 0
        mpu.A = 0x01
        # $0000 SBC $FEE0,X
        self._write(mpu.mem_space, 0x0000, (0xFD, 0xE0, 0xFE))
        mpu.X = 0x0D
        mpu.mem_space.memory_data[0xFEED] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_abs_x_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR &= ~mpu.CARRY_FLAG  # borrow = 1
        mpu.A = 0x01
        # $0000 SBC $FEE0,X
        self._write(mpu.mem_space, 0x0000, (0xFD, 0xE0, 0xFE))
        mpu.X = 0x0D
        mpu.mem_space.memory_data[0xFEED] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_abs_x_downto_four_with_borrow_clears_z_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR &= ~mpu.CARRY_FLAG  # borrow = 1
        mpu.A = 0x07
        # $0000 SBC $FEE0,X
        self._write(mpu.mem_space, 0x0000, (0xFD, 0xE0, 0xFE))
        mpu.X = 0x0D
        mpu.mem_space.memory_data[0xFEED] = 0x02
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x04, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)

    # SBC Absolute, Y-Indexed

    def test_sbc_abs_y_all_zeros_and_no_borrow_is_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR |= mpu.CARRY_FLAG  # borrow = 0
        mpu.A = 0x00
        # $0000 SBC $FEE0,Y
        self._write(mpu.mem_space, 0x0000, (0xF9, 0xE0, 0xFE))
        mpu.Y = 0x0D
        mpu.mem_space.memory_data[0xFEED] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_abs_y_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR |= mpu.CARRY_FLAG  # borrow = 0
        mpu.A = 0x01
        # $0000 SBC $FEE0,Y
        self._write(mpu.mem_space, 0x0000, (0xF9, 0xE0, 0xFE))
        mpu.Y = 0x0D
        mpu.mem_space.memory_data[0xFEED] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_abs_y_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR &= ~mpu.CARRY_FLAG  # borrow = 1
        mpu.A = 0x01
        # $0000 SBC $FEE0,Y
        self._write(mpu.mem_space, 0x0000, (0xF9, 0xE0, 0xFE))
        mpu.Y = 0x0D
        mpu.mem_space.memory_data[0xFEED] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_abs_y_downto_four_with_borrow_clears_z_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR &= ~mpu.CARRY_FLAG  # borrow = 1
        mpu.A = 0x07
        # $0000 SBC $FEE0,Y
        self._write(mpu.mem_space, 0x0000, (0xF9, 0xE0, 0xFE))
        mpu.Y = 0x0D
        mpu.mem_space.memory_data[0xFEED] = 0x02
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x04, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)

    # SBC Indirect, Indexed (X)

    def test_sbc_ind_x_all_zeros_and_no_borrow_is_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR |= mpu.CARRY_FLAG  # borrow = 0
        mpu.A = 0x00
        # $0000 SBC ($10,X)
        # $0013 Vector to $FEED
        self._write(mpu.mem_space, 0x0000, (0xE1, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xED, 0xFE))
        mpu.X = 0x03
        mpu.mem_space.memory_data[0xFEED] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_ind_x_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR |= mpu.CARRY_FLAG  # borrow = 0
        mpu.A = 0x01
        # $0000 SBC ($10,X)
        # $0013 Vector to $FEED
        self._write(mpu.mem_space, 0x0000, (0xE1, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xED, 0xFE))
        mpu.X = 0x03
        mpu.mem_space.memory_data[0xFEED] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_ind_x_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR &= ~mpu.CARRY_FLAG  # borrow = 1
        mpu.A = 0x01
        # $0000 SBC ($10,X)
        # $0013 Vector to $FEED
        self._write(mpu.mem_space, 0x0000, (0xE1, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xED, 0xFE))
        mpu.X = 0x03
        mpu.mem_space.memory_data[0xFEED] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_ind_x_downto_four_with_borrow_clears_z_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR &= ~mpu.CARRY_FLAG  # borrow = 1
        mpu.A = 0x07
        # $0000 SBC ($10,X)
        # $0013 Vector to $FEED
        self._write(mpu.mem_space, 0x0000, (0xE1, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xED, 0xFE))
        mpu.X = 0x03
        mpu.mem_space.memory_data[0xFEED] = 0x02
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x04, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)

    # SBC Indexed, Indirect (Y)

    def test_sbc_ind_y_all_zeros_and_no_borrow_is_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR |= mpu.CARRY_FLAG  # borrow = 0
        mpu.A = 0x00
        mpu.Y = 0x03
        # $0000 SBC ($10),Y
        # $0010 Vector to $FEED
        self._write(mpu.mem_space, 0x0000, (0xF1, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xED, 0xFE))
        mpu.mem_space.memory_data[0xFEED + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_ind_y_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR |= mpu.CARRY_FLAG  # borrow = 0
        mpu.A = 0x01
        # $0000 SBC ($10),Y
        # $0010 Vector to $FEED
        self._write(mpu.mem_space, 0x0000, (0xF1, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xED, 0xFE))
        mpu.mem_space.memory_data[0xFEED + mpu.Y] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_ind_y_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR &= ~mpu.CARRY_FLAG  # borrow = 1
        mpu.A = 0x01
        # $0000 SBC ($10),Y
        # $0010 Vector to $FEED
        self._write(mpu.mem_space, 0x0000, (0xF1, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xED, 0xFE))
        mpu.mem_space.memory_data[0xFEED + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_ind_y_downto_four_with_borrow_clears_z_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR &= ~mpu.CARRY_FLAG  # borrow = 1
        mpu.A = 0x07
        # $0000 SBC ($10),Y
        # $0010 Vector to $FEED
        self._write(mpu.mem_space, 0x0000, (0xF1, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xED, 0xFE))
        mpu.mem_space.memory_data[0xFEED + mpu.Y] = 0x02
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x04, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)

    # SBC Zero Page, X-Indexed

    def test_sbc_zp_x_all_zeros_and_no_borrow_is_zero(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR |= mpu.CARRY_FLAG  # borrow = 0
        mpu.A = 0x00
        # $0000 SBC $10,X
        self._write(mpu.mem_space, 0x0000, (0xF5, 0x10))
        mpu.X = 0x0D
        mpu.mem_space.memory_data[0x001D] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_zp_x_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR |= mpu.CARRY_FLAG  # borrow = 0
        mpu.A = 0x01
        # $0000 SBC $10,X
        self._write(mpu.mem_space, 0x0000, (0xF5, 0x10))
        mpu.X = 0x0D
        mpu.mem_space.memory_data[0x001D] = 0x01
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_zp_x_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR &= ~mpu.CARRY_FLAG  # borrow = 1
        mpu.A = 0x01
        # $0000 SBC $10,X
        self._write(mpu.mem_space, 0x0000, (0xF5, 0x10))
        mpu.X = 0x0D
        mpu.mem_space.memory_data[0x001D] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    def test_sbc_zp_x_downto_four_with_borrow_clears_z_n(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        mpu.SR &= ~mpu.CARRY_FLAG  # borrow = 1
        mpu.A = 0x07
        # $0000 SBC $10,X
        self._write(mpu.mem_space, 0x0000, (0xF5, 0x10))
        mpu.X = 0x0D
        mpu.mem_space.memory_data[0x001D] = 0x02
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x04, mpu.A)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(mpu.CARRY_FLAG, mpu.CARRY_FLAG)

    # SEC

    def test_sec_sets_carry_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.CARRY_FLAG
        # $0000 SEC
        mpu.mem_space.memory_data[0x0000] = 0x038
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(mpu.CARRY_FLAG, mpu.SR & mpu.CARRY_FLAG)

    # SED

    def test_sed_sets_decimal_mode_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.DEC_MODE_FLAG)
        # $0000 SED
        mpu.mem_space.memory_data[0x0000] = 0xF8
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(mpu.DEC_MODE_FLAG, mpu.SR & mpu.DEC_MODE_FLAG)

    # SEI

    def test_sei_sets_interrupt_disable_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~(mpu.INT_DIS_FLAG)
        # $0000 SEI
        mpu.mem_space.memory_data[0x0000] = 0x78
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(mpu.INT_DIS_FLAG, mpu.SR & mpu.INT_DIS_FLAG)

    # STA Absolute

    def test_sta_absolute_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.NEGATIVE_FLAG
        mpu.A = 0xFF
        # $0000 STA $ABCD
        self._write(mpu.mem_space, 0x0000, (0x8D, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(flags, mpu.SR)

    def test_sta_absolute_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.ZERO_FLAG
        mpu.A = 0x00
        # $0000 STA $ABCD
        self._write(mpu.mem_space, 0x0000, (0x8D, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(flags, mpu.SR)

    # STA Zero Page

    def test_sta_zp_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.NEGATIVE_FLAG
        mpu.A = 0xFF
        # $0000 STA $0010
        self._write(mpu.mem_space, 0x0000, (0x85, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(flags, mpu.SR)

    def test_sta_zp_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.ZERO_FLAG
        mpu.A = 0x00
        # $0000 STA $0010
        self._write(mpu.mem_space, 0x0000, (0x85, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(flags, mpu.SR)

    # STA Absolute, X-Indexed

    def test_sta_abs_x_indexed_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.NEGATIVE_FLAG
        mpu.A = 0xFF
        mpu.X = 0x03
        # $0000 STA $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x9D, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(flags, mpu.SR)

    def test_sta_abs_x_indexed_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.ZERO_FLAG
        mpu.A = 0x00
        mpu.X = 0x03
        # $0000 STA $ABCD,X
        self._write(mpu.mem_space, 0x0000, (0x9D, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.X] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD + mpu.X])
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(flags, mpu.SR)

    # STA Absolute, Y-Indexed

    def test_sta_abs_y_indexed_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.NEGATIVE_FLAG
        mpu.A = 0xFF
        mpu.Y = 0x03
        # $0000 STA $ABCD,Y
        self._write(mpu.mem_space, 0x0000, (0x99, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD + mpu.Y])
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(flags, mpu.SR)

    def test_sta_abs_y_indexed_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.ZERO_FLAG
        mpu.A = 0x00
        mpu.Y = 0x03
        # $0000 STA $ABCD,Y
        self._write(mpu.mem_space, 0x0000, (0x99, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD + mpu.Y] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD + mpu.Y])
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(flags, mpu.SR)

    # STA Indirect, Indexed (X)

    def test_sta_ind_indexed_x_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.NEGATIVE_FLAG
        mpu.A = 0xFF
        mpu.X = 0x03
        # $0000 STA ($0010,X)
        # $0013 Vector to $FEED
        self._write(mpu.mem_space, 0x0000, (0x81, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xED, 0xFE))
        mpu.mem_space.memory_data[0xFEED] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xFEED])
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(flags, mpu.SR)

    def test_sta_ind_indexed_x_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.ZERO_FLAG
        mpu.A = 0x00
        mpu.X = 0x03
        # $0000 STA ($0010,X)
        # $0013 Vector to $FEED
        self._write(mpu.mem_space, 0x0000, (0x81, 0x10))
        self._write(mpu.mem_space, 0x0013, (0xED, 0xFE))
        mpu.mem_space.memory_data[0xFEED] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xFEED])
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(flags, mpu.SR)

    # STA Indexed, Indirect (Y)

    def test_sta_indexed_ind_y_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.NEGATIVE_FLAG
        mpu.A = 0xFF
        mpu.Y = 0x03
        # $0000 STA ($0010),Y
        # $0010 Vector to $FEED
        self._write(mpu.mem_space, 0x0000, (0x91, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xED, 0xFE))
        mpu.mem_space.memory_data[0xFEED + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xFEED + mpu.Y])
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(flags, mpu.SR)

    def test_sta_indexed_ind_y_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.ZERO_FLAG
        mpu.A = 0x00
        mpu.Y = 0x03
        # $0000 STA ($0010),Y
        # $0010 Vector to $FEED
        self._write(mpu.mem_space, 0x0000, (0x91, 0x10))
        self._write(mpu.mem_space, 0x0010, (0xED, 0xFE))
        mpu.mem_space.memory_data[0xFEED + mpu.Y] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xFEED + mpu.Y])
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(flags, mpu.SR)

    # STA Zero Page, X-Indexed

    def test_sta_zp_x_indexed_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.NEGATIVE_FLAG
        mpu.A = 0xFF
        mpu.X = 0x03
        # $0000 STA $0010,X
        self._write(mpu.mem_space, 0x0000, (0x95, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(0xFF, mpu.A)
        self.assertEqual(flags, mpu.SR)

    def test_sta_zp_x_indexed_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.ZERO_FLAG
        mpu.A = 0x00
        mpu.X = 0x03
        # $0000 STA $0010,X
        self._write(mpu.mem_space, 0x0000, (0x95, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(flags, mpu.SR)

    # STX Absolute

    def test_stx_absolute_stores_x_leaves_x_and_n_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.NEGATIVE_FLAG
        mpu.X = 0xFF
        # $0000 STX $ABCD
        self._write(mpu.mem_space, 0x0000, (0x8E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(0xFF, mpu.X)
        self.assertEqual(flags, mpu.SR)

    def test_stx_absolute_stores_x_leaves_x_and_z_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.ZERO_FLAG
        mpu.X = 0x00
        # $0000 STX $ABCD
        self._write(mpu.mem_space, 0x0000, (0x8E, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(0x00, mpu.X)
        self.assertEqual(flags, mpu.SR)

    # STX Zero Page

    def test_stx_zp_stores_x_leaves_x_and_n_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.NEGATIVE_FLAG
        mpu.X = 0xFF
        # $0000 STX $0010
        self._write(mpu.mem_space, 0x0000, (0x86, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(0xFF, mpu.X)
        self.assertEqual(flags, mpu.SR)

    def test_stx_zp_stores_x_leaves_x_and_z_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.ZERO_FLAG
        mpu.X = 0x00
        # $0000 STX $0010
        self._write(mpu.mem_space, 0x0000, (0x86, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(0x00, mpu.X)
        self.assertEqual(flags, mpu.SR)

    # STX Zero Page, Y-Indexed

    def test_stx_zp_y_indexed_stores_x_leaves_x_and_n_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.NEGATIVE_FLAG
        mpu.X = 0xFF
        mpu.Y = 0x03
        # $0000 STX $0010,Y
        self._write(mpu.mem_space, 0x0000, (0x96, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.Y] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0x0010 + mpu.Y])
        self.assertEqual(0xFF, mpu.X)
        self.assertEqual(flags, mpu.SR)

    def test_stx_zp_y_indexed_stores_x_leaves_x_and_z_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.ZERO_FLAG
        mpu.X = 0x00
        mpu.Y = 0x03
        # $0000 STX $0010,Y
        self._write(mpu.mem_space, 0x0000, (0x96, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.Y] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010 + mpu.Y])
        self.assertEqual(0x00, mpu.X)
        self.assertEqual(flags, mpu.SR)

    # STY Absolute

    def test_sty_absolute_stores_y_leaves_y_and_n_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.NEGATIVE_FLAG
        mpu.Y = 0xFF
        # $0000 STY $ABCD
        self._write(mpu.mem_space, 0x0000, (0x8C, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(0xFF, mpu.Y)
        self.assertEqual(flags, mpu.SR)

    def test_sty_absolute_stores_y_leaves_y_and_z_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.ZERO_FLAG
        mpu.Y = 0x00
        # $0000 STY $ABCD
        self._write(mpu.mem_space, 0x0000, (0x8C, 0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0003, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0xABCD])
        self.assertEqual(0x00, mpu.Y)
        self.assertEqual(flags, mpu.SR)

    # STY Zero Page

    def test_sty_zp_stores_y_leaves_y_and_n_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.NEGATIVE_FLAG
        mpu.Y = 0xFF
        # $0000 STY $0010
        self._write(mpu.mem_space, 0x0000, (0x84, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(0xFF, mpu.Y)
        self.assertEqual(flags, mpu.SR)

    def test_sty_zp_stores_y_leaves_y_and_z_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.ZERO_FLAG
        mpu.Y = 0x00
        # $0000 STY $0010
        self._write(mpu.mem_space, 0x0000, (0x84, 0x10))
        mpu.mem_space.memory_data[0x0010] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010])
        self.assertEqual(0x00, mpu.Y)
        self.assertEqual(flags, mpu.SR)

    # STY Zero Page, X-Indexed

    def test_sty_zp_x_indexed_stores_y_leaves_y_and_n_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.NEGATIVE_FLAG
        mpu.Y = 0xFF
        mpu.X = 0x03
        # $0000 STY $0010,X
        self._write(mpu.mem_space, 0x0000, (0x94, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0x00
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0xFF, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(0xFF, mpu.Y)
        self.assertEqual(flags, mpu.SR)

    def test_sty_zp_x_indexed_stores_y_leaves_y_and_z_flag_unchanged(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = flags = 0xFF & ~mpu.ZERO_FLAG
        mpu.Y = 0x00
        mpu.X = 0x03
        # $0000 STY $0010,X
        self._write(mpu.mem_space, 0x0000, (0x94, 0x10))
        mpu.mem_space.memory_data[0x0010 + mpu.X] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x00, mpu.mem_space.memory_data[0x0010 + mpu.X])
        self.assertEqual(0x00, mpu.Y)
        self.assertEqual(flags, mpu.SR)

    # TAX

    def test_tax_transfers_accumulator_into_x(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xAB
        mpu.X = 0x00
        # $0000 TAX
        mpu.mem_space.memory_data[0x0000] = 0xAA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0xAB, mpu.A)
        self.assertEqual(0xAB, mpu.X)

    def test_tax_sets_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        mpu.A = 0x80
        mpu.X = 0x00
        # $0000 TAX
        mpu.mem_space.memory_data[0x0000] = 0xAA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(0x80, mpu.X)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_tax_sets_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.A = 0x00
        mpu.X = 0xFF
        # $0000 TAX
        mpu.mem_space.memory_data[0x0000] = 0xAA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0x00, mpu.X)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    # TAY

    def test_tay_transfers_accumulator_into_y(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0xAB
        mpu.Y = 0x00
        # $0000 TAY
        mpu.mem_space.memory_data[0x0000] = 0xA8
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0xAB, mpu.A)
        self.assertEqual(0xAB, mpu.Y)

    def test_tay_sets_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        mpu.A = 0x80
        mpu.Y = 0x00
        # $0000 TAY
        mpu.mem_space.memory_data[0x0000] = 0xA8
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(0x80, mpu.Y)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_tay_sets_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.A = 0x00
        mpu.Y = 0xFF
        # $0000 TAY
        mpu.mem_space.memory_data[0x0000] = 0xA8
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0x00, mpu.Y)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    # TSX

    def test_tsx_transfers_stack_pointer_into_x(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SP = 0xAB
        mpu.X = 0x00
        # $0000 TSX
        mpu.mem_space.memory_data[0x0000] = 0xBA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0xAB, mpu.SP)
        self.assertEqual(0xAB, mpu.X)

    def test_tsx_sets_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        mpu.SP = 0x80
        mpu.X = 0x00
        # $0000 TSX
        mpu.mem_space.memory_data[0x0000] = 0xBA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x80, mpu.SP)
        self.assertEqual(0x80, mpu.X)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_tsx_sets_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.SP = 0x00
        mpu.Y = 0xFF
        # $0000 TSX
        mpu.mem_space.memory_data[0x0000] = 0xBA
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x00, mpu.SP)
        self.assertEqual(0x00, mpu.X)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    # TXA

    def test_txa_transfers_x_into_a(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0xAB
        mpu.A = 0x00
        # $0000 TXA
        mpu.mem_space.memory_data[0x0000] = 0x8A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0xAB, mpu.A)
        self.assertEqual(0xAB, mpu.X)

    def test_txa_sets_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        mpu.X = 0x80
        mpu.A = 0x00
        # $0000 TXA
        mpu.mem_space.memory_data[0x0000] = 0x8A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(0x80, mpu.X)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_txa_sets_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.X = 0x00
        mpu.A = 0xFF
        # $0000 TXA
        mpu.mem_space.memory_data[0x0000] = 0x8A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0x00, mpu.X)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    # TXS

    def test_txs_transfers_x_into_stack_pointer(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.X = 0xAB
        # $0000 TXS
        mpu.mem_space.memory_data[0x0000] = 0x9A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0xAB, mpu.SP)
        self.assertEqual(0xAB, mpu.X)

    def test_txs_does_not_set_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        mpu.X = 0x80
        # $0000 TXS
        mpu.mem_space.memory_data[0x0000] = 0x9A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x80, mpu.SP)
        self.assertEqual(0x80, mpu.X)
        self.assertEqual(0, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_txs_does_not_set_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.X = 0x00
        # $0000 TXS
        mpu.mem_space.memory_data[0x0000] = 0x9A
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x00, mpu.SP)
        self.assertEqual(0x00, mpu.X)
        self.assertEqual(0, mpu.SR & mpu.ZERO_FLAG)

    # TYA

    def test_tya_transfers_y_into_a(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.Y = 0xAB
        mpu.A = 0x00
        # $0000 TYA
        mpu.mem_space.memory_data[0x0000] = 0x98
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0xAB, mpu.A)
        self.assertEqual(0xAB, mpu.Y)

    def test_tya_sets_negative_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.NEGATIVE_FLAG
        mpu.Y = 0x80
        mpu.A = 0x00
        # $0000 TYA
        mpu.mem_space.memory_data[0x0000] = 0x98
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0001, mpu.PC)
        self.assertEqual(0x80, mpu.A)
        self.assertEqual(0x80, mpu.Y)
        self.assertEqual(mpu.NEGATIVE_FLAG, mpu.SR & mpu.NEGATIVE_FLAG)

    def test_tya_sets_zero_flag(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR &= ~mpu.ZERO_FLAG
        mpu.Y = 0x00
        mpu.A = 0xFF
        # $0000 TYA
        mpu.mem_space.memory_data[0x0000] = 0x98
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x00, mpu.A)
        self.assertEqual(0x00, mpu.Y)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)
        self.assertEqual(0x0001, mpu.PC)

    def test_brk_interrupt(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = 0x00
        self._write(mpu.mem_space, 0xFFFE, (0x00, 0x04))

        self._write(mpu.mem_space, 0x0000, (0xA9, 0x01,  # LDA #$01
                                            0x00, 0xEA,  # BRK + skipped byte
                                            0xEA, 0xEA,  # NOP, NOP
                                            0xA9, 0x03))  # LDA #$03

        self._write(mpu.mem_space, 0x0400, (0xA9, 0x02,  # LDA #$02
                                            0x40))  # RTI

        SRrocessorCycles = self.step(cpu=mpu)  # LDA #$01
        self.assertEqual(0x01, mpu.A)
        self.assertEqual(0x0002, mpu.PC)
        SRrocessorCycles = self.step(cpu=mpu)  # BRK
        self.assertEqual(0x0400, mpu.PC)
        SRrocessorCycles = self.step(cpu=mpu)  # LDA #$02
        self.assertEqual(0x02, mpu.A)
        self.assertEqual(0x0402, mpu.PC)
        SRrocessorCycles = self.step(cpu=mpu)  # RTI

        self.assertEqual(0x0004, mpu.PC)
        SRrocessorCycles = self.step(cpu=mpu)  # A NOP
        SRrocessorCycles = self.step(cpu=mpu)  # The second NOP

        SRrocessorCycles = self.step(cpu=mpu)  # LDA #$03
        self.assertEqual(0x03, mpu.A)
        self.assertEqual(0x0008, mpu.PC)

    # Test Helpers

    def _write(self, memory, start_address, bytes):
        memory.memory_data[start_address:start_address + len(bytes)] = bytes

    def _make_mpu(self, *args, **kargs):
        klass = self._get_target_class()
        mpu = klass(*args, **kargs)
        if 'memory' not in kargs:
            mpu.mem_space = 0x10000 * [0xAA]
        return mpu

    def _get_target_class(self):
        raise NotImplementedError("Target class not specified")


#class MPUTests(unittest.TestCase):
class MPUTests(unittest.TestCase):
    """ NMOS 6502 tests """

    def step(self, cpu: CPU6502):
        cycles = 0
        cycle_counter = -1
        while cycle_counter != 0:
            cycle_counter = cpu.tick()
            cycles += 1

        return cycles

    def setUp(self):
        self.memspace = SimpleMemorySpace(memspace_size=1024 * 64)

    # ADC Indirect, Indexed (X)

    def _write(self, memspace, start_address, bytes):
        for i in range(len(bytes)):
            memspace.memory_data[start_address + i] = bytes[i]

    def test_adc_ind_indexed_has_page_wrap_bug(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = 0x00
        mpu.A = 0x01
        mpu.X = 0xFF
        # $0000 ADC ($80,X)
        # $007f Vector to $BBBB (read if page wrapped)
        # $017f Vector to $ABCD (read if no page wrap)
        self._write(mpu.mem_space, 0x0000, (0x61, 0x80))
        self._write(mpu.mem_space, 0x007f, (0xBB, 0xBB))
        self._write(mpu.mem_space, 0x017f, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x01
        mpu.mem_space.memory_data[0xBBBB] = 0x02
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x03, mpu.A)

    # ADC Indexed, Indirect (Y)

    def test_adc_indexed_ind_y_has_page_wrap_bug(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.PC = 0x1000
        mpu.SR = 0
        mpu.A = 0x42
        mpu.Y = 0x02
        # $1000 ADC ($FF),Y
        self._write(mpu.mem_space, 0x1000, (0x71, 0xff))
        # Vector
        mpu.mem_space.memory_data[0x00ff] = 0x10  # low byte
        mpu.mem_space.memory_data[0x0100] = 0x20  # high byte if no page wrap
        mpu.mem_space.memory_data[0x0000] = 0x00  # high byte if page wrapped
        # Data
        mpu.mem_space.memory_data[0x2012] = 0x14  # read if no page wrap
        mpu.mem_space.memory_data[0x0012] = 0x42  # read if page wrapped
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(hex(0x84), hex(mpu.A))

    # LDA Zero Page, X-Indexed

    def test_lda_zp_x_indexed_page_wraps(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.X = 0xFF
        # $0000 LDA $80,X
        self._write(mpu.mem_space, 0x0000, (0xB5, 0x80))
        mpu.mem_space.memory_data[0x007F] = 0x42
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x42, mpu.A)

    # AND Indexed, Indirect (Y)

    def test_and_indexed_ind_y_has_page_wrap_bug(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.PC = 0x1000
        mpu.A = 0x42
        mpu.Y = 0x02
        # $1000 AND ($FF),Y
        self._write(mpu.mem_space, 0x1000, (0x31, 0xff))
        # Vector
        mpu.mem_space.memory_data[0x00ff] = 0x10  # low byte
        mpu.mem_space.memory_data[0x0100] = 0x20  # high byte if no page wrap
        mpu.mem_space.memory_data[0x0000] = 0x00  # high byte if page wrapped
        # Data
        mpu.mem_space.memory_data[0x2012] = 0x00  # read if no page wrap
        mpu.mem_space.memory_data[0x0012] = 0xFF  # read if page wrapped
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x42, mpu.A)

    # BRK

    def test_brk_preserves_decimal_flag_when_it_is_set(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = mpu.DEC_MODE_FLAG
        # $C000 BRK
        mpu.mem_space.memory_data[0xC000] = 0x00
        mpu.PC = 0xC000
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(mpu.BREAK_FLAG, mpu.SR & mpu.BREAK_FLAG)
        self.assertEqual(mpu.DEC_MODE_FLAG, mpu.SR & mpu.DEC_MODE_FLAG)

    def test_brk_preserves_decimal_flag_when_it_is_clear(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = 0
        # $C000 BRK
        mpu.mem_space.memory_data[0xC000] = 0x00
        mpu.PC = 0xC000
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(mpu.BREAK_FLAG, mpu.SR & mpu.BREAK_FLAG)
        self.assertEqual(0, mpu.SR & mpu.DEC_MODE_FLAG)

    # CMP Indirect, Indexed (X)

    def test_cmp_ind_x_has_page_wrap_bug(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = 0
        mpu.A = 0x42
        mpu.X = 0xFF
        # $0000 CMP ($80,X)
        # $007f Vector to $BBBB (read if page wrapped)
        # $017f Vector to $ABCD (read if no page wrap)
        self._write(mpu.mem_space, 0x0000, (0xC1, 0x80))
        self._write(mpu.mem_space, 0x007f, (0xBB, 0xBB))
        self._write(mpu.mem_space, 0x017f, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        mpu.mem_space.memory_data[0xBBBB] = 0x42
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    # CMP Indexed, Indirect (Y)

    def test_cmp_indexed_ind_y_has_page_wrap_bug(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.PC = 0x1000
        mpu.SR = 0
        mpu.A = 0x42
        mpu.Y = 0x02
        # $1000 CMP ($FF),Y
        self._write(mpu.mem_space, 0x1000, (0xd1, 0xff))
        # Vector
        mpu.mem_space.memory_data[0x00ff] = 0x10  # low byte
        mpu.mem_space.memory_data[0x0100] = 0x20  # high byte if no page wrap
        mpu.mem_space.memory_data[0x0000] = 0x00  # high byte if page wrapped
        # Data
        mpu.mem_space.memory_data[0x2012] = 0x14  # read if no page wrap
        mpu.mem_space.memory_data[0x0012] = 0x42  # read if page wrapped
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(mpu.ZERO_FLAG, mpu.SR & mpu.ZERO_FLAG)

    # EOR Indirect, Indexed (X)

    def test_eor_ind_x_has_page_wrap_bug(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.SR = 0
        mpu.A = 0xAA
        mpu.X = 0xFF
        # $0000 EOR ($80,X)
        # $007f Vector to $BBBB (read if page wrapped)
        # $017f Vector to $ABCD (read if no page wrap)
        self._write(mpu.mem_space, 0x0000, (0x41, 0x80))
        self._write(mpu.mem_space, 0x007f, (0xBB, 0xBB))
        self._write(mpu.mem_space, 0x017f, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x00
        mpu.mem_space.memory_data[0xBBBB] = 0xFF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x55, mpu.A)

    # EOR Indexed, Indirect (Y)

    def test_eor_indexed_ind_y_has_page_wrap_bug(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.PC = 0x1000
        mpu.A = 0xAA
        mpu.Y = 0x02
        # $1000 EOR ($FF),Y
        self._write(mpu.mem_space, 0x1000, (0x51, 0xff))
        # Vector
        mpu.mem_space.memory_data[0x00ff] = 0x10  # low byte
        mpu.mem_space.memory_data[0x0100] = 0x20  # high byte if no page wrap
        mpu.mem_space.memory_data[0x0000] = 0x00  # high byte if page wrapped
        # Data
        mpu.mem_space.memory_data[0x2012] = 0x00  # read if no page wrap
        mpu.mem_space.memory_data[0x0012] = 0xFF  # read if page wrapped
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x55, mpu.A)

    # LDA Indirect, Indexed (X)

    def test_lda_ind_indexed_x_has_page_wrap_bug(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.X = 0xff
        # $0000 LDA ($80,X)
        # $007f Vector to $BBBB (read if page wrapped)
        # $017f Vector to $ABCD (read if no page wrap)
        self._write(mpu.mem_space, 0x0000, (0xA1, 0x80))
        self._write(mpu.mem_space, 0x007f, (0xBB, 0xBB))
        self._write(mpu.mem_space, 0x017f, (0xCD, 0xAB))
        mpu.mem_space.memory_data[0xABCD] = 0x42
        mpu.mem_space.memory_data[0xBBBB] = 0xEF
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0xEF, mpu.A)

    # LDA Indexed, Indirect (Y)

    def test_lda_indexed_ind_y_has_page_wrap_bug(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.PC = 0x1000
        mpu.A = 0x00
        mpu.Y = 0x02
        # $1000 LDA ($FF),Y
        self._write(mpu.mem_space, 0x1000, (0xb1, 0xff))
        # Vector
        mpu.mem_space.memory_data[0x00ff] = 0x10  # low byte
        mpu.mem_space.memory_data[0x0100] = 0x20  # high byte if no page wrap
        mpu.mem_space.memory_data[0x0000] = 0x00  # high byte if page wrapped
        # Data
        mpu.mem_space.memory_data[0x2012] = 0x14  # read if no page wrap
        mpu.mem_space.memory_data[0x0012] = 0x42  # read if page wrapped
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x42, mpu.A)

    # LDA Zero Page, X-Indexed

    def test_lda_zp_x_has_page_wrap_bug(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.A = 0x00
        mpu.X = 0xFF
        # $0000 LDA $80,X
        self._write(mpu.mem_space, 0x0000, (0xB5, 0x80))
        mpu.mem_space.memory_data[0x007F] = 0x42
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x0002, mpu.PC)
        self.assertEqual(0x42, mpu.A)

    # JMP Indirect

    def test_jmp_jumps_to_address_with_page_wrap_bug(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.mem_space.memory_data[0x00ff] = 0
        # $0000 JMP ($00)
        self._write(mpu.mem_space, 0, (0x6c, 0xff, 0x00))
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x6c00, mpu.PC)
        self.assertEqual(5, SRrocessorCycles)

    # ORA Indexed, Indirect (Y)

    def test_ora_indexed_ind_y_has_page_wrap_bug(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.PC = 0x1000
        mpu.A = 0x00
        mpu.Y = 0x02
        # $1000 ORA ($FF),Y
        self._write(mpu.mem_space, 0x1000, (0x11, 0xff))
        # Vector
        mpu.mem_space.memory_data[0x00ff] = 0x10  # low byte
        mpu.mem_space.memory_data[0x0100] = 0x20  # high byte if no page wrap
        mpu.mem_space.memory_data[0x0000] = 0x00  # high byte if page wrapped
        # Data
        mpu.mem_space.memory_data[0x2012] = 0x00  # read if no page wrap
        mpu.mem_space.memory_data[0x0012] = 0x42  # read if page wrapped
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x42, mpu.A)

    # SBC Indexed, Indirect (Y)

    def test_sbc_indexed_ind_y_has_page_wrap_bug(self):
        mpu = CPU6502(mem_space=self.memspace)
        mpu.PC = 0x1000
        mpu.SR = mpu.CARRY_FLAG
        mpu.A = 0x42
        mpu.Y = 0x02
        # $1000 SBC ($FF),Y
        self._write(mpu.mem_space, 0x1000, (0xf1, 0xff))
        # Vector
        mpu.mem_space.memory_data[0x00ff] = 0x10  # low byte
        mpu.mem_space.memory_data[0x0100] = 0x20  # high byte if no page wrap
        mpu.mem_space.memory_data[0x0000] = 0x00  # high byte if page wrapped
        # Data
        mpu.mem_space.memory_data[0x2012] = 0x02  # read if no page wrap
        mpu.mem_space.memory_data[0x0012] = 0x03  # read if page wrapped
        SRrocessorCycles = self.step(cpu=mpu)
        self.assertEqual(0x3f, mpu.A)
