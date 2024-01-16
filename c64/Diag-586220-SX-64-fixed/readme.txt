Diag 586220++ SX-64 fixed.
--------------------------


The original Commodore Diag 586220 module can't identify if it's running on an C64 or an SX64.
That wouldn't be a problem at all, but the SX-64 has no Tape-Port and the SX-64 Kernal
has a different checksum. So the original Diag 586220 marks the Kernal as BAD and
INTERRUPT test fails as BAD because the diagnostic hardware (eg. Check64) won't detect
the FLAG IRQ from Tape-Port.

This modified version has now a fixed SX64 detection and an fixed IRQ test when it's
running on SX-64 hardware. To get a valid test result, the original SX-64 Kernal has
to be enabled. Kernal-Replacements like JiffyDOS must be deactivated.

Only with real SX-64 Kernal AND THE DIAGNOSTIC HARDWARE ATTACHED TO THE SYSTEM is a 
100% hardware diagnostic possible ! Please see the attached pictures.

This version depends on an extended (plus) version of Marty / Radwar, the disassembly is from
World of Jani. It detects 49 different Kernal-Versions by checksum.

Have fun with Diag 586220++ SX-64 fixed.


KiWi / www.SX-64.de

