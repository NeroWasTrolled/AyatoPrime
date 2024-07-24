import discord
from discord.ext import commands, tasks
import random
import re
from datetime import datetime
from custom_events import gerenciador_de_eventos
from qte import QuickTimeEvent
from button_qte import ButtonQTE

id_do_servidor = '1016374201663365290'
lucky_user_id = ''

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

rolagens_de_usuarios = {}
pity_ativo_para_usuario = {}
contador_de_pity_jackpot = {}

padrao_de_dado = re.compile(r'(\d+)d(\d+)\s*([+-]\s*\d+)?')

blocked_channels = set() 

@bot.event
async def on_ready():
    print(f'Bot está pronto como {bot.user}')
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=id_do_servidor))
        print(f"Sincronizado {len(synced)} comando(s)")
    except Exception as e:
        print(e)
    verificar_tempo_de_evento.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    match = padrao_de_dado.fullmatch(message.content.strip())

    if match and not is_channel_blocked(message.channel.id):
        user_id = message.author.id
        numero = int(match.group(1))
        tipo_dado = int(match.group(2))
        modificador = int(match.group(3).replace(" ", "")) if match.group(3) else 0
        media = (tipo_dado + 1) / 2

        if user_id not in rolagens_de_usuarios:
            rolagens_de_usuarios[user_id] = []
        if user_id not in pity_ativo_para_usuario:
            pity_ativo_para_usuario[user_id] = False
        if user_id not in contador_de_pity_jackpot:
            contador_de_pity_jackpot[user_id] = 0

        aplicar_pity = False
        jackpot_ocorreu = False

        if gerenciador_de_eventos.eventos_ativos and gerenciador_de_eventos.pode_ativar_evento(user_id):
            evento = gerenciador_de_eventos.obter_evento_para_usuario(user_id)
            if evento is None:
                if random.random() < 0.05:
                    gerenciador_de_eventos.ativar_evento_para_usuario(user_id)
                    evento = gerenciador_de_eventos.obter_evento_para_usuario(user_id)
                    embed = discord.Embed(title=f"{evento['evento'].replace('_', ' ').title()} Activated!", description=f"{message.author.mention} is now in an event!")
                    if evento['evento'] == 'adrenaline_meter':
                        file = discord.File("Adrenaline_Meter.gif", filename="Adrenaline_Meter.gif")
                        embed.set_image(url="attachment://Adrenaline_Meter.gif")
                    elif evento['evento'] == 'rage_meter':
                        file = discord.File("Rage_Meter.gif", filename="Rage_Meter.gif")
                        embed.set_image(url="attachment://Rage_Meter.gif")
                    await message.channel.send(embed=embed, file=file)

            if evento:
                if datetime.utcnow() < evento['hora_fim']:
                    rolagens = [random.randint(1, tipo_dado) for _ in range(numero)]
                    rolagens, mensagem_do_evento = gerenciador_de_eventos.obter_efeitos_do_evento(rolagens, tipo_dado, evento)
                else:
                    gerenciador_de_eventos.desativar_evento_para_usuario(user_id)

        if numero == 3:
            contador_de_pity_jackpot[user_id] += 1
            if contador_de_pity_jackpot[user_id] >= 5 or random.random() < 0.25:
                rolagens = [random.randint(1, tipo_dado) for _ in range(3)]
                contador_de_pity_jackpot[user_id] = 0
                aplicar_pity = True
                if rolagens[0] == rolagens[1] == rolagens[2]:
                    jackpot_ocorreu = True
            else:
                aplicar_pity = False
        else:
            if user_id == lucky_user_id:
                aplicar_pity = True
            else:
                aplicar_pity = len(rolagens_de_usuarios[user_id]) >= 5 and all(roll < media for roll in rolagens_de_usuarios[user_id][-5:])

            if pity_ativo_para_usuario[user_id]:
                if user_id == lucky_user_id:
                    if random.random() < 0.9:
                        aplicar_pity = True
                    else:
                        pity_ativo_para_usuario[user_id] = False
                else:
                    if random.random() < 0.5:
                        aplicar_pity = True
                    else:
                        pity_ativo_para_usuario[user_id] = False

        if not aplicar_pity:
            rolagens = [random.randint(1, tipo_dado) for _ in range(numero)]
        else:
            rolagens = [random.randint(max(1, tipo_dado - 2), tipo_dado) for _ in range(numero)]

        evento = gerenciador_de_eventos.obter_evento_para_usuario(user_id)
        if evento:
            rolagens, mensagem_do_evento = gerenciador_de_eventos.obter_efeitos_do_evento(rolagens, tipo_dado, evento)
        else:
            mensagem_do_evento = None

        rolagens_de_usuarios[user_id].append(sum(rolagens) / numero)

        resultado = ', '.join([f"**{roll}**" if roll == 1 or roll == tipo_dado else str(roll) for roll in rolagens])
        total = sum(rolagens) + modificador

        if numero == 1:
            roll = rolagens[0]
            if roll == tipo_dado:
                resultado = f"` {total} ` ⟵ [**{roll}**] {message.content}"
            elif roll == 1:
                resultado = f"` {total} ` ⟵ [**{roll}**] {message.content}"
            else:
                resultado = f"` {total} ` ⟵ [{roll}] {message.content}"
        else:
            resultado = f"` {total} ` ⟵ [{', '.join(map(str, rolagens))}] {message.content}"

        mensagem_final = resultado.strip()
        if numero == 3 and rolagens[0] == rolagens[1] == rolagens[2]:
            mensagem_final = f"# JACKPOT!\n{mensagem_final}"
        if mensagem_do_evento:
            mensagem_final = f"{mensagem_do_evento}\n\n{mensagem_final}"

        await message.reply(mensagem_final)

    await bot.process_commands(message)

