from datetime import datetime
import discord
from discord import app_commands
from parse_colles import create_colloscope
from parse_colles_s2 import create_colloscope_s2, next_colle
from parse_salles import create_edt, parse_edt, create_image
import os
from dotenv import load_dotenv, dotenv_values
import random as rng


# Créer une instance du bot
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


exclusions = ["dire", "dis", "disons", "dites", "dîtes", "dit"]

load_dotenv()


# Événement lorsque le bot est prêt
@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1292935532472565852))

    print(f"Connecté en tant que {bot.user.name}")

    botactivity = discord.Streaming(
        url="https://twitch.tv/marsisus", name=" l'exiiistence."
    )
    await bot.change_presence(activity=botactivity)


async def hour_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    hours = ["8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18"]
    return [
        app_commands.Choice(name=hour, value=hour)
        for hour in hours
        if current.lower() in hour.lower()
    ]


async def day_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
    return [
        app_commands.Choice(name=day, value=day)
        for day in days
        if current.lower() in day.lower()
    ]


# réagir a un message
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if "quoi" in message.content[-10:].lower():
        r = rng.randint(0,1000)
        if r == 1 :
            await message.channel.send(f"quoicoubeh {message.author.mention} !")
        else : 
            await message.channel.send(f"FEUUR {message.author.mention} !!!")
    if "j'aime" in message.content.lower()[:6]:
        await message.author.edit(nick=f"{message.content[6:]}")

    for i in range(len(message.content.split())):
        if message.channel.id == 1292943453423931493 or message.channel.id == 1304556681774239784:
            return
        if message.content.lower().split()[i] in exclusions:
            continue
        if len(message.content.split()[i]) < 4:
            continue
        if (
            "dis" in message.content.lower().split()[i][:3]
            or "dit" in message.content.lower().split()[i][:3]
        ):
            await message.channel.send(f"{message.content.split()[i][3:]}")
        elif "cri" in message.content.lower().split()[i][:3]:
            await message.channel.send(f"{message.content.upper().split()[i][3:]}")
        elif (
            "di" in message.content.lower().split()[i][:2]
            or "dy" in message.content.lower().split()[i][:2]
        ):
            await message.channel.send(f"{message.content.split()[i][2:]}")


# slash commands
@tree.command(
    name="parse_colles",
    description="Récupérer un fichier en .ics contenant vos colles du S1",
    guild=discord.Object(id=1292935532472565852),
)
@app_commands.describe(group="Votre Groupe de Colles. (1-16)")
@app_commands.describe(
    timezone="Le fuseau Horaire UTC+n (laisser vide si vous ne savez pas), UTC+2 par défaut"
)
async def recup_colles(
    interaction: discord.Interaction, group: str, timezone: str = "Europe/Paris"
):
    if 0 < int(group) < 17:
        create_colloscope(int(group), timezone)
        await interaction.response.send_message(
            content=f"Voici le fichier de colles parsé pour le groupe {group} ! ",
            file=discord.File("output.ics", filename=f"groupe{group}.ics"),
        )
    else:
        await interaction.response.send_message(
            content="Ce groupe n'existe pas banane !"
        )


@tree.command(
    name="free_rooms",
    description="Trouver les salles libres à un moment donné",
    guild=discord.Object(id=1292935532472565852),
)
@app_commands.describe(hour="L'heure de la journée (par défault maintenant) (sans le h)")
@app_commands.autocomplete(hour=hour_autocomplete)
@app_commands.describe(day="Le jour de la semaine (par défault aujourd'hui)")
@app_commands.autocomplete(day=day_autocomplete)
@app_commands.describe(room="(FACULTATIF) Si vous souhaitez une salle en particulier")
async def recup_edt(
    interaction: discord.Interaction,
    day: str = datetime.now().strftime("%A"),
    hour: str = datetime.now().strftime("%H"),
    room: str = "",
):
    if 8 <= int(hour) <= 18:
        free_rooms = create_edt(int(hour), 1, day.capitalize())
        # embeds = parse_edt(sorted(free_rooms), hour, day.capitalize())
        # await interaction.response.send_message(embed=embeds[0])
        # if len(embeds) == 2:
        #     await interaction.followup.send(embed=embeds[1])
        if room == "":
            create_image(free_rooms, hour, day.capitalize())
            await interaction.response.send_message(file=discord.File("edt.png"))
        else:
            for salle in free_rooms:
                if salle[0] == room:
                    await interaction.response.send_message(
                        content=f"La salle {room} est libre à {hour}h le {day}!"
                    )
                    return
            await interaction.response.send_message(
                content=f"La salle {room} n'est pas libre à {hour}h le {day}!"
            )

        

    else:
        await interaction.response.send_message(
            content=f"Je ne connais pas {hour} heure(s)..."
        )


