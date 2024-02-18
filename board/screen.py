# PLEASE CHECK OUT MY OTHER REPO FOR EMULATOR
# MORE INFO ON THAT PAGE
# FREE TO USE, JUST STAR REPO PLZ :3
# https://github.com/TunayAdaKaracan/chip-8-emu-pygame

class Screen:
    def __init__(self, scale):
        self.cols = 64
        self.rows = 32

        self.scale = scale

        self.display = [0] * self.cols * self.rows

    def set_pixel(self, x, y):
        pixel_loc = x + (y * self.cols)
        self.display[pixel_loc] ^= 1
        return not self.display[pixel_loc]

    def clear(self):
        self.display = [0] * self.cols * self.rows

    def test_render(self):
        self.set_pixel(1, 1)
        self.set_pixel(6, 1)
        self.set_pixel(12, 0)
        self.set_pixel(0, 0)
        self.set_pixel(0, -1)