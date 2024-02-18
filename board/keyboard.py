# PLEASE CHECK OUT MY OTHER REPO FOR EMULATOR
# MORE INFO ON THAT PAGE
# FREE TO USE, JUST STAR REPO PLZ :3
# https://github.com/TunayAdaKaracan/chip-8-emu-pygame

DEFAULT_KEYBINDINGS = {
    49: 0x1,  # 1
    50: 0x2,  # 2
    51: 0x3,  # 3
    52: 0xc,  # 4
    113: 0x4,  # Q
    119: 0x5,  # W
    101: 0x6,  # E
    114: 0xD,  # R
    97: 0x7,  # A
    115: 0x8,  # S
    100: 0x9,  # D
    102: 0xE,  # F
    122: 0xA,  # Z
    120: 0x0,  # X
    99: 0xB,  # C
    118: 0xF  # V
}


class VirtualKeyboard:
    def __init__(self, key_bindings=None):
        self.KEYMAP = key_bindings or DEFAULT_KEYBINDINGS

        self.keys_pressed = []

        self.key_press_for_event = None
        self.key_press_event = None

    def is_key_pressed(self, key):
        return key in self.keys_pressed

    def key_down(self, key):
        if key not in self.KEYMAP and key not in self.KEYMAP.values():
            return
        self.keys_pressed.append(self.KEYMAP[key] if key in self.KEYMAP else key)
        if self.key_press_event and not self.key_press_for_event:
            self.key_press_for_event = key

    def key_up(self, key):
        if key not in self.KEYMAP and key not in self.KEYMAP.values():
            return
        if self.key_press_for_event and self.key_press_event:
            self.key_press_event(self.KEYMAP[self.key_press_for_event] if key in self.KEYMAP else key)
            self.key_press_event = None
            self.key_press_for_event = None
        self.keys_pressed.remove(self.KEYMAP[key] if key in self.KEYMAP else key)