import datetime
import discord
from discord.ext import commands, tasks
from board.cpu import Chip


bot = commands.Bot(".", intents=discord.Intents.all())


emus = {}


@tasks.loop(seconds=1/60)
async def update_timers_all_chips():
    for val in emus.values():
        val[1].update_timers()


@tasks.loop(seconds=1)
async def tick_all_chips():
    for user_id, values in emus.items():
        if (datetime.datetime.now() - values[0]).seconds >= 1:
            values[1].tick()
            emus[user_id][0] = datetime.datetime.now()
            await values[2].edit(embed=create_embed(render_display(values[1])))


def key_press(user, key):
    _, chip, _ = emus[user]
    chip.keyboard.key_down(key)
    chip.tick()
    chip.keyboard.key_up(key)
    emus[user][0] = datetime.datetime.now()
    return render_display(chip)


def render_display(chip):
    pixels = 0
    all_pixels = []
    index = 7
    for bit in chip.screen.display:
        pixels |= (bit << index)
        if index == 0:
            all_pixels.append(pixels)
            pixels = 0
            index = 8
        index -= 1
    return ','.join([str(val) for val in all_pixels])


def create_embed(text):
    scale = 8
    embed = discord.Embed(title="GamePad Window")
    embed.set_image(url=f"https://api.kutuptilkisi.dev?scale={scale}&data={text}")  # PRIVATE API ON MY RPI | DO NOT REQUEST | %99 OF TIME OFFLINE
    return embed


class GamePad(discord.ui.View):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user

    async def edit(self, i, k):
        await i.edit_original_message(embed=create_embed(key_press(self.user, k)))

    @discord.ui.button(label="1", style=discord.ButtonStyle.green)
    async def key_1(self, button, interaction):
        await self.edit(interaction, 0x1)

    @discord.ui.button(label="2", style=discord.ButtonStyle.green)
    async def key_2(self, button, interaction):
        await self.edit(interaction, 0x2)

    @discord.ui.button(label="3", style=discord.ButtonStyle.green)
    async def key_3(self, button, interaction):
        await self.edit(interaction, 0x3)

    @discord.ui.button(label="C", style=discord.ButtonStyle.green)
    async def key_C(self, button, interaction):
        await self.edit(interaction, 0xC)

    @discord.ui.button(label="Pause", style=discord.ButtonStyle.red)
    async def key_pause(self, button, interaction):
        emus[self.user][1].pause()
        await interaction.response.send_message("Paused")

    @discord.ui.button(label="4", style=discord.ButtonStyle.green)
    async def key_4(self, button, interaction):
        await self.edit(interaction, 0x4)

    @discord.ui.button(label="5", style=discord.ButtonStyle.green)
    async def key_5(self, button, interaction):
        await self.edit(interaction, 0x5)

    @discord.ui.button(label="6", style=discord.ButtonStyle.green)
    async def key_6(self, button, interaction):
        await self.edit(interaction, 0x6)

    @discord.ui.button(label="D", style=discord.ButtonStyle.green)
    async def key_D(self, button, interaction):
        await self.edit(interaction, 0xD)

    @discord.ui.button(label="Resume", style=discord.ButtonStyle.red)
    async def key_Resume(self, button, interaction):
        emus[self.user][1].resume()
        await interaction.response.send_message("Resuming")

    @discord.ui.button(label="7", style=discord.ButtonStyle.green)
    async def key_7(self, button, interaction):
        await self.edit(interaction, 0x7)

    @discord.ui.button(label="8", style=discord.ButtonStyle.green)
    async def key_8(self, button, interaction):
        await self.edit(interaction, 0x8)

    @discord.ui.button(label="9", style=discord.ButtonStyle.green)
    async def key_9(self, button, interaction):
        await self.edit(interaction, 0x9)

    @discord.ui.button(label="E", style=discord.ButtonStyle.green)
    async def key_E(self, button, interaction):
        await self.edit(interaction, 0xE)

    @discord.ui.button(label="Kill", style=discord.ButtonStyle.red)
    async def key_kill(self, button, interaction):
        del emus[self.user]
        await interaction.response.send_message("Killed emulator")
        self.stop()

    @discord.ui.button(label="A", style=discord.ButtonStyle.green)
    async def key_A(self, button, interaction):
        await self.edit(interaction, 0xA)

    @discord.ui.button(label="0", style=discord.ButtonStyle.green)
    async def key_0(self, button, interaction):
        await self.edit(interaction, 0x0)

    @discord.ui.button(label="B", style=discord.ButtonStyle.green)
    async def key_B(self, button, interaction):
        await self.edit(interaction, 0xB)

    @discord.ui.button(label="F", style=discord.ButtonStyle.green)
    async def key_F(self, button, interaction):
        await self.edit(interaction, 0xF)


@bot.event
async def on_ready():
    print("Ready")
    update_timers_all_chips.start()
    tick_all_chips.start()


@bot.command("play")
async def play(ctx: commands.Context, speed=None):
    if not speed:
        speed = 10
    else:
        speed = int(speed)

    if len(ctx.message.attachments) == 0:
        await ctx.send("Please upload a rom while using the command")
        return

    attach = ctx.message.attachments[0]
    chip = Chip(1, False, speed)
    chip.load_sprites_to_mem()
    chip.load_program_to_mem(await attach.read())
    message = await ctx.send("Your game is here!", embed=create_embed(render_display(chip)), view=GamePad(ctx.author.id))
    emus[ctx.author.id] = [datetime.datetime.now(), chip, message]


bot.run("<you are pretty sneaky, aren't you>")
