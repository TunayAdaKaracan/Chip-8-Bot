# PLEASE CHECK OUT MY OTHER REPO FOR EMULATOR
# MORE INFO ON THAT PAGE
# FREE TO USE, JUST STAR REPO PLZ :3
# https://github.com/TunayAdaKaracan/chip-8-emu-pygame

import numpy


class VirtualMemory:
    def __init__(self, size=4096):
        self.mem = numpy.array([0] * size).astype(numpy.uint8)

    def set(self, addr, data):
        self.mem[addr] = numpy.array(data).astype(numpy.uint8)

    def get(self, addr):
        return self.mem[addr]


class Register:
    def __init__(self, dtype="uint8"):
        self.type = getattr(numpy, dtype)
        self.val = numpy.array(0).astype(self.type)

    def set(self, data):
        self.val = numpy.array(data).astype(self.type)

    def get(self):
        return self.val
