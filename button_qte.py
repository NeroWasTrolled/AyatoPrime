import discord
from discord import Embed, ButtonStyle
from discord.ui import Button, View
import random

class ButtonQTEView(View):
    def __init__(self, user, sequence, initial_timeout=5):
        super().__init__(timeout=initial_timeout)
        self.user = user
        self.sequence = sequence
        self.current_step = 0
        self.correct_presses = 0
        self.original_message = None
        self.initial_timeout = initial_timeout
        self.timeout = initial_timeout
        self.in_progress = True
        self.is_reverse = False  # For reverse order power-up

    async def on_timeout(self):
        if self.in_progress:
            await self.end_qte(success=False)

    async def handle_button_click(self, interaction: discord.Interaction):
        if not self.in_progress:
            return

        button_id = interaction.data['custom_id']
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("Você não está participando deste QTE.", ephemeral=True)
            return

        expected_id = self.sequence[::-1][self.current_step] if self.is_reverse else self.sequence[self.current_step]
        if button_id == expected_id:
            self.correct_presses += 1
            self.current_step += 1
            if self.current_step < len(self.sequence):
                self.timeout = max(1, self.timeout * 0.8)
                await self.next_prompt(interaction)
            else:
                await self.end_qte(interaction, success=True)
        else:
            await self.end_qte(interaction, success=False)

    async def next_prompt(self, interaction=None):
        self.clear_items()
        button_labels = {
            "botao1": ("🟨", "Y"), 
            "botao2": ("🔴", "B"), 
            "botao3": ("🔵", "X"), 
            "botao4": ("🟩", "A"),
            "botao5": ("🟧", "LB"),  # Additional buttons for more challenge
            "botao6": ("🟦", "RB")
        }
        next_id = self.sequence[::-1][self.current_step] if self.is_reverse else self.sequence[self.current_step]
        next_label = button_labels[next_id][1]
        prompt_message = f"Pressione {next_label}!"

        embed = Embed(title="QuickTimeEvent", description=prompt_message)

        # Assegura que o botão correto está presente nos botões exibidos
        displayed_buttons = [next_id]
        while len(displayed_buttons) < 4:
            possible_button = random.choice(list(button_labels.keys()))
            if possible_button not in displayed_buttons:
                displayed_buttons.append(possible_button)

        random.shuffle(displayed_buttons)

        for custom_id in displayed_buttons:
            emoji, label = button_labels[custom_id]
            button = Button(label=label, style=ButtonStyle.secondary, emoji=emoji, custom_id=custom_id)
            button.callback = self.handle_button_click
            self.add_item(button)

        if interaction:
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await self.original_message.edit(embed=embed, view=self)

    async def end_qte(self, interaction=None, success=False):
        self.in_progress = False
        self.stop()
        self.clear_items()

        if success:
            result_message = f"{self.user.mention} completou a sequência! Acertos: {self.correct_presses}/{len(self.sequence)} 🎉"
            encouragement = "Incrível! Você foi super rápido!" if self.correct_presses == len(self.sequence) else "Bom trabalho! Continue praticando para melhorar ainda mais!"
        else:
            result_message = f"{self.user.mention} errou! Acertos: {self.correct_presses}/{len(self.sequence)} 😞"
            encouragement = "Não desista! Tente novamente e veja se consegue acertar todos os passos!"

        embed = Embed(title="Resultado do QuickTimeEvent", description=result_message)
        embed.set_footer(text=encouragement)

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
        self.sequence = self.generate_sequence()

    def generate_sequence(self, length=7):
        buttons = ["botao1", "botao2", "botao3", "botao4", "botao5", "botao6"]
        sequence = []
        last_choice = None
        for _ in range(length):
            next_choice = random.choice(buttons)
            while next_choice == last_choice:
                next_choice = random.choice(buttons)
            sequence.append(next_choice)
            last_choice = next_choice
        return sequence

    async def start(self):
        embed = Embed(title="QuickTimeEvent", description="Prepare-se para pressionar os botões na sequência correta!")
        view = ButtonQTEView(self.user, self.sequence)
        original_message = await self.ctx.send(embed=embed, view=view)
        view.original_message = original_message
        await view.next_prompt()
