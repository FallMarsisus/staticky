import openpyxl
from datetime import datetime, timedelta, timezone
import discord
from discord import app_commands, Embed
from PIL import Image, ImageDraw, ImageFont

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
    if type == "Amphi":
        return "🧪 Amphi"
    if type == "TP":
        return "🔬 TP"
    if type == "Info":
        return "💻 Info"
    if type == "Colle":
        return "📖 Colle"
    if type == "Classe":
        return "🎓 Classe"
    if type == "?":
        return "❓ Inconnu"
    else:
        return ""
def create_image(coordinates, hour, day):
    # Create a larger blank image with a custom background color
    img = Image.new('RGB', (800, 5000), color=(60, 63, 65))
    draw = ImageDraw.Draw(img)

    # Load a less formal and slightly larger font
    font = ImageFont.truetype("font.ttf", 45)
    title_font = ImageFont.truetype("font.ttf", 55)
    
    # Title
    title = f"EDT : {hour}h - {day}"
    draw.text((400 - (draw.textbbox((0, 0), title, font=title_font)[2] - draw.textbbox((0, 0), title, font=title_font)[0]) // 2, 20), title, fill="white", font=title_font)

    # Description
    description = f"Liste des Salles disponibles à {hour}h"
    draw.text((400 - (draw.textbbox((0, 0), description, font=font)[2] - draw.textbbox((0, 0), description, font=font)[0]) // 2, 80), description, fill="white", font=font)

    # Draw the table header with a different color
    header = ["Salle", "Type"]
    x_text = [200, 600]
    for i, h in enumerate(header):
        draw.text((x_text[i] - (draw.textbbox((0, 0), h, font=font)[2] - draw.textbbox((0, 0), h, font=font)[0]) // 2, 140), h, fill="white", font=font)

    # Define background colors for each type of room
    type_colors = {
        "Amphi": (255, 153, 153),
        "TP": (153, 204, 255),
        "Info": (255, 204, 204),
        "Colle": (255, 255, 153),
        "Classe": (255, 229, 153),
        "?": (224, 224, 224)
    }

    # Sort coordinates by room type
    coordinates.sort(key=lambda x: x[1])

    # Draw the coordinates in a table format with alternating row colors
    y_text = 200
    line_height = 45
    padding = 8
    for i, (room, room_type) in enumerate(coordinates):
        if y_text + line_height + padding > 3000:
            break
        fill_color = type_colors.get(room_type, (150, 150, 150))
        
        # Draw rounded rectangle
        draw.rounded_rectangle([(0, y_text), (800, y_text + line_height)], radius=20, fill=fill_color)
        
        text_y = y_text + (line_height - font.getbbox(room)[3]) // 2
        
        # Draw the room name
        draw.text((200 - (draw.textbbox((0, 0), room, font=font)[2] - draw.textbbox((0, 0), room, font=font)[0]) // 2, text_y), room, fill="black", font=font)
        
        # Draw the room type in darker gray
        draw.text((600 - (draw.textbbox((0, 0), set_value(room_type, hour), font=font)[2] - draw.textbbox((0, 0), set_value(room_type, hour), font=font)[0]) // 2, text_y), set_value(room_type, hour), fill="gray", font=font)
        
        y_text += line_height + padding

    # Resize the image to fit the content
    img = img.crop((0, 0, 800, y_text))

    img.save("edt.png")

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