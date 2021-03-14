import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import event
import json
from operator import itemgetter

intents = discord.Intents.default()
intents.members = True

load_dotenv()
BOT_KEY = os.getenv("BOT_KEY")
logging.basicConfig()
logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
client = commands.Bot(command_prefix = '.', intents = intents)

event_role_id = 820349883504525362
currently_playing = []
bets = []

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author.bot:
        return
    await client.process_commands(message)


@client.command()
async def hi(ctx):
    print(discord.__version__)
    await ctx.channel.send('hi')


@client.command()
async def bet(ctx, *, args: str):
    if not os.path.isfile('members/' + str(ctx.author.id) + '.json'):
        await ctx.send("You haven't joined the event yet")
    else:
        value = args.split(' ')[-1]
        team_name = args[slice(-1*len(value) - 1)].lower()
        try:
            value = int(value)
            if team_name not in currently_playing:
                raise
            with open('members/' + str(ctx.author.id) + '.json', 'r') as read_file:
                member = json.load(read_file)
            if member['coins'] >= value:
                newMember = {
                    "name": ctx.author.name,
                    "id": ctx.author.id,
                    "coins": member['coins'] - value
                }
                with open('members/' + str(ctx.author.id) + '.json', 'w') as write_file:
                    json.dump(newMember, write_file, indent=4)
                bet = {
                    "name": ctx.author.name,
                    "id": ctx.author.id,
                    "value": value,
                    "team": team_name,
                    "rate": event.rates[team_name]
                }
                bets.append(bet)
                await ctx.message.add_reaction('✅')
            else:
                await ctx.send("You don't have enough coins, to check how many you have use `.balance`")
        except:
            await ctx.send('Invalid format')


@client.command()
async def current_bets(ctx):
    global bets
    if bets:
        answer = 'The current bets are:\n'
        for bet in bets:
            answer = answer + '- **{}** is betting **{}** on **{}** with a rate of **{}**\n'.format(bet['name'], bet['value'], bet['team'], bet['rate'])
        await ctx.send(answer)

@client.command()
async def leaderboard(ctx):
    member_list = []
    for filename in os.listdir('members/'):
        with open('members/' + filename, 'r') as read_file:
            member = json.load(read_file)
        member_list.append(member)
    sorted_list = sorted(member_list, key=itemgetter('coins'), reverse=True)
    resp = "The Leaderboard is:\n\n"
    for member in enumerate(sorted_list):
        resp += "**{}**. {} - {}\n".format(member[0]+1, member[1]['name'], member[1]['coins'])
    await ctx.send(resp)


@client.command()
async def join(ctx):
    if os.path.isfile('members/' + str(ctx.author.id) + '.json'):
        await ctx.send("You're already joined the event")
    else:
        await ctx.author.add_roles(ctx.guild.get_role(event_role_id))
        newMember = {
            "name": ctx.author.name,
            "id": ctx.author.id,
            "coins": 1000
        }
        with open('members/' + str(ctx.author.id) + '.json', 'x') as write_file:
            json.dump(newMember, write_file, indent=4)
        await ctx.message.add_reaction('✅')


@client.command()
async def balance(ctx):
    if os.path.isfile('members/' + str(ctx.author.id) + '.json'):
        with open('members/' + str(ctx.author.id) + '.json', 'r') as read_file:
            member = json.load(read_file)
            await ctx.send('{} has **{}** coins'.format(ctx.author.mention, member['coins']))
    else:
        await ctx.send("You haven't joined the event yet, to join type `.join`")

        
@client.command()
async def match(ctx, role1: discord.Role, role2: discord.Role):
    global currently_playing
    currently_playing = [role1.name.lower(), role2.name.lower()]
    winner = await event.event(role1, role2, ctx)
    if bets:
        for bet in bets:
            if bet['team'] == winner.name:
                print(bet)
                with open('members/' + str(bet['id']) + '.json', 'r') as read_file:
                    member = json.load(read_file)
                member['coins'] = member['coins'] + bet['value']*bet['rate']
                with open('members/' + str(bet['id']) + '.json', 'w') as write_file:
                    json.dump(member, write_file, indent=4)
    currently_playing = []

client.run(BOT_KEY)