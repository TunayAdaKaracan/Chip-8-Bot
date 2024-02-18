# PLEASE CHECK OUT MY OTHER REPO FOR EMULATOR
# MORE INFO ON THAT PAGE
# FREE TO USE, JUST STAR REPO PLZ :3
# https://github.com/TunayAdaKaracan/chip-8-emu-pygame

import random
from .keyboard import VirtualKeyboard
from .screen import Screen
from .memory import VirtualMemory, Register


sprites = [
        0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
        0x20, 0x60, 0x20, 0x20, 0x70,  # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
        0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
        0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
        0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
        0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
        0xF0, 0x80, 0xF0, 0x80, 0x80   # F
]


class Chip:
    def __init__(self, screen_scale=1, start_paused=False, speed=10, schip=False, **kwargs):
        self.screen = Screen(screen_scale)
        self.keyboard = VirtualKeyboard()
        self.mem = VirtualMemory()
        self.stack_size = kwargs.get("stack_size", 24)

        self.registers = [Register() for _ in range(16)]

        self.address = Register(dtype="uint16")

        self.delay_timer = 0

        # Actually pointless until i add audio
        self.sound_timer = 0

        self.pc = 0x200  # Most programs start at mem addr 0x200
        self.stack = []

        self.paused = start_paused

        self.speed = speed

        self.__INSTRUCTION_MAP = {
            0x0000: self.opcode_0nnn,
            0x1000: self.opcode_1nnn,
            0x2000: self.opcode_2nnn,
            0x3000: self.opcode_3nnn,
            0x4000: self.opcode_4nnn,
            0x5000: self.opcode_5nnn,
            0x6000: self.opcode_6nnn,
            0x7000: self.opcode_7nnn,
            0x8000: self.opcode_8nnn,
            0x9000: self.opcode_9nnn,
            0xA000: self.opcode_Annn,
            0xB000: self.opcode_Bnnn,
            0xC000: self.opcode_Cnnn,
            0xD000: self.opcode_Dnnn,
            0xE000: self.opcode_Ennn,
            0xF000: self.opcode_Fnnn
        }

        self.last_instructions = []

        # configuration
        self.schip_mode = schip

    def load_sprites_to_mem(self):
        for i, v in enumerate(sprites):
            self.mem.set(i, v)


    def load_program_to_mem(self, program):
        for i, v in enumerate(program):
            self.mem.set(0x200 + i, v)

    def load_rom(self, file_name, relative_path="./rom/"):
        with open(relative_path+file_name, "rb") as f:
            content = f.read()
        self.load_program_to_mem(list(content))

    def tick(self):
        for _ in range(self.speed):
            if not self.paused:
                # 16-bit instructions on 8-bit memory
                opcode = (self.mem.get(self.pc) << 8 | self.mem.get(self.pc + 1))
                self.execute_inst(opcode)
            else:
                break

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def update_timers(self):
        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            self.sound_timer -= 1

    def execute_inst(self, opcode):
        self.last_instructions.append([opcode, [int(reg.get()) for reg in self.registers]])
        if len(self.last_instructions) > 5:
            self.last_instructions.pop(0)
        self.pc += 2

        opcode_type = (opcode & 0xF000)
        try:
            self.__INSTRUCTION_MAP[opcode_type](opcode)
        except KeyError:
            raise RuntimeError("Unknown opcode")
        except Exception as e:
            print(e)
            print("Unknown ERROR:")
            print("Last instructions:")
            for snapshot in self.last_instructions:
                print(f"{hex(snapshot[0])} "+' '.join([hex(val) for val in snapshot[1]]))
            exit(-1)

    # Some opcodes are structured in a way where the lowest 4-bit of highest byte is register addr
    def decode_first(self, opcode):
        return (opcode & 0xF00) >> 8

    def decode_second(self, opcode):
        return (opcode & 0xF0) >> 4

    # SYS Call
    # 00E0 = Clear Screen
    # 00EE = Return, Gets last program counter from stack and returns to that point
    def opcode_0nnn(self, opcode):
        if opcode == 0x00E0:
            return self.screen.clear()
        if opcode == 0x00EE:
            if len(self.stack) == 0:
                raise RuntimeError("Bad ROM: Trying to pop from stack which is empty")
            self.pc = self.stack.pop()

    # JMP addr/imm
    # 2kkk
    # Jump to addr
    def opcode_1nnn(self, opcode):
        self.pc = (opcode & 0xFFF)

    # CALL addr/imm
    # 2kkk
    # Saves program counter to stack and jumps to a new addr
    def opcode_2nnn(self, opcode):
        self.stack.append(self.pc)
        if len(self.stack) > self.stack_size:  # Force limit to stack size
            raise RuntimeError("BAD ROM: Stack Overflow.")
        self.pc = (opcode & 0xFFF)

    # COMP Vx imm
    # 3xkk
    # Compares register x to immediate value kk. Jump 1 instruction if eq
    def opcode_3nnn(self, opcode):
        if self.registers[self.decode_first(opcode)].get() == (opcode & 0xFF):
            self.pc += 2

    # COMP Vx imm
    # 4xkk
    # Compares register x to immediate value kk. Jump 1 instruction if neq
    def opcode_4nnn(self, opcode):
        if self.registers[self.decode_first(opcode)].get() != (opcode & 0xFF):
            self.pc += 2

    # COMP Vx Vy
    # 5xy0
    # Compares register x to register y. Jump 1 instruction if eq
    def opcode_5nnn(self, opcode):
        if (opcode & 0xF) != 0:
            return
        if self.registers[self.decode_first(opcode)].get() == self.registers[self.decode_second(opcode)].get():
            self.pc += 2

    # LOAD Vx imm
    # 6xkk
    # Loads immediate value to register x
    def opcode_6nnn(self, opcode):
        self.registers[self.decode_first(opcode)].set(opcode & 0xFF)

    # ADD Vx imm
    # 7xkk
    # Adds immediate value to register x
    def opcode_7nnn(self, opcode):
        self.registers[self.decode_first(opcode)].set(self.registers[self.decode_first(opcode)].get() + (opcode & 0xFF))

    def opcode_8nnn(self, opcode):
        last_bits = (opcode & 0xF)
        vx = self.registers[self.decode_first(opcode)]
        vy = self.registers[self.decode_second(opcode)]

        if last_bits == 0x0:
            vx.set(vy.get())
            return

        if last_bits == 0x1:
            vx.set(vx.get() | vy.get())
            return

        if last_bits == 0x2:
            vx.set(vx.get() & vy.get())
            return

        if last_bits == 0x3:
            vx.set(vx.get() ^ vy.get())
            return

        if last_bits == 0x4:
            sums = int(vx.get()) + int(vy.get())
            tmp = 0
            if sums > 0xFF:
                tmp = 1

            vx.set(sums)
            self.registers[0xF].set(tmp)
            return

        if last_bits == 0x5:
            tmp = 0
            if vx.get() >= vy.get():
                tmp = 1

            vx.set(vx.get() - vy.get())
            self.registers[0xF].set(tmp)
            return

        if last_bits == 0x6:
            if self.schip_mode:
                vx.set(vy.get())
            tmp = vx.get() & 0x1
            vx.set(vx.get() >> 1)
            self.registers[0xF].set(tmp)
            return

        if last_bits == 0x7:
            tmp = 0
            if vy.get() >= vx.get():
                tmp = 1
            vx.set(vy.get() - vx.get())
            self.registers[0xF].set(tmp)
            return

        # CARRY: Fails 2, 3
        if last_bits == 0xE:
            if self.schip_mode:
                vx.set(vy.get())
            tmp = (vx.get() & 0x80) >> 7
            vx.set((vx.get() << 1))
            self.registers[0xF].set(tmp)
            return

    def opcode_9nnn(self, opcode):
        if (opcode & 0xF) != 0:
            return
        if self.registers[self.decode_first(opcode)].get() != self.registers[self.decode_second(opcode)].get():
            self.pc += 2

    def opcode_Annn(self, opcode):
        self.address.set(opcode & 0xFFF)

    def opcode_Bnnn(self, opcode):
        self.pc = self.registers[self.decode_first(opcode)].get() + (opcode & 0xFFF)

    def opcode_Cnnn(self, opcode):
        rand = random.randint(0, 0xFF)
        self.registers[self.decode_first(opcode)].set(rand & (opcode & 0xFF))

    def opcode_Dnnn(self, opcode):
        width = 8
        height = (opcode & 0xF)
        vx = self.registers[self.decode_first(opcode)]
        vy = self.registers[self.decode_second(opcode)]
        self.registers[0xF].set(0)

        for row in range(height):
            y_position = vy.get() + row
            y_position %= 32

            sprite = self.mem.get(self.address.get() + row)

            for col in range(width):
                x_position = vx.get() + col
                x_position %= 64

                if x_position >= self.screen.cols:
                    break

                if (sprite & 0x80) > 0:
                    if self.screen.set_pixel(x_position, y_position):
                        self.registers[0xF].set(1)

                sprite <<= 1

            if y_position >= self.screen.rows:
                break


    def opcode_Ennn(self, opcode):
        last_bits = (opcode & 0xFF)
        key_check = self.registers[self.decode_first(opcode)].get() & 0xF
        if last_bits == 0x9E:
            if self.keyboard.is_key_pressed(key_check):
                self.pc += 2
            return

        if last_bits == 0xA1:
            if not self.keyboard.is_key_pressed(key_check):
                self.pc += 2

    def opcode_Fnnn(self, opcode):
        vx = self.registers[self.decode_first(opcode)]
        last_bits = (opcode & 0xFF)

        if last_bits == 0x07:
            vx.set(self.delay_timer)
            return

        if last_bits == 0x0A:
            self.paused = True

            def press(key):
                vx.set(key)
                self.paused = False

            self.keyboard.key_press_event = press
            return

        if last_bits == 0x15:
            self.delay_timer = int(vx.get())
            return

        if last_bits == 0x18:
            self.sound_timer = int(vx.get())
            return

        if last_bits == 0x1E:
            self.address.set(self.address.get() + vx.get())
            return

        if last_bits == 0x29:
            self.address.set((vx.get() & 0xF) * 5)
            return

        if last_bits == 0x33:
            self.mem.set(self.address.get(), int(vx.get() / 100))
            self.mem.set(self.address.get() + 1, int((vx.get() % 100) / 10))
            self.mem.set(self.address.get() + 2, int(vx.get() % 10))
            return

        if last_bits == 0x55:
            for i in range(((opcode & 0xF00) >> 8) + 1):
                self.mem.set(self.address.get() + i, self.registers[i].get())
            return

        if last_bits == 0x65:
            for i in range(((opcode & 0xF00) >> 8) + 1):
                self.registers[i].set(self.mem.get(self.address.get() + i))