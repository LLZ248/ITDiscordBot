#!/usr/bin/env python3
import json
import os
import random
import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
prefix = "IT!"
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix=prefix)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


class MiscCog(commands.Cog, name="Misc Category"):
    @commands.command(name='roll_dice', help='Simulates rolling dice.')
    async def roll(self, ctx, number_of_dice: int, number_of_sides: int):
        dice = [
            str(random.choice(range(1, number_of_sides + 1)))
            for _ in range(number_of_dice)
        ]
        await ctx.send(', '.join(dice))

    @commands.command(name='quote', help='display a random quote')
    async def getRandomQuote(self, ctx):
        token = True
        while token:
            max = 12842 + 1
            num = random.randint(1, max)
            url = f"http://www.quotationspage.com/quote/{num}.html"
            x = requests.get(url=url)
            quote = x.text
            if quote.find("ERROR: No such quotation number.") == -1:
                token = False
                start = quote.find("<dl>") + len("<dl>")
                end = quote.find("</dl>")
                quote = quote[start:end]

                start = quote.find("<dd class=\"author\">") + len("<dd class=\"author\"><b>")
                end = quote.find("</b>")
                author = quote[start:end]
                author = author[author.find(">") + 1:]
                author = author[:author.find("<")]

                quote = quote.replace("<dt>", "")
                quote = quote.replace("</dt>", "")
                end = quote.find("<dd class=\"author\"><b>")
                quote = quote[:end]

                print(f"quote sent.")
                await ctx.send(f"{quote}- {author}")

    @commands.command(name='dailyZodiac', help='DAILY HOROSCOPE')
    async def daily_zodiac_horoscope(self, ctx, zodiac: str = "NA"):
        if zodiac == "NA":
            await ctx.send(f"Please give a zodiac sign. EG:{prefix}dailyZodiac Virgo or {prefix}dailyZodiac virgo")
            return
        zodiac = zodiac.lower()
        validZodiacs = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius",
                        "capricorn",
                        "aquarius", "pisces"]
        if zodiac in validZodiacs:
            url = f"https://www.astrology.com/horoscope/daily/{zodiac}.html"
            x = requests.get(url)
            # strip the message from the whole html page
            start = x.text.find('<p><span style="font-weight: 400">') + len('<p><span style="font-weight: 400">')
            end = x.text.find('</span></p>')
            msg = x.text[start:end]
            # remove the unwanted html tags
            msg = msg.replace(f'<a href="https://www.astrology.com/zodiac-signs/{zodiac}">', "")
            msg = msg.replace("</span>", "")
            msg = msg.replace("</a>", "")
            msg = msg.replace("<span style=\"font-weight: 400\">", "")
            await ctx.send(msg)
        else:
            await ctx.send(f"Invalid Zodiac Sign Given! Valid Zodiac Signs are {','.join(validZodiacs)}")


class ClassCog(commands.Cog, name="Class Category"):
    @commands.command(name='findClassWithCode', help='Find the class timetable and information with class code. Last Updated:2/9/2021')
    async def findClassWithCode(self, ctx, classCode: str = "NA"):
        if classCode == "NA":
            await ctx.send(f"Please give a class code. EG:BIT200")
            return

        with open("ITClasses-Sem3-2021.json") as jsonFile:
            allClasses = json.load(jsonFile)

        found = False
        for itclass in allClasses["ITClasses"]:
            if classCode in itclass["code"]:
                msg = itclass["code"] + " " + itclass["name"] + "\n" + itclass["lecturer"]
                if len(itclass["slots"]) == 0:
                    msg = msg + "\nNo time slots"
                else:
                    for slot in itclass["slots"]:
                        msg = msg + "\n" + slot["mode"] + ": " + slot["day"] + " " + slot["time"]
                found = True
                await ctx.send(msg)
                break
        if not found:
            await ctx.send(f"There is no class with code \"{classCode}\" ⊙﹏⊙∥")


