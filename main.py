import discord
from discord.ext import commands, tasks
import os
from flask import Flask
from threading import Thread
import datetime

# Crear servidor web con Flask para mantener el bot en línea
app = Flask('')

@app.route('/')
def home():
    return "Bot activo 🩷"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Cargar token desde variables de entorno
TOKEN = os.getenv("DISCORD_TOKEN")
VANITY = "/gxng"
ROLE_NAME = "$"

# Configurar intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True

# Inicializar bot
bot = commands.Bot(command_prefix=",", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Conectado como {bot.user}")
    check_statuses.start()

@tasks.loop(seconds=60)
async def check_statuses():
    try:
        print(f"[{datetime.datetime.now()}] Ejecutando revisión de estados...")

        for guild in bot.guilds:
            role = discord.utils.get(guild.roles, name=ROLE_NAME)
            if not role:
                try:
                    role = await guild.create_role(name=ROLE_NAME)
                    print(f"Rol '{ROLE_NAME}' creado en {guild.name}")
                except Exception as e:
                    print(f"No se pudo crear el rol: {e}")
                    continue

            for member in guild.members:
                if member.bot:
                    continue

                status_text = ""
                for activity in member.activities:
                    if isinstance(activity, discord.CustomActivity) and activity.name:
                        status_text = activity.name.lower()

                if VANITY.lower() in status_text:
                    if role not in member.roles:
                        try:
                            await member.add_roles(role)
                            print(f"✅ Rol añadido a {member.display_name}")
                        except Exception as e:
                            print(f"❌ Error al añadir rol: {e}")
                else:
                    if role in member.roles:
                        try:
                            await member.remove_roles(role)
                            print(f"🗑️ Rol removido de {member.display_name}")
                        except Exception as e:
                            print(f"❌ Error al remover rol: {e}")
    except Exception as error:
        print(f"❗ Error en check_statuses: {error}")

# Comandos

@bot.command()
async def setstatus(ctx, *, status: str):
    await ctx.message.delete()
    await bot.change_presence(activity=discord.Game(name=status))
    msg = await ctx.send(f"Estado cambiado a: {status}")
    await msg.delete(delay=10)

@bot.command()
async def role(ctx, role: discord.Role):
    await ctx.message.delete()
    if role in ctx.author.roles:
        msg = await ctx.send(f"Ya tienes el rol {role.mention}.")
    else:
        await ctx.author.add_roles(role)
        msg = await ctx.send(f"✅ Rol {role.mention} agregado.")
    await msg.delete(delay=10)

@bot.command()
async def unrole(ctx, role: discord.Role):
    await ctx.message.delete()
    if role in ctx.author.roles:
        await ctx.author.remove_roles(role)
        msg = await ctx.send(f"❌ Rol {role.mention} eliminado.")
    else:
        msg = await ctx.send(f"No tienes el rol {role.mention}.")
    await msg.delete(delay=10)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.message.delete()
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    msg = await ctx.send("🔒 Canal bloqueado.")
    await msg.delete(delay=10)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.message.delete()
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    msg = await ctx.send("🔓 Canal desbloqueado.")
    await msg.delete(delay=10)

keep_alive()

# Iniciar el bot
bot.run(TOKEN)