# Slash command to get help
@tree.command(
    name="help",
    description="Afficher l'aide",
    guild=discord.Object(id=1292935532472565852),
)
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Le Bot des MP2I[3]",
        url="https://staticky.marsisus.me",
        description="""
Bienvenue sur la page d'aide du bot !
Voici les commandes disponibles :
- `/parse_colles [groupe] {timezone}`
: Récupérer un fichier en .ics contenant vos colles du S1
- `/free_rooms {jour} {heure}`
: Trouver les salles libres à un moment donné
- `/help` : Afficher l'aide""",
        colour=0x00B0F4,
        timestamp=datetime.now(),
    )

    embed.set_author(
        name="Staticky",
        url="https://staticky.marsisus.me",
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


# Slash command to add a colle to the marketplace
@tree.command(
    name="add_colle",
    description="!!NE FONCTIONNE PAS !! Ajoute une collle au marketplace",
    guild=discord.Object(id=1292935532472565852),
)
@app_commands.describe(group="Votre Groupe de Colles. (1-16)")
@app_commands.describe(day="Format: JJ/MM/AAAA, bien réspécter le format")
@app_commands.describe(hour='L\'heure de la colle, sans le "h"')
@app_commands.autocomplete(hour=hour_autocomplete)
@app_commands.describe(teacher="Le nom du professeur")
@app_commands.describe(
    subject="La matière de la colle (Maths, Physique, Anglais, Lettres)"
)
# @app_commands.autocomplete(subject=["Maths", "Physique", "Anglais", "Lettres"])
@app_commands.describe(room="La salle de la colle")
# @app_commands.autocomplete(group=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"])


async def add_colle(
    interaction: discord.Interaction,
    group: str,
    day: str,
    hour: str,
    teacher: str,
    subject: str,
    room: str,
):
    # "ASSERTIONS" A IMPLEMENTER !!!!
    embed = discord.Embed(
        title=f"Colle de {subject}",
        description=f"Date : {day} {hour}h00\nProfesseur : {teacher}\nSalle : {room}\n Groupe : {group}\n\n! ENCORE EN PHASE DE TEST ! NON FONCTIONNEL !",
        colour=0xF50083,
        timestamp=datetime.now(),
    )

    embed.set_author(name=f"{interaction.user.name}")

    await interaction.response.send_message(embed=embed)


@tree.command(
    name="parse_colles_s2",
    description="Récupérer un fichier en .ics contenant vos colles du S2",
    guild=discord.Object(id=1292935532472565852),
)
@app_commands.describe(group="Votre Groupe de Colles. (1-16)")
@app_commands.describe(
    timezone="Le fuseau Horaire UTC+n (laisser vide si vous ne savez pas), UTC+2 par défaut"
)
async def recup_colles_s2(
    interaction: discord.Interaction, group: str, timezone: str = "Europe/Paris"
):
    if 0 < int(group) < 17:
        create_colloscope_s2(int(group), timezone)
        await interaction.response.send_message(
            content=f"Voici le fichier de colles parsé pour le groupe {group} ! ",
            file=discord.File("output_s2.ics", filename=f"groupe{group}_s2.ics"),
        )
    else:
        await interaction.response.send_message(
            content="Ce groupe n'existe pas banane !"
        )


@tree.command(
    name="next_colle",
    description="Récupérer les informations de la prochaine colle du S2 pour un groupe",
    guild=discord.Object(id=1292935532472565852),
)
@app_commands.describe(group="Votre Groupe de Colles. (1-16)")
@app_commands.describe(
    timezone="Le fuseau Horaire UTC+n (laisser vide si vous ne savez pas), UTC+2 par défaut"
)
async def next_colle_s2(
    interaction: discord.Interaction, group: str, timezone: str = "Europe/Paris"
):
    if 0 < int(group) < 17:
        colle_info = next_colle(int(group), timezone)
        if colle_info:
            embed = discord.Embed(
                title=f"Prochaine Colle de {colle_info['subject']}",
                description=f"""
                Date : {colle_info['date']}
                Jour : {colle_info['day']}
                Heure de début : {colle_info['start_time']}
                Heure de fin : {colle_info['end_time']}
                Professeur : {colle_info['professor']}
                Salle : {colle_info['room']}
                """,
                colour=0x00B0F4,
                timestamp=datetime.now(),
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                content=f"Aucune colle trouvée pour le groupe {group}."
            )
    else:
        await interaction.response.send_message(
            content="Ce groupe n'existe pas banane !"
        )

# Lancer le bot
bot.run(os.getenv("BOT_TOKEN"))
