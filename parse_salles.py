import openpyxl
from datetime import datetime, timedelta, timezone
import discord
from discord import app_commands, Embed

def create_edt(heure:int, semestre:int, day:int) -> list[int]:

    days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    days_english = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    try:
        day_number_sem = days.index(day)
    except ValueError:
        day_number_sem = days_english.index(day)
    workbook = openpyxl.load_workbook('edt salles.xlsx')

    sheet = workbook['EDT']

    # Retrieve all coordinates where the cell value is 10
    coordinates = []
    for cell in sheet[3 + (heure - 8) + 11*day_number_sem][1:]:
        val = cell.value
        if val is None or ("0" not in val and "O" not in val and "S1" not in val):
            try:
                temp = sheet.cell(row=1, column=cell.column).value
                if temp is not None:
                    coordinates.append((temp, sheet.cell(row=2, column=cell.column).value))
            except Exception as e:
                print(f"Error: {e}")

    return coordinates


def set_value(type, hour) -> str:
    if type == "sci":
        return ":test_tube: :white_check_mark:"
    if type == "info":
        return ":desktop: :no_entry:"
    if type == "colle":
        return "<:colle:1309644102345949295> :grey_question:"
    if type == "classe":
        return ":mortar_board: :white_check_mark:"
    else : return ""
def parse_edt(coordinates, hour, day):
    embeds = []

    embed1 = discord.Embed(title=f"EDT : {hour}h - {day}",
                           url="https://staticky.marsisus.me",
                           description=f"Liste des Salles disponibles à {hour}h",
                           timestamp=datetime.now())

    for i in range(min(25, len(coordinates))):
        embed1.add_field(name=f"**{coordinates[i][0]}**", inline=True, value=set_value(coordinates[i][1], hour))
    embed1.set_footer(text="Made by Marsisus, Magos, Hugo, Gabriel...       ")
    embeds.append(embed1)

    if len(coordinates) > 25:
        embed2 = discord.Embed(
                               timestamp=datetime.now())

        for i in range(25, len(coordinates)):
            embed2.add_field(name=f"**{coordinates[i][0]}**", value=set_value(coordinates[i][1], hour), inline=True)
        embed2.set_footer(text="Made by Marsisus, Magos, Hugo, Gabriel...       ")
        embeds.append(embed2)

    return embeds