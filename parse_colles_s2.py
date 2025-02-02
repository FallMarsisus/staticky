import openpyxl
from datetime import datetime, timedelta, timezone
import locale
import calendar
import pytz
from ics import Calendar, Event

# Open the Excel file

def create_colloscope_s2(groupe:int, timezone:str = "Europe/Paris"):
    try: 
        pytz.timezone(timezone)
        timezone = timezone
    except pytz.UnknownTimeZoneError:
        timezone = "Europe/Paris"
    c = Calendar()

    workbook = openpyxl.load_workbook('colloscope.xlsx')

    # Access a specific sheet
    sheet = workbook['Colloscope S2']

    # Do something with the sheet, such as reading data or modifying it
    # Retrieve all coordinates where the cell value is 10
    coordinates = []
    for row in sheet.iter_rows():
        for cell in row:
            if cell.value == groupe:
                coordinates.append((cell.row, cell.column))

    # Retrieve additional information for each coordinate starting from the 6th row
    for coordinate in coordinates:
        row = coordinate[0]
        if row < 6:
            continue
        column = coordinate[1]
        matière = sheet[f'A{row}'].value
        if not matière:
            continue
        matière = matière.capitalize()
        professor = sheet[f'B{row}'].value
        room = sheet[f'D{row}'].value
        hour = sheet[f'E{row}'].value
        duration = sheet[f'F{row}'].value  # Assuming the duration is in column F
        # Convert column number to letter
        column_letter = chr(ord('A') + column - 1)
        date_str = sheet[f'{column_letter}1'].value  # Ligne 1 pour les dates à partir de la colonne G
        if date_str is None:
            continue
        try:
            date = datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            continue
        except TypeError:
            date = date_str
        try:
            day_sem = sheet[f"C{row}"].value
        except TypeError or day_sem is None:
            continue
        if day_sem is None:
            continue 
        day_sem = str(day_sem).split(" ")[0].capitalize()
        days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        days_english = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        try:
            day_number_sem = days.index(day_sem)
        except ValueError:
            day_number_sem = days_english.index(day_sem)
        # Combine day_number_sem with date
        new_days = day_number_sem + date.day;
        if new_days > 30 and date.month in [4, 6, 9, 11]:
            new_days = new_days - 30;
            new_month = date.month + 1;
        elif new_days > 31 and date.month in [1, 3, 5, 7, 8, 10, 12]:
            new_days = new_days - 31;
            new_month = date.month + 1;
        else :
            new_month = date.month;
        if (new_month <9):
            combined_date = datetime(2025, new_month, new_days).date()
        else:
            combined_date = datetime(2024, new_month, new_days).date()
        

        if professor == None:
            continue;
        

        try: 
            start_time = datetime.strptime(hour.split('-')[0], "%Hh%M").time()
        except ValueError:
            start_time = datetime.strptime(hour.split('-')[0], "%Hh").time()
        duration_hours = int(duration)
        duration_minutes = int((duration - duration_hours) * 60)
        

        # Calculate the end time by adding the duration to the start time
        end_time = (datetime.combine(date.today(), start_time) + timedelta(hours=duration_hours, minutes=duration_minutes)).time()

        # Create a new datetime object with the combined date and start time
        start_datetime = datetime.combine(combined_date, start_time)
        
        # Create a new datetime object with the combined date and end time
        end_datetime = datetime.combine(combined_date, end_time)

    
        print(f"Day: {day_sem}")
        print(f"Date: {combined_date}")
        print(f"Start time: {start_datetime}")
        print(f"End time: {end_datetime}")
        print(f"Subject: {matière}")
        print(f"Professor: {professor}")
        print(f"Room: {room}")
        print("--------------------")

        e = Event()
        e.name = f"Colle {matière}"

        e.begin = start_datetime.astimezone(pytz.timezone(timezone))
        e.duration = timedelta(hours=duration_hours, minutes=duration_minutes)
        e.location = f"{room} - Saint-Louis"
        e.description = f"Professeur: {professor}\nSalle: {room}\nMatière : {matière}"
        e.organizer = f"Groupe {groupe}"
        e.alarms = []
        c.events.add(e)
        
    # Save the changes
    workbook.save('colloscope.xlsx')


    with open(f'output_s2.ics', 'w') as my_file:
        my_file.writelines(c)

    # Close the workbook
    workbook.close()

def next_colle(groupe: int, timezone: str = "Europe/Paris"):
    try: 
        pytz.timezone(timezone)
        timezone = timezone
    except pytz.UnknownTimeZoneError:
        timezone = "Europe/Paris"
    c = Calendar()
    create_colloscope_s2(groupe, timezone)
    with open(f'output_s2.ics', 'r') as my_file:
        c = Calendar(my_file.read())

    now = datetime.now(pytz.timezone(timezone))
    next_colle_info = None

    for event in c.events:
        if event.begin > now:
            if next_colle_info is None or event.begin < next_colle_info['start_time']:
                next_colle_info = {
                    'day': event.begin.format('dddd', locale='fr_FR'),
                    'date': event.begin.date(),
                    'start_time': event.begin,
                    'end_time': event.end,
                    'subject': event.name.replace("Colle ", ""),
                    'professor': event.description.split('\n')[0].replace("Professeur: ", ""),
                    'room': event.location.split(' - ')[0]
                }

    return next_colle_info
