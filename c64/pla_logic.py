from dataclasses import dataclass


@dataclass
class PLAInputs:
    CAS = 0
    LORAM = 0
    HIRAM = 0
    CHAREN = 0
    VA14 = 0
    A15 = 0
    A14 = 0
    A13 = 0
    A12 = 0
    BA = 0
    AEC = 0
    R_W = 0
    EXROM = 0
    GAME = 0
    VA13 = 0
    VA12 = 0


def BASIC(pla_inputs: PLAInputs):
    return not pla_inputs.LORAM or not pla_inputs.HIRAM or not pla_inputs.A15 or pla_inputs.A14 or\
           not pla_inputs.A13 or \
           pla_inputs.AEC or not pla_inputs.R_W or not pla_inputs.GAME


def KERNAL(pla_inputs: PLAInputs):
    return ((not pla_inputs.HIRAM or not pla_inputs.A15 or not pla_inputs.A14 or not pla_inputs.A13 or pla_inputs.AEC or
             not pla_inputs.R_W or not pla_inputs.GAME) and
            (not pla_inputs.HIRAM or not pla_inputs.A15 or not pla_inputs.A14 or not pla_inputs.A13 or pla_inputs.AEC or
             not pla_inputs.R_W or pla_inputs.EXROM or pla_inputs.GAME))


def CHAROM(pla_inputs: PLAInputs):
    return ((not pla_inputs.HIRAM or pla_inputs.CHAREN or not pla_inputs.A15 or not pla_inputs.A14 or pla_inputs.A13 or
             not pla_inputs.A12 or pla_inputs.AEC or not pla_inputs.R_W or not pla_inputs.GAME) and
            (not pla_inputs.LORAM or pla_inputs.CHAREN or not pla_inputs.A15 or not pla_inputs.A14 or pla_inputs.A13 or
             not pla_inputs.A12 or pla_inputs.AEC or not pla_inputs.R_W or not pla_inputs.GAME) and
            (not pla_inputs.HIRAM or pla_inputs.CHAREN or not pla_inputs.A15 or not pla_inputs.A14 or pla_inputs.A13 or
             not pla_inputs.A12 or pla_inputs.AEC or not pla_inputs.R_W or pla_inputs.EXROM or pla_inputs.GAME) and
            (not pla_inputs.VA14 or not pla_inputs.AEC or not pla_inputs.GAME or pla_inputs.VA13 or
             not pla_inputs.VA12) and
            (not pla_inputs.VA14 or not pla_inputs.AEC or pla_inputs.EXROM or pla_inputs.GAME or pla_inputs.VA13 or
             not pla_inputs.VA12))


def Ival(b, i_):
    return ~~(i_ & (1 << b))


