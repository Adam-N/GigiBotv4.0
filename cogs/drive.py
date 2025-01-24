import asyncio
import datetime as dt
import json
import os
import tempfile
from os.path import exists
import requests
import discord
from PIL import Image
from discord import app_commands
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials

import gspread as gspread

from discord.ext import commands, tasks


class Drive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 334925467431862272
        self.scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name("config/service_account.json", self.scope)
        self.temp_file_deletion.start()

    def cog_unload(self):
        self.temp_file_deletion.cancel()

    @tasks.loop(minutes=30)
    async def temp_file_deletion(self):
        for filename in os.listdir('config/temp'):
            f = os.path.join('config/temp', filename)
            # checking if it is a file
            if os.path.isfile(f):
                os.remove(f)

    async def get_sunday(self):
        year, week, weekday = dt.datetime.now().isocalendar()
        if weekday == 7:
            week += 1
        elif weekday != 7:
            weekday = 7

        return dt.datetime.fromisocalendar(year, week, weekday)


    async def weekly_reminder(self, server_id):
        if int(server_id) != self.guild_id:
            return
        gc = gspread.service_account()
        guild = self.bot.get_guild(server_id)
        sh = gc.open("Schedule for Triumphant")
        sheet = sh.sheet1
        sunday = dt.datetime.today()
        time_cell = sheet.find(f"{sunday.strftime('%B %d, %Y')}", in_column=1)
        name_cell = sheet.cell(time_cell.row, 2)
        for_tag = sheet.find(f"{name_cell.value}", in_column=4)
        id_cell = sheet.cell(for_tag.row, 6)
        id = id_cell.numeric_value
        user = guild.get_member(int(id))
        with open(f'config/{guild.id}/config.json', 'r') as f:
            config = json.load(f)
        channel = guild.get_channel(config["triumphant_config"]["triumph_channel"])
        await channel.send(f"{user.mention} it's your turn this week!")
        await channel.send(f"Here is a drive link with any media from the week: {await self.share()}")

    @app_commands.command(name="drive_tag")
    @commands.is_owner()
    async def tag(self, ctx):
        await self.weekly_reminder(ctx.guild.id)

    async def create(self):
        service = build('drive', 'v3', credentials=self.credentials)

        fileMetadata = {
            'name': str((await self.get_sunday()).strftime('%B %d, %Y')),
            'mimeType': "application/vnd.google-apps.folder",
            'parents': ["1DRi4GMQOWtg2-yEVShXdGv-Yp6aGENcd"]
        }

        newFolder = service.files().create(body=fileMetadata, fields='id').execute()

        doc_fileMetadata = {
            'name': str(f"{(await self.get_sunday()).strftime('%B %d, %Y')} - Text File"),
            'mimeType': "application/vnd.google-apps.document",
            'parents': [newFolder["id"]]
        }
        new_doc = service.files().create(body=doc_fileMetadata, fields='id').execute()

    @app_commands.command(name="drive_list")
    @commands.is_owner()
    async def list(self, interaction:discord.Interaction):
        service = build('drive', 'v3', credentials=self.credentials)
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        print(items)

    @app_commands.command(name="drive_remove")
    @commands.is_owner()
    async def remove(self, interaction:discord.Interaction):
        service = build('drive', 'v3', credentials=self.credentials)
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        print(f"Before: {items}")
        for file in items:
            if file['name'] == "April 24, 2022":
                service.files().delete(fileId=file["id"], supportsAllDrives=True).execute()
        print(f"After: {items}")

    async def text_file(self, text):
        service = build('drive', 'v3', credentials=self.credentials)
        text =  "\n \n \n" + text + "\n================================ \n"
        response = service.files().list(
            q=f"mimeType= 'application/vnd.google-apps.document' and name='{(await self.get_sunday()).strftime('%B %d, %Y')} - Text File'",
            spaces='drive',
            fields='files(id, name, parents)').execute()
        doc_service = build('docs', 'v1', credentials=self.credentials)

        items = response.get('files', [])
        to_insert = [
            {
                'insertText': {
                    'location': {
                        'index': 1,
                        "segmentId": None
                    },

                    'text': f"{text} \n \n"
                }
            }]

        result = doc_service.documents().batchUpdate(
            documentId=items[0]['id'], body={'requests': to_insert}).execute()

    async def upload(self, image: discord.message.Attachment):
        service = build('drive', 'v3', credentials=self.credentials)
        response = service.files().list(
            q=f"mimeType= 'application/vnd.google-apps.folder' and name='{str((await self.get_sunday()).strftime('%B %d, %Y'))}'",
            spaces='drive',
            fields='files(id, name)').execute()
        items = response.get('files', [])
        name = os.path.splitext(f"{image.filename}")[0]
        fileMetadata = {
            'name': str(f"{name}.png"),
            'parents': [items[0]["id"]]
        }


        img = Image.open(requests.get(image.url, stream=True).raw)
        temp_file = tempfile.NamedTemporaryFile(mode='w+b', suffix='.png', dir='config/temp', delete=False)
        img.save(temp_file.name, format='PNG')

        media = MediaFileUpload(temp_file.name, mimetype='image/png')
        service.files().create(
            body=fileMetadata, media_body=media, fields='id').execute()

    async def share(self):
        service = build('drive', 'v3', credentials=self.credentials)
        response = service.files().list(
            q=f"mimeType= 'application/vnd.google-apps.folder' and name='{str((await self.get_sunday()).strftime('%B %d, %Y'))}'",
            spaces='drive',
            fields='files(id, name)').execute()
        items = response.get('files', [])

        request_body = {
            'role': 'reader',
            'type': 'anyone'
        }
        file_id = items[0]["id"]

        response_permission = service.permissions().create(
            fileId=file_id,
            body=request_body
        ).execute()

        response_share_link = service.files().get(
            fileId=file_id,
            fields='webViewLink'
        ).execute()
        link = response_share_link.get("webViewLink", [])
        return link


    # For testing
    """@commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        print('in')
        channel = await self.bot.fetch_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        if msg.attachments:
            await self.upload(msg.attachments[0])"""


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Drive(bot))
