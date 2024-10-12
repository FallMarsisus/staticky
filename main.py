from datetime import datetime
import discord
from discord import app_commands
from parse_colles import create_colloscope
import os 
from dotenv import load_dotenv, dotenv_values


# Créer une instance du bot
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client( intents=intents) 
tree = app_commands.CommandTree(bot)


load_dotenv()
# Événement lorsque le bot est prêt
@bot.event
async def on_ready():
    # await tree.sync(guild=discord.Object(id=1292935532472565852))

    print(f'Connecté en tant que {bot.user.name}')

    botactivity = discord.Streaming(url="https://twitch.tv/marsisus", name=" l'exiiistence.")
    await bot.change_presence(activity=botactivity)



# réagir a un message 
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "quoi" in message.content[-10:].lower():
        await message.channel.send(f"quoicoubeh {message.author.mention} !")
    if "j'aime" in message.content.lower()[:6]:
        await message.author.edit(nick=f'{message.content[6:]}')
    
    for i in range(len(message.content.split())):
        if len(message.content.split()[i]) < 4:
            continue
        if "dis" in message.content.lower().split()[i][:3] or "dit" in message.content.lower().split()[i][:3]:
            await message.channel.send(f"{message.content.split()[i][3:]}")
        elif "cri" in message.content.lower().split()[i][:3]:
            await message.channel.send(f"{message.content.upper().split()[i][3:]}")
        elif "di" in message.content.lower().split()[i][:2] or "dy" in message.content.lower().split()[i][:2]:
            await message.channel.send(f"{message.content.split()[i][2:]}")


# slash commands 
@tree.command(
    name="parse_colles",
    description="Récupérer un fichier en .ics contenant vos colles du S1",
    guild=discord.Object(id=1292935532472565852)
)
@app_commands.describe(group = "Votre Groupe de Colles. (1-16)")
@app_commands.describe(timezone = "Le fuseau Horaire UTC+n (laisser vide si vous ne savez pas), UTC+2 par défaut")
async def recup_colles(interaction:discord.Interaction, group:str, timezone:str = "Europe/Paris"):
    if 0<int(group)<17:
        create_colloscope(int(group), timezone)
        await interaction.response.send_message(content=f"Voici le fichier de colles parsé pour le groupe {group} ! ", file=discord.File("output.ics", filename=f"groupe{group}.ics") )
    else:
        await interaction.response.send_message(content="Ce groupe n'existe pas banane !")

# Slash command to get help
@tree.command(
    name="help",
    description="Afficher l'aide",
    guild=discord.Object(id=1292935532472565852)

)
async def help(interaction:discord.Interaction):
    embed = discord.Embed(title="Le Bot des MP2I[3]",
                      url="https://staticky.marsisus.me",
                      description="Bienvenue sur la page d'aide du bot !\n#Voici les commandes disponibles :\n - `/parse_colles [groupe] {timezone}` : Récupérer un fichier en .ics contenant vos colles du S1\n - `/help` : Afficher l'aide",
                      colour=0x00b0f4,
                      timestamp=datetime.now())

    embed.set_author(name="Staticky",
                 url="https://staticky.marsisus.me",)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# Lancer le bot
bot.run(os.getenv('BOT_TOKEN'))