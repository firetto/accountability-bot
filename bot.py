import discord
import datetime
from discord.ext import commands, tasks

# Google Sheets API imports
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Discord Bot Setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Google Sheets API Setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'credentials.json'  # Your service account JSON file

# Create credentials and build the Sheets API service
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=creds)

# Spreadsheet details (replace with your own)
SPREADSHEET_ID = '1pELDQAtI_zociYCnMZQRK6qllRNZVYiS1dmnuEMA-6A'
RANGE_NAME = 'Sheet1!A1:A8'  # Adjust the range as needed

target_time = datetime.time(hour=5, minute=7, tzinfo=datetime.timezone.utc)
@tasks.loop(time=target_time)
async def daily_task():
    channel = bot.get_channel(1357576514899677206)  # Replace with your channel ID

    try:
        # Fetch data
        sheet = sheets_service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range='Sheet1').execute()
        values = result.get('values', [])

        if not values or len(values) < 2:
            await channel.send("Spreadsheet has no data.")
            return

        headers = values[0]
        rows = values[1:]

        messages = []
        for row in rows:
            name = row[0]
            for i in range(1, len(headers)):
                subject = headers[i]
                value = row[i] if i < len(row) else ""
                if value.strip() == "":
                    messages.append(f"Hey {name}, go do your {subject.lower()}! You lazy ass!")

        if messages:
            await channel.send("\n".join(messages))
        else:
            await channel.send("All tasks completed! Good job!")

    except Exception as e:
        await channel.send(f"Error while checking the sheet: {e}")


@bot.command(name='getsheet')
async def get_sheet_data(ctx):
    """Fetches data from a Google Sheet and sends it to Discord."""
    try:
        
        # Call the Sheets API to fetch data
        sheet = sheets_service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            await ctx.send("No data found in the sheet.")
            return

        # Format the data for Discord output
        output = ""
        for row in values:
            # Join each row's columns with a comma
            output += ", ".join(row) + "\n"

        # Discord messages have a character limit, so we wrap the text in a code block.
        await ctx.send(f"```\n{output}\n```")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        
@bot.command(name='getsheets')
async def get_all_sheets(ctx):
    """Fetches data from a Google Sheet and sends it to Discord."""
    try:
        # Fetch spreadsheet metadata
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = spreadsheet.get('sheets', [])
        sheet_names = [sheet['properties']['title'] for sheet in sheets]

        if sheet_names:
            await ctx.send("Sheet names:\n" + "\n".join(sheet_names))
        else:
            await ctx.send("No sheets found in the spreadsheet.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    daily_task.start()

with open("token.txt") as f:
    token = f.readline()
    # Run the bot (replace with your actual Discord bot token)
    bot.run(token)
    
    
