import discord
from discord import Embed, ButtonStyle
from discord.ui import Button, View
import random

class QuickTimeEventView(View):
    def __init__(self, user1, user2, max_clicks):
        super().__init__(timeout=None)
        self.user1 = user1
        self.user2 = user2
        self.scores = {user1.id: 0, user2.id: 0}
        self.max_clicks = max_clicks
        self.original_message = None

    async def handle_button_click(self, interaction: discord.Interaction):
        user = interaction.user
        print(f"QuickTimeEventView: Button clicked by {user.name} (ID: {user.id})")
        if user.id not in [self.user1.id, self.user2.id]:
            await interaction.response.send_message("Você não está participando deste QTE.", ephemeral=True)
            return

        self.scores[user.id] += 1
        print(f"QuickTimeEventView: Scores updated: {self.scores}")
        if self.scores[user.id] >= self.max_clicks:
            await self.end_qte(winner=user)
        else:
            await interaction.response.defer()

    async def end_qte(self, winner=None):
        print("QuickTimeEventView: Ending QTE")
        self.stop()
        self.clear_items()
        await self.original_message.edit(view=self)

        result_message = f"{self.user1.mention} pontuação total: {self.scores[self.user1.id]}\n"
        result_message += f"{self.user2.mention} pontuação total: {self.scores[self.user2.id]}\n\n"

        if winner:
            result_message += f"O vencedor é {winner.mention}!"
        else:
            result_message += "É um empate!"

        embed = Embed(title="Resultado do QuickTimeEvent", description=result_message)
        await self.original_message.channel.send(embed=embed)

    @discord.ui.button(label="Clique Rápido!", style=ButtonStyle.primary, custom_id="quick_click_button")
    async def click_button(self, interaction: discord.Interaction, button: Button):
        await self.handle_button_click(interaction)

class QuickTimeEvent:
    def __init__(self, bot, ctx, user1, user2):
        self.bot = bot
        self.ctx = ctx
        self.user1 = user1
        self.user2 = user2
        self.max_clicks = random.randint(10, 30)  # Valor aleatório de clicks entre 10 e 30

    async def start(self):
        embed = Embed(title="QuickTimeEvent", description="Clique no botão o mais rápido possível! O vencedor será uma surpresa!")
        view = QuickTimeEventView(self.user1, self.user2, self.max_clicks)
        original_message = await self.ctx.send(embed=embed, view=view)
        view.original_message = original_message
