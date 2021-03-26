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
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
client = commands.Bot(command_prefix = '.', intents = intents)

mod_team = [173620782092517376, 164002296278024192, 243083529871818752, 322917297763123202, 239572326822182912]
dev_chat = 766867758302101504
match_channel = 727673871133835275 #824692473674727496
command_channel = 824691712077201428
botroom = 316142433828208643
emoji_id = 824839887722643507
event_role_id = 824698167874027520

currently_playing = []
bets = []
allowed_channels = [botroom, command_channel, dev_chat]
capitalize = {}

client.remove_command('help')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author.bot:
        return
    await client.process_commands(message)

@client.event
async def on_raw_reaction_add(payload):
    if payload.emoji.id == emoji_id:
        await payload.member.add_roles((await client.fetch_guild(payload.guild_id)).get_role(event_role_id))
        if os.path.isfile('members/' + str(payload.user_id) + '.json'):
            return
        else:
            newMember = {
                "name": payload.member.name,
                "id": payload.user_id,
                "coins": 1000
            }
            with open('members/' + str(payload.user_id) + '.json', 'x') as write_file:
                json.dump(newMember, write_file, indent=4)


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
            if value != 'all':
                value = int(value)
                if value<1:
                    raise
            global aliases
            global bets
            if bets:
                count = 0
                for bet in bets:
                    print(bet)
                    if bet['id'] == ctx.author.id:
                        count += 1
                print(count)
                if count >= 10:
                    await ctx.send("You've reached the bet limit for this match")
                    return
            team_name = aliases[team_name]
            if team_name not in currently_playing:
                raise
            with open('members/' + str(ctx.author.id) + '.json', 'r') as read_file:
                member = json.load(read_file)
            if member['coins'] == 0:
                await ctx.send("You don't have any Gold")
                return
            if value == 'all' or member['coins'] >= value:
                newCoins = 0 if value == "all" else member['coins'] - value
                betValue = member['coins'] if value == "all" else value
                newMember = {
                    "name": ctx.author.name,
                    "id": ctx.author.id,
                    "coins": newCoins
                }
                with open('members/' + str(ctx.author.id) + '.json', 'w') as write_file:
                    json.dump(newMember, write_file, indent=4)
                bet = {
                    "name": ctx.author.name,
                    "id": ctx.author.id,
                    "value": betValue,
                    "team": team_name,
                    "rate": event.rates[team_name]
                }
                bets.append(bet)
                await ctx.message.add_reaction('✅')
            else:
                await ctx.send("You don't have enough Gold, to check how many you have use `.balance`")
        except:
            await ctx.send('Invalid format')


# @client.command()
# async def current_bets(ctx):
#     global bets
#     if bets:
#         answer = 'The current bets are:\n'
#         for bet in bets:
#             answer = answer + '- **{}** is betting **{}** on **{}** with a rate of **{}**\n'.format(bet['name'], bet['value'], capitalize[bet['team']], bet['rate'])
#         await ctx.send(answer)
#     else:
#         await ctx.send("No bets are placed currently")

@client.command()
async def mybets(ctx):
    global bets
    if bets:
        answer = 'Your bet(s) are:\n'
        for bet in bets:
            if bet['id']==ctx.author.id:
                answer = answer + "**{}** on **{}** with a rate of **{}**\n".format(bet['value'], capitalize[bet['team']], bet['rate'])
        await ctx.send(answer)
    else:
        await ctx.send("You have no bets placed currently")

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
        if member[0] == 9:
            break
    await ctx.send(resp)


@client.command()
async def join(ctx):
    if ctx.channel.id not in allowed_channels:
        return
    if os.path.isfile('members/' + str(ctx.author.id) + '.json'):
        await ctx.send("You've already joined the event")
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
            await ctx.send('{} has **{}** Gold'.format(ctx.author.mention, member['coins']))
    else:
        await ctx.send("You haven't joined the event yet, to join type `.join`")

        
@client.command()
async def match(ctx, role1: discord.Role, role2: discord.Role):
    channel = client.get_channel(match_channel)
    if ctx.author.id not in mod_team:
        return
    global currently_playing
    global bets
    global aliases
    global capitalize
    currently_playing = [role1.name.lower(), role2.name.lower()]
    capitalize = {
        role1.name.lower(): role1.name,
        role2.name.lower(): role2.name
    }
    aliases = dict(event.getAliases(role1.name.lower()), **event.getAliases(role2.name.lower()))
    winner = await event.Event(role1, role2, channel)
    embed = discord.Embed(color=0x00fff7)
    embed.add_field(name=f"🎉🎉 **{winner.name}** wins! 🎉🎉", value=f'🏆🏆{winner.mention}🏆🏆')
    await channel.send(embed = embed)
    if bets:
        for bet in bets:
            if bet['team'] == winner.name.lower():
                logging.debug(bet)
                print(bet)
                with open('members/' + str(bet['id']) + '.json', 'r') as read_file:
                    member = json.load(read_file)
                member['coins'] = member['coins'] + bet['value']*bet['rate']
                with open('members/' + str(bet['id']) + '.json', 'w') as write_file:
                    json.dump(member, write_file, indent=4)
    currently_playing = []
    bets = []
    event.stimulusCheck()
    

@client.command()
async def reset_coins(ctx):
    if ctx.author.id not in mod_team:
        return
    for filename in os.listdir('members/'):
        with open('members/' + filename, 'r') as read_file:
            member = json.load(read_file)
        member['coins'] = 1000
        with open('members/' + filename, 'w') as write_file:
            json.dump(member, write_file, indent=4)
    await ctx.message.add_reaction('✅')
    

@client.command()
async def list_teams(ctx, *, args):
    if ctx.author.id not in mod_team:
        return
    roles = ctx.message.role_mentions
    embed = discord.Embed(color=0xffc400)
    for role in roles:
        member_list = '```'
        for member in role.members:
            member_list += '- '+ member.name + '\n'
        member_list += '```'
        embed.add_field(name=role.name, value=member_list, inline=True)
    await ctx.send(embed=embed)



client.run(BOT_KEY)