def is_channel_blocked(channel_id):
    return channel_id in blocked_channels

@tasks.loop(seconds=1)
async def verificar_tempo_de_evento():
    if gerenciador_de_eventos.eventos_ativos:
        for user_id in list(gerenciador_de_eventos.usuarios_em_evento):
            evento = gerenciador_de_eventos.obter_evento_para_usuario(user_id)
            if evento and datetime.utcnow() >= evento['hora_fim']:
                gerenciador_de_eventos.desativar_evento_para_usuario(user_id)

@bot.command(name='qte')
async def qte(ctx, user1: discord.User, user2: discord.User = None):
    if not is_channel_blocked(ctx.channel.id):
        if user2:
            qte_game = QuickTimeEvent(bot, ctx, user1, user2)
        else:
            qte_game = ButtonQTE(bot, ctx, user1)
        await qte_game.start()
    else:
        await ctx.send(f"Comandos QTE estão bloqueados neste canal.")

@bot.command(name='fight')
async def fight(ctx):
    if not is_channel_blocked(ctx.channel.id):
        if gerenciador_de_eventos.eventos_ativos:
            gerenciador_de_eventos.desativar_eventos()
            await ctx.send("Eventos foram desativados.")
        else:
            gerenciador_de_eventos.ativar_eventos()
            embed = discord.Embed(title="Eventos Ativados", description="Eventos estão agora disponíveis. Role os dados para ver o que acontece!")
            await ctx.send(embed=embed)

@bot.command(name='block')
@commands.has_permissions(administrator=True)
async def block(ctx):
    blocked_channels.add(ctx.channel.id)
    await ctx.send(f"Canal {ctx.channel.name} bloqueado para comandos, exceto !unblock.")

@bot.command(name='unblock')
@commands.has_permissions(administrator=True)
async def unblock(ctx):
    if ctx.channel.id in blocked_channels:
        blocked_channels.remove(ctx.channel.id)
        await ctx.send(f"Canal {ctx.channel.name} desbloqueado para comandos.")
    else:
        await ctx.send(f"Canal {ctx.channel.name} não estava bloqueado.")

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, quantidade: int = 10):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Você não tem permissão para usar esse comando.", delete_after=10)
        return

    def nao_eh_bot_ou_webhook_ou_rolagem_de_dados(mensagem):
        return not mensagem.author.bot and not mensagem.webhook_id and not padrao_de_dado.fullmatch(mensagem.content.strip())

    if quantidade > 1000:
        await ctx.send("O limite máximo para o comando `!clear` é de 1000 mensagens.", delete_after=10)
        quantidade = 1000

    mensagens = await ctx.channel.purge(limit=quantidade, check=nao_eh_bot_ou_webhook_ou_rolagem_de_dados)
    await ctx.send(f'{len(mensagens)} mensagens foram apagadas.', delete_after=5)

bot.run('')