if __name__ == '__main__':

    # /** The input combination, at least 16 bits */

    i = -1

    initial = True

    logic_array = []

    while True:
        i += 1

        CAS_ = Ival(1, i)
        LORAM_ = Ival(2, i)
        HIRAM_ = Ival(3, i)
        CHAREN_ = Ival(4, i)
        VA14_ = Ival(5, i)
        A15 = Ival(6, i)
        A14 = Ival(7, i)
        A13 = Ival(12, i)
        A12 = Ival(14, i)
        BA = Ival(13, i)
        AEC_ = Ival(8, i)
        R_W_ = Ival(9, i)
        EXROM_ = Ival(11, i)
        GAME_ = Ival(15, i)
        VA13 = Ival(10, i)
        VA12 = Ival(0, i)

        # /** @name The output signals. */

        # /* CASRAM_ */
        F0 = ((LORAM_ and HIRAM_ and A15 and not A14 and A13 and
               not AEC_ and R_W_ and GAME_) or
              (HIRAM_ and A15 and A14 and A13 and
               not AEC_ and R_W_ and GAME_) or
              (HIRAM_ and A15 and A14 and A13 and
               not AEC_ and R_W_ and not EXROM_ and not GAME_) or
              (HIRAM_ and not CHAREN_ and A15 and A14 and not A13 and
               A12 and not AEC_ and R_W_ and GAME_) or
              (LORAM_ and not CHAREN_ and A15 and A14 and not A13 and
               A12 and not AEC_ and R_W_ and GAME_) or
              (HIRAM_ and not CHAREN_ and A15 and A14 and not A13 and
               A12 and not AEC_ and R_W_ and not EXROM_ and not GAME_) or
              (VA14_ and AEC_ and GAME_ and not VA13 and VA12) or
              (VA14_ and AEC_ and not EXROM_ and not GAME_ and not VA13 and VA12) or
              (HIRAM_ and CHAREN_ and A15 and A14 and not A13 and
               A12 and BA and not AEC_ and R_W_ and GAME_) or
              (HIRAM_ and CHAREN_ and A15 and A14 and not A13 and
               A12 and not AEC_ and not R_W_ and GAME_) or
              (LORAM_ and CHAREN_ and A15 and A14 and not A13 and
               A12 and BA and not AEC_ and R_W_ and GAME_) or
              (LORAM_ and CHAREN_ and A15 and A14 and not A13 and
               A12 and not AEC_ and not R_W_ and GAME_) or
              (HIRAM_ and CHAREN_ and A15 and A14 and not A13 and
               A12 and BA and not AEC_ and R_W_ and not EXROM_ and not GAME_) or
              (HIRAM_ and CHAREN_ and A15 and A14 and not A13 and
               A12 and not AEC_ and not R_W_ and not EXROM_ and not GAME_) or
              (LORAM_ and CHAREN_ and A15 and A14 and not A13 and
               A12 and BA and not AEC_ and R_W_ and not EXROM_ and not GAME_) or
              (LORAM_ and CHAREN_ and A15 and A14 and not A13 and
               A12 and not AEC_ and not R_W_ and not EXROM_ and not GAME_) or
              (A15 and A14 and not A13 and A12 and BA and
               not AEC_ and R_W_ and EXROM_ and not GAME_) or
              (A15 and A14 and not A13 and A12 and
               not AEC_ and not R_W_ and EXROM_ and not GAME_) or
              (LORAM_ and HIRAM_ and A15 and not A14 and not A13 and
               not AEC_ and R_W_ and not EXROM_) or
              (A15 and not A14 and not A13 and not AEC_ and EXROM_ and not GAME_) or
              (HIRAM_ and A15 and not A14 and A13 and not AEC_ and
               R_W_ and not EXROM_ and not GAME_) or
              (A15 and A14 and A13 and not AEC_ and EXROM_ and not GAME_) or
              (AEC_ and EXROM_ and not GAME_ and VA13 and VA12) or
              (not A15 and not A14 and A12 and EXROM_ and not GAME_) or
              (not A15 and not A14 and A13 and EXROM_ and not GAME_) or
              (not A15 and A14 and EXROM_ and not GAME_) or
              (A15 and not A14 and A13 and EXROM_ and not GAME_) or
              (A15 and A14 and not A13 and not A12 and EXROM_ and not GAME_) or
              CAS_)

        # /* BASIC_ */

        F1 = (not LORAM_ or not HIRAM_ or not A15 or A14 or not A13 or AEC_ or not R_W_ or not GAME_)

        # /* KERNAL_ */
        F2 = ((not HIRAM_ or not A15 or not A14 or not A13 or AEC_ or
               not R_W_ or not GAME_) and
              (not HIRAM_ or not A15 or not A14 or not A13 or AEC_ or
               not R_W_ or EXROM_ or GAME_))

        # /* CHAROM_ */
        F3 = ((not HIRAM_ or CHAREN_ or not A15 or not A14 or A13 or
               not A12 or AEC_ or not R_W_ or not GAME_) and
              (not LORAM_ or CHAREN_ or not A15 or not A14 or A13 or
               not A12 or AEC_ or not R_W_ or not GAME_) and
              (not HIRAM_ or CHAREN_ or not A15 or not A14 or A13 or
               not A12 or AEC_ or not R_W_ or EXROM_ or GAME_) and
              (not VA14_ or not AEC_ or not GAME_ or VA13 or not VA12) and
              (not VA14_ or not AEC_ or EXROM_ or GAME_ or VA13 or not VA12))

        # /* GR/W */
        F4 = (CAS_ or not A15 or not A14 or A13 or not A12 or AEC_ or R_W_)

        # /* I_O_ */
        F5 = ((not HIRAM_ or not CHAREN_ or not A15 or not A14 or A13 or
               not A12 or not BA or AEC_ or not R_W_ or not GAME_) and
              (not HIRAM_ or not CHAREN_ or not A15 or not A14 or A13 or
               not A12 or AEC_ or R_W_ or not GAME_) and
              (not LORAM_ or not CHAREN_ or not A15 or not A14 or A13 or
               not A12 or not BA or AEC_ or not R_W_ or not GAME_) and
              (not LORAM_ or not CHAREN_ or not A15 or not A14 or A13 or
               not A12 or AEC_ or R_W_ or not GAME_) and
              (not HIRAM_ or not CHAREN_ or not A15 or not A14 or A13 or
               not A12 or not BA or AEC_ or not R_W_ or EXROM_ or
               GAME_) and
              (not HIRAM_ or not CHAREN_ or not A15 or not A14 or A13 or
               not A12 or AEC_ or R_W_ or EXROM_ or GAME_) and
              (not LORAM_ or not CHAREN_ or not A15 or not A14 or A13 or
               not A12 or not BA or AEC_ or not R_W_ or EXROM_ or
               GAME_) and
              (not LORAM_ or not CHAREN_ or not A15 or not A14 or A13 or
               not A12 or AEC_ or R_W_ or EXROM_ or GAME_) and
              (not A15 or not A14 or A13 or not A12 or not BA or
               AEC_ or not R_W_ or not EXROM_ or GAME_) and
              (not A15 or not A14 or A13 or not A12 or AEC_ or
               R_W_ or not EXROM_ or GAME_))

        # /* ROML_ */
        F6 = ((not LORAM_ or not HIRAM_ or not A15 or A14 or A13 or
               AEC_ or not R_W_ or EXROM_) and
              (not A15 or A14 or A13 or AEC_ or not EXROM_ or GAME_))

        # /* ROMH_ */
        F7 = ((not HIRAM_ or not A15 or A14 or not A13 or
               AEC_ or not R_W_ or EXROM_ or GAME_) and
              (not A15 or not A14 or not A13 or AEC_ or not EXROM_ or GAME_) and
              (not AEC_ or not EXROM_ or GAME_ or not VA13 or not VA12))

        o = 0

        if F0:
            o |= 1 << 6
        if F1:
            o |= 1 << 5
        if F2:
            o |= 1 << 4
        if F3:
            o |= 1 << 3
        if F4:
            o |= 1 << 2
        if F5:
            o |= 1 << 1
        if F6:
            o |= 1 << 0
        if F7:
            o |= 1 << 7

        # print(o)
        logic_array.append(o)
        if i & 0xffff == 0 and not initial:
            break
        print(f"{i & 0xffff} {o}")

        initial = False

    file = open("c64_pla_logic.bin", "wb")
    file.write(bytearray(logic_array))
    file.close()
