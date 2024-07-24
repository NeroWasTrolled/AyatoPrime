import discord
from discord import Embed, ButtonStyle
from discord.ui import Button, View
import random

class ButtonQTEView(View):
    def __init__(self, user, sequence, timeout=5):
        super().__init__(timeout=timeout)
        self.user = user
        self.sequence = sequence
        self.current_step = 0
        self.correct_presses = 0
        self.original_message = None
        self.timeout = timeout

    async def on_timeout(self):
        await self.end_qte()

    async def handle_button_click(self, interaction: discord.Interaction):
        button_id = interaction.data['custom_id']
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("Você não está participando deste QTE.", ephemeral=True)
            return

        if button_id == self.sequence[self.current_step]:
            self.correct_presses += 1
            self.current_step += 1
            if self.current_step < len(self.sequence):
                # Reduz o tempo de forma mais suave e garante que nunca fique abaixo de 2 segundos
                self.timeout = max(2, self.timeout * 0.8)
                await self.next_prompt(interaction)
            else:
                await self.end_qte(interaction)
        else:
            await self.end_qte(interaction)

    async def next_prompt(self, interaction=None):
        self.clear_items()
        button_labels = {
            "botao1": ("🟨", "Y"), 
            "botao2": ("🔴", "B"), 
            "botao3": ("🔵", "X"), 
            "botao4": ("🟩", "A")
        }
        next_id = self.sequence[self.current_step]
        next_label = button_labels[next_id][1]
        prompt_message = f"Pressione {next_label}!"

        embed = Embed(title="QuickTimeEvent", description=prompt_message)

        # Embaralhar a ordem dos botões
        buttons = list(button_labels.items())
        random.shuffle(buttons)

        for custom_id, (emoji, label) in buttons:
            button = Button(label=label, style=ButtonStyle.secondary, emoji=emoji, custom_id=custom_id)
            button.callback = self.handle_button_click
            self.add_item(button)

        if interaction:
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await self.original_message.edit(embed=embed, view=self)

    async def end_qte(self, interaction=None):
        self.stop()
        self.clear_items()

        result_message = f"{self.user.mention} acertou {self.correct_presses} de {len(self.sequence)} passos!"
        embed = Embed(title="Resultado do QuickTimeEvent", description=result_message)

        if interaction:
            await interaction.response.edit_message(view=None)
            await interaction.channel.send(embed=embed)
        else:
            await self.original_message.edit(view=None)
            await self.original_message.channel.send(embed=embed)

class ButtonQTE:
    def __init__(self, bot, ctx, user):
        self.bot = bot
        self.ctx = ctx
        self.user = user
        self.sequence = random.choices(["botao1", "botao2", "botao3", "botao4"], k=5)

    async def start(self):
        embed = Embed(title="QuickTimeEvent", description="Pressione o botão correto!")
        view = ButtonQTEView(self.user, self.sequence)
        original_message = await self.ctx.send(embed=embed, view=view)
        view.original_message = original_message
        await view.next_prompt()