class AdminCog(commands.Cog, name="Admin Category"):
    """
    Commands for admin use
    """

    @commands.command(name='create-channel')
    @commands.has_role('admin')
    async def create_channel(self, ctx, channel_name='test'):
        guild = ctx.guild
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if not existing_channel:
            print(f'Creating a new channel: {channel_name}')
            await guild.create_text_channel(channel_name)

    @commands.command(name='create-class',
                      help="Create a single class(category with the name includes text and voice channel)")
    @commands.has_role('admin')
    async def create_class(self, ctx, class_name='default-class'):
        class_name = class_name.upper()
        guild = ctx.guild
        existing_category = discord.utils.get(guild.categories, name=class_name)
        if not existing_category:
            role = await guild.create_role(name=class_name)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
                role: discord.PermissionOverwrite(read_messages=True)
            }
            category = await guild.create_category(class_name, overwrites=overwrites)
            print(f'\033[97mCreating a new class: {class_name}')
            await category.create_text_channel(f"text-chit-chat")
            await category.create_voice_channel(f"voice-chit-chat")

            await ctx.send(f"╰(*°▽°*)╯ Class {class_name} has been created.")
            print(f"\033[92mClass {class_name} has been created.")
        else:
            await ctx.send(f"（＞人＜；） Class {class_name} is already existed.")

    @commands.command(name='create-classes', help="Create multiple classes, separate with <,> Eg: BIT100,BIT101")
    @commands.has_role('admin')
    async def create_classes(self, ctx, class_names='default-classes'):
        guild = ctx.guild
        for class_name in class_names.replace(" ", "").split(","):
            class_name = class_name.upper()
            existing_category = discord.utils.get(guild.categories, name=class_name)
            if not existing_category:
                role = await guild.create_role(name=class_name)
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True),
                    role: discord.PermissionOverwrite(read_messages=True)
                }
                category = await guild.create_category(class_name, overwrites=overwrites)
                print(f'\033[97mCreating a new class: {class_name}')
                await category.create_text_channel(f"text-chit-chat")
                await category.create_voice_channel(f"voice-chit-chat")

                await ctx.send(f"╰(*°▽°*)╯ Class {class_name} has been created.")
                print(f"\033[92mClass {class_name} has been created.")

    @commands.command(name='delete-class')
    @commands.has_role('admin')
    async def delete_class(self, ctx, class_name='default-class'):
        class_name = class_name.upper()
        guild = ctx.guild
        existing_category = discord.utils.get(guild.categories, name=class_name)
        if not existing_category:
            print(f"No such class: {class_name}")
            await ctx.send(f"＞﹏＜ No such class: {class_name}")
        else:
            print(f"deleting class{class_name}")
            delChannels = existing_category.channels
            for channel in delChannels:
                await channel.delete()
            await existing_category.delete()
            await discord.utils.get(guild.roles, name=class_name).delete()
            print(f"Done deleting of class {class_name}")
            await ctx.send(f"\(￣︶￣*\)) Done deleting of class {class_name}")

    @commands.command(name='delete-classes')
    @commands.has_role('admin')
    async def delete_classes(self, ctx, class_names='default-class'):
        guild = ctx.guild
        for class_name in class_names.split(","):
            class_name = class_name.upper().replace(" ", "")
            existing_category = discord.utils.get(guild.categories, name=class_name)
            if not existing_category:
                print(f"No such class: {class_name}")
                await ctx.send(f"＞﹏＜ No such class: {class_name}")
            else:
                print(f"deleting class {class_name}")
                delChannels = existing_category.channels
                for channel in delChannels:
                    await channel.delete()
                await existing_category.delete()
                await discord.utils.get(guild.roles, name=class_name).delete()
                print(f"Done deleting of class {class_name}")
                await ctx.send(f"\(￣︶￣*\)) Done deleting of class {class_name}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        print("\033[91mCOMMAND ERROR")
        await ctx.send('{{{(>_<)}}} You do not have the correct role for this command.')


bot.add_cog(MiscCog())
bot.add_cog(ClassCog())
bot.add_cog(AdminCog())
bot.run(TOKEN)
