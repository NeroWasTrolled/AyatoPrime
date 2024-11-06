import discord
from discord.ext import commands
from discord.ui import View, Button
from asyncio import sleep

class Enquete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.votos = {}

    async def remover_reacao_anterior(self, payload, usuarios_permitidos):
        canal = self.bot.get_channel(payload.channel_id)
        mensagem = await canal.fetch_message(payload.message_id)
        usuario = payload.member or await self.bot.fetch_user(payload.user_id)

        if mensagem.id in self.votos:
            usuario_reacoes = self.votos[mensagem.id].get(usuario.id)
            if usuario_reacoes:
                for reaction in mensagem.reactions:
                    if reaction.emoji == usuario_reacoes and reaction.count > 1:
                        await mensagem.remove_reaction(reaction.emoji, usuario)
                        break

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        canal = self.bot.get_channel(payload.channel_id)
        mensagem = await canal.fetch_message(payload.message_id)
        emoji = payload.emoji.name
        usuario = payload.member or await self.bot.fetch_user(payload.user_id)

        if mensagem.id in self.votos:
            usuarios_permitidos = self.votos[mensagem.id].get("permitidos", [])
            if usuarios_permitidos and usuario.id not in usuarios_permitidos:
                await mensagem.remove_reaction(emoji, usuario)
            else:
                await self.remover_reacao_anterior(payload, usuarios_permitidos)
                self.votos[mensagem.id][usuario.id] = emoji

    async def criar_enquete(self, ctx, descricao, opcoes, emojis, respostas):
        usuarios_mencionados = [user.id for user in ctx.message.mentions]
        embed = discord.Embed(title="**📊 Enquete**", description=descricao, color=0x1f8b4c)
        embed.set_footer(text="Reaja com um emoji para votar!")

        mensagem = await ctx.send(embed=embed)
        self.votos[mensagem.id] = {"permitidos": usuarios_mencionados}

        for emoji in emojis:
            await mensagem.add_reaction(emoji)

        tempo_de_votacao = 10
        await sleep(tempo_de_votacao)

        mensagem = await ctx.fetch_message(mensagem.id)
        await mensagem.delete()

        reacoes = mensagem.reactions
        votos = {opcao: 0 for opcao in opcoes}

        for reacao in reacoes:
            if reacao.emoji in emojis:
                indice = emojis.index(reacao.emoji)
                votos[opcoes[indice]] = reacao.count - 1

        if all(voto == 0 for voto in votos.values()):
            embed_nenhum_voto = discord.Embed(
                title="**⏳ Sem Escolha**",
                description="Nenhuma escolha foi efetuada, com isso o narrador pode decidir os acontecimentos.",
                color=0xff0000
            )
            await ctx.send(embed=embed_nenhum_voto)
        else:
            max_votos = max(votos.values())
            vencedores = [opcao for opcao, count in votos.items() if count == max_votos]

            if len(vencedores) > 1:
                resultado_embed = discord.Embed(
                    title="**🤝 Resultado da Enquete - Empate**",
                    description="Houve um empate nas escolhas, o narrador decidirá o que acontecerá a seguir.",
                    color=0xff0000
                )
            else:
                opcao_vencedora = vencedores[0]
                resultado_embed = discord.Embed(
                    title="**🏆 Resultado da Enquete**",
                    description=respostas[opcao_vencedora],
                    color=0x00ff00
                )
            await ctx.send(embed=resultado_embed)

    @commands.command(name='rotas')
    @commands.has_permissions(administrator=True)
    async def rotas(self, ctx):
        descricao = (
            "Você se encontra em uma encruzilhada, por qual caminho seguirá?\n"
            "⬅️ - Esquerda\n"
            "⬆️ - Meio\n"
            "➡️ - Direita"
        )
        opcoes = ["Esquerda", "Meio", "Direita"]
        emojis = ['⬅️', '⬆️', '➡️']
        respostas = {
            "Esquerda": "A opção escolhida e mais votada foi de ir para a Esquerda.",
            "Meio": "A opção escolhida e mais votada foi de seguir pelo Meio.",
            "Direita": "A opção escolhida e mais votada foi de ir para a Direita."
        }
        await self.criar_enquete(ctx, descricao, opcoes, emojis, respostas)

    @commands.command(name='avanço')
    @commands.has_permissions(administrator=True)
    async def avancar(self, ctx):
        descricao = (
            "Você está em um momento crucial, o que deseja fazer?\n"
            "⬆️ - Continuar\n"
            "🛑 - Parar\n"
            "↩️ - Retornar"
        )
        opcoes = ["Continuar", "Parar", "Retornar"]
        emojis = ['⬆️', '🛑', '↩️']
        respostas = {
            "Continuar": "A opção escolhida e mais votada foi de Continuar.",
            "Parar": "A opção escolhida e mais votada foi de Parar.",
            "Retornar": "A opção escolhida e mais votada foi de Retornar."
        }
        await self.criar_enquete(ctx, descricao, opcoes, emojis, respostas)

    @commands.command(name='combate')
    @commands.has_permissions(administrator=True)
    async def combate(self, ctx):
        descricao = (
            "Escolha sua ação de combate:\n"
            "⚔️ - Atacar\n"
            "🛡️ - Defender\n"
            "🏃 - Desviar\n"
            "🔁 - Contra-atacar"
        )
        opcoes = ["Atacar", "Defender", "Desviar", "Contra-atacar"]
        emojis = ['⚔️', '🛡️', '🏃', '🔁']
        respostas = {
            "Atacar": "A opção escolhida e mais votada foi de Atacar.",
            "Defender": "A opção escolhida e mais votada foi de Defender.",
            "Desviar": "A opção escolhida e mais votada foi de Desviar.",
            "Contra-atacar": "A opção escolhida e mais votada foi de Contra-atacar."
        }
        await self.criar_enquete(ctx, descricao, opcoes, emojis, respostas)

    @commands.command(name='exploracao')
    @commands.has_permissions(administrator=True)
    async def exploracao(self, ctx):
        descricao = (
            "Você encontra uma área de interesse, o que deseja fazer?\n"
            "🔍 - Investigar\n"
            "🚶 - Ignorar\n"
            "🗺️ - Marcar no mapa"
        )
        opcoes = ["Investigar", "Ignorar", "Marcar no mapa"]
        emojis = ['🔍', '🚶', '🗺️']
        respostas = {
            "Investigar": "A opção escolhida e mais votada foi de Investigar a área.",
            "Ignorar": "A opção escolhida e mais votada foi de Ignorar a área.",
            "Marcar no mapa": "A opção escolhida e mais votada foi de Marcar no mapa."
        }
        await self.criar_enquete(ctx, descricao, opcoes, emojis, respostas)

    @commands.command(name='interagir')
    @commands.has_permissions(administrator=True)
    async def interacao_npc(self, ctx):
        descricao = (
            "Você encontra um NPC, como deseja interagir?\n"
            "💬 - Conversar\n"
            "😠 - Intimidar\n"
            "💰 - Subornar"
        )
        opcoes = ["Conversar", "Intimidar", "Subornar"]
        emojis = ['💬', '😠', '💰']
        respostas = {
            "Conversar": "A opção escolhida e mais votada foi de Conversar com o NPC.",
            "Intimidar": "A opção escolhida e mais votada foi de Intimidar o NPC.",
            "Subornar": "A opção escolhida e mais votada foi de Subornar o NPC."
        }
        await self.criar_enquete(ctx, descricao, opcoes, emojis, respostas)

    @commands.command(name='armadilha')
    @commands.has_permissions(administrator=True)
    async def armadilha(self, ctx):
        descricao = (
            "Você encontra uma armadilha, o que deseja fazer?\n"
            "✋ - Desarmar\n"
            "🏃 - Evitar\n"
            "⚡ - Acionar intencionalmente"
        )
        opcoes = ["Desarmar", "Evitar", "Acionar intencionalmente"]
        emojis = ['✋', '🏃', '⚡']
        respostas = {
            "Desarmar": "A opção escolhida e mais votada foi de Desarmar a armadilha.",
            "Evitar": "A opção escolhida e mais votada foi de Evitar a armadilha.",
            "Acionar intencionalmente": "A opção escolhida e mais votada foi de Acionar intencionalmente a armadilha."
        }
        await self.criar_enquete(ctx, descricao, opcoes, emojis, respostas)

    @commands.command(name='rota')
    @commands.has_permissions(administrator=True)
    async def rota(self, ctx):
        descricao = (
            "Escolha o caminho a seguir:\n"
            "🛡️ - Seguir o caminho seguro\n"
            "⚔️ - Escolher o atalho perigoso\n"
            "🗺️ - Procurar um caminho alternativo"
        )
        opcoes = ["Seguir o caminho seguro", "Escolher o atalho perigoso", "Procurar um caminho alternativo"]
        emojis = ['🛡️', '⚔️', '🗺️']
        respostas = {
            "Seguir o caminho seguro": "A opção escolhida e mais votada foi de Seguir o caminho seguro.",
            "Escolher o atalho perigoso": "A opção escolhida e mais votada foi de Escolher o atalho perigoso.",
            "Procurar um caminho alternativo": "A opção escolhida e mais votada foi de Procurar um caminho alternativo."
        }
        await self.criar_enquete(ctx, descricao, opcoes, emojis, respostas)

    @commands.command(name='grupo')
    @commands.has_permissions(administrator=True)
    async def grupo(self, ctx):
        descricao = (
            "Como o grupo deve proceder?\n"
            "✋ - Dividir o grupo\n"
            "🤝 - Permanecer junto\n"
            "🧭 - Seguir um líder"
        )
        opcoes = ["Dividir o grupo", "Permanecer junto", "Seguir um líder"]
        emojis = ['✋', '🤝', '🧭']
        respostas = {
            "Dividir o grupo": "A opção escolhida e mais votada foi de Dividir o grupo.",
            "Permanecer junto": "A opção escolhida e mais votada foi de Permanecer junto.",
            "Seguir um líder": "A opção escolhida e mais votada foi de Seguir um líder."
        }
        await self.criar_enquete(ctx, descricao, opcoes, emojis, respostas)

    @commands.command(name='clima')
    @commands.has_permissions(administrator=True)
    async def clima(self, ctx):
        descricao = (
            "O tempo está mudando, o que fazer?\n"
            "🏠 - Procurar abrigo\n"
            "🚶 - Continuar a jornada\n"
            "🔮 - Usar magia/clima"
        )
        opcoes = ["Procurar abrigo", "Continuar a jornada", "Usar magia/clima"]
        emojis = ['🏠', '🚶', '🔮']
        respostas = {
            "Procurar abrigo": "A opção escolhida e mais votada foi de Procurar abrigo.",
            "Continuar a jornada": "A opção escolhida e mais votada foi de Continuar a jornada.",
            "Usar magia/clima": "A opção escolhida e mais votada foi de Usar magia/clima."
        }
        await self.criar_enquete(ctx, descricao, opcoes, emojis, respostas)

    @commands.command(name='pistas')
    @commands.has_permissions(administrator=True)
    async def pistas(self, ctx):
        descricao = (
            "Você encontra pistas importantes, o que fazer?\n"
            "🔍 - Analisar as pistas\n"
            "❓ - Perguntar aos habitantes locais\n"
            "🧭 - Seguir o instinto"
        )
        opcoes = ["Analisar as pistas", "Perguntar aos habitantes locais", "Seguir o instinto"]
        emojis = ['🔍', '❓', '🧭']
        respostas = {
            "Analisar as pistas": "A opção escolhida e mais votada foi de Analisar as pistas.",
            "Perguntar aos habitantes locais": "A opção escolhida e mais votada foi de Perguntar aos habitantes locais.",
            "Seguir o instinto": "A opção escolhida e mais votada foi de Seguir o instinto."
        }
        await self.criar_enquete(ctx, descricao, opcoes, emojis, respostas)

    @commands.command(name='enigma')
    @commands.has_permissions(administrator=True)
    async def enigma(self, ctx):
        descricao = (
            "Você encontra um enigma, como deseja reagir?\n"
            "🧠 - Tentar resolver o enigma\n"
            "🚶 - Ignorar e seguir em frente\n"
            "🔍 - Procurar ajuda externa"
        )
        opcoes = ["Tentar resolver o enigma", "Ignorar e seguir em frente", "Procurar ajuda externa"]
        emojis = ['🧠', '🚶', '🔍']
        respostas = {
            "Tentar resolver o enigma": "A opção escolhida e mais votada foi de Tentar resolver o enigma.",
            "Ignorar e seguir em frente": "A opção escolhida e mais votada foi de Ignorar e seguir em frente.",
            "Procurar ajuda externa": "A opção escolhida e mais votada foi de Procurar ajuda externa."
        }
        await self.criar_enquete(ctx, descricao, opcoes, emojis, respostas)

    @commands.command(name='comercio')
    @commands.has_permissions(administrator=True)
    async def comercio(self, ctx):
        descricao = (
            "Você chegou a um mercado, o que deseja fazer?\n"
            "🛒 - Comprar suprimentos\n"
            "💰 - Vender itens\n"
            "🔄 - Trocar informações"
        )
        opcoes = ["Comprar suprimentos", "Vender itens", "Trocar informações"]
        emojis = ['🛒', '💰', '🔄']
        respostas = {
            "Comprar suprimentos": "A opção escolhida e mais votada foi de Comprar suprimentos.",
            "Vender itens": "A opção escolhida e mais votada foi de Vender itens.",
            "Trocar informações": "A opção escolhida e mais votada foi de Trocar informações."
        }
        await self.criar_enquete(ctx, descricao, opcoes, emojis, respostas)

    @commands.command(name='resgate')
    @commands.has_permissions(administrator=True)
    async def resgate(self, ctx):
        descricao = (
            "Você encontra um prisioneiro, o que fazer?\n"
            "🆘 - Resgatar o prisioneiro\n"
            "❓ - Interrogar o inimigo\n"
            "🛡️ - Escoltar o NPC para segurança"
        )
        opcoes = ["Resgatar o prisioneiro", "Interrogar o inimigo", "Escoltar o NPC para segurança"]
        emojis = ['🆘', '❓', '🛡️']
        respostas = {
            "Resgatar o prisioneiro": "A opção escolhida e mais votada foi de Resgatar o prisioneiro.",
            "Interrogar o inimigo": "A opção escolhida e mais votada foi de Interrogar o inimigo.",
            "Escoltar o NPC para segurança": "A opção escolhida e mais votada foi de Escoltar o NPC para segurança."
        }
        await self.criar_enquete(ctx, descricao, opcoes, emojis, respostas)

    @commands.command(name='moral')
    @commands.has_permissions(administrator=True)
    async def moral(self, ctx):
        descricao = (
            "Você testemunha uma situação moral, como reage?\n"
            "🤝 - Ajudar o necessitado\n"
            "🚶 - Ignorar o problema\n"
            "💼 - Tirar proveito da situação"
        )
        opcoes = ["Ajudar o necessitado", "Ignorar o problema", "Tirar proveito da situação"]
        emojis = ['🤝', '🚶', '💼']
        respostas = {
            "Ajudar o necessitado": "A opção escolhida e mais votada foi de Ajudar o necessitado.",
            "Ignorar o problema": "A opção escolhida e mais votada foi de Ignorar o problema.",
            "Tirar proveito da situação": "A opção escolhida e mais votada foi de Tirar proveito da situação."
        }
        await self.criar_enquete(ctx, descricao, opcoes, emojis, respostas)

    @commands.command(name='ajuda')
    async def ajuda(self, ctx):
        pages = [
            discord.Embed(title="``` 𝐀𝐉𝐔𝐃𝐀 - 𝐄𝐍𝐐𝐔𝐄𝐓𝐄𝐒 𝐃𝐄 𝐀𝐂̧𝐀̃𝐎 ```", description="""
            **__ESCOLHA DE ROTA__**
            `!rotas`
            - > **Escolha entre Esquerda, Meio ou Direita.**

            **__DECISÃO DE AVANÇO__**
            `!avanço`
            - > **Decida entre Continuar, Parar ou Retornar.**

            **__AÇÃO DE COMBATE__**
            `!combate`
            - > **Escolha sua ação de combate: Atacar, Defender, Desviar ou Contra-atacar.**
            """, color=discord.Color.blue()),

            discord.Embed(title="``` 𝐀𝐉𝐔𝐃𝐀 - 𝐄𝐗𝐏𝐋𝐎𝐑𝐀𝐂̧𝐀̃𝐎 𝐄 𝐈𝐍𝐓𝐄𝐑𝐀𝐂̧𝐀̃𝐎```", description="""
            **__EXPLORAÇÃO DE TERRENO__**
            `!exploracao`
            - > **Decida o que fazer em uma área de interesse: Investigar, Ignorar ou Marcar no mapa.**

            **__INTERAÇÃO COM NPC__**
            `!interacao_npc`
            - > **Decida como interagir com um NPC: Conversar, Intimidar ou Subornar.**

            **__REAÇÃO A ARMADILHA__**
            `!armadilha`
            - > **Reaja a uma armadilha: Desarmar, Evitar ou Acionar intencionalmente.**
            """, color=discord.Color.blue()),

            discord.Embed(title="``` 𝐀𝐉𝐔𝐃𝐀 - 𝐆𝐑𝐔𝐏𝐎𝐒 𝐄 𝐃𝐄𝐂𝐈𝐒𝐎̃𝐄𝐒 𝐃𝐄 𝐑𝐎𝐓𝐀```", description="""
            **__ESCOLHA DE ROTA__**
            `!rota`
            - > **Escolha o caminho a seguir: Seguir o caminho seguro, Escolher o atalho perigoso ou Procurar um caminho alternativo.**

            **__DECISÃO DE GRUPO__**
            `!grupo`
            - > **Decida a estratégia do grupo: Dividir o grupo, Permanecer junto ou Seguir um líder.**
            """, color=discord.Color.blue()),

            discord.Embed(title="``` 𝐀𝐉𝐔𝐃𝐀 - 𝐄𝐕𝐄𝐍𝐓𝐎𝐒 𝐂𝐋𝐈𝐌𝐀́𝐓𝐈𝐂𝐎𝐒 𝐄 𝐏𝐈𝐒𝐓𝐀𝐒 ```", description="""
            **__EVENTO CLIMÁTICO__**
            `!clima`
            - > **Reaja a um evento climático: Procurar abrigo, Continuar a jornada ou Usar magia/clima.**

            **__INVESTIGAÇÃO DE PISTAS__**
            `!pistas`
            - > **Decida como lidar com pistas encontradas: Analisar as pistas, Perguntar aos habitantes locais ou Seguir o instinto.**
            """, color=discord.Color.blue()),

            discord.Embed(title="``` 𝐀𝐉𝐔𝐃𝐀 - 𝐄𝐍𝐈𝐆𝐌𝐀𝐒 𝐄 𝐂𝐎𝐌𝐄́𝐑𝐂𝐈𝐎 ```", description="""
            **__RESOLUÇÃO DE ENIGMA__**
            `!enigma`
            - > **Reaja a um enigma: Tentar resolver o enigma, Ignorar e seguir em frente ou Procurar ajuda externa.**

            **__DECISÃO DE COMÉRCIO__**
            `!comercio`
            - > **Decida o que fazer em um mercado: Comprar suprimentos, Vender itens ou Trocar informações.**
            """, color=discord.Color.blue()),

            discord.Embed(title="``` 𝐀𝐉𝐔𝐃𝐀 - 𝐌𝐈𝐒𝐒𝐎̃𝐄𝐒 𝐄 𝐌𝐎𝐑𝐀𝐋 ```", description="""
            **__MISSÃO DE RESGATE OU ESCOLTA__**
            `!resgate`
            - > **Decida em uma missão de resgate ou escolta: Resgatar o prisioneiro, Interrogar o inimigo ou Escoltar o NPC para segurança.**

            **__AÇÃO MORAL__**
            `!moral`
            - > **Reaja a uma situação moral: Ajudar o necessitado, Ignorar o problema ou Tirar proveito da situação.**
            """, color=discord.Color.blue()),

            discord.Embed(title="``` 𝐀𝐉𝐔𝐃𝐀 - 𝐐𝐔𝐈𝐂𝐊 𝐓𝐈𝐌𝐄 𝐄𝐕𝐄𝐍𝐓𝐒 ```", description="""
            **__QTE DE BOTÕES__**
            `!qte @usuário`
            - > **Teste seus reflexos com o QuickTime Event de botões. Siga as instruções de botões e pressione rapidamente!**

            **__QTE DE CLIQUES RÁPIDOS__**
            `!qte @usuário1 @usuário2`
            - > **Desafie outro jogador em uma competição de cliques rápidos! O primeiro a atingir o número máximo de cliques vence.**
            """, color=discord.Color.blue())
        ]

        current_page = 0

        async def update_page(interaction):
            await interaction.response.edit_message(embed=pages[current_page], view=create_view())

        def create_view():
            view = View()
            prev_button = Button(label="⏮️", style=discord.ButtonStyle.primary)
            next_button = Button(label="⏭️", style=discord.ButtonStyle.primary)
            first_button = Button(label="⏪", style=discord.ButtonStyle.primary)
            last_button = Button(label="⏩", style=discord.ButtonStyle.primary)
            jump_button = Button(label="...", style=discord.ButtonStyle.primary)

            async def prev_button_callback(interaction):
                nonlocal current_page
                current_page = (current_page - 1) % len(pages)
                await update_page(interaction)

            async def next_button_callback(interaction):
                nonlocal current_page
                current_page = (current_page + 1) % len(pages)
                await update_page(interaction)

            async def first_button_callback(interaction):
                nonlocal current_page
                current_page = 0
                await update_page(interaction)

            async def last_button_callback(interaction):
                nonlocal current_page
                current_page = len(pages) - 1
                await update_page(interaction)

            async def jump_button_callback(interaction):
                modal = JumpToPageModal(len(pages), update_page)
                await interaction.response.send_modal(modal)

            prev_button.callback = prev_button_callback
            next_button.callback = next_button_callback
            first_button.callback = first_button_callback
            last_button.callback = last_button_callback
            jump_button.callback = jump_button_callback

            view.add_item(first_button)
            view.add_item(prev_button)
            view.add_item(jump_button)
            view.add_item(next_button)
            view.add_item(last_button)
            return view

        class JumpToPageModal(discord.ui.Modal):
            def __init__(self, total_pages, update_page_callback):
                super().__init__(title="Ir para página")
                self.total_pages = total_pages
                self.update_page_callback = update_page_callback

                self.page_number = discord.ui.TextInput(label="Número da página", style=discord.TextStyle.short)
                self.add_item(self.page_number)

            async def on_submit(self, interaction):
                nonlocal current_page
                try:
                    page = int(self.page_number.value) - 1
                    if 0 <= page < self.total_pages:
                        current_page = page
                        await self.update_page_callback(interaction)
                    else:
                        await interaction.response.send_message(f"Número de página inválido. Digite um número entre 1 e {self.total_pages}.", ephemeral=True)
                except ValueError:
                    await interaction.response.send_message("Por favor, digite um número válido.", ephemeral=True)

        await ctx.send(embed=pages[current_page], view=create_view())

async def setup(bot):
    await bot.add_cog(Enquete(bot))
