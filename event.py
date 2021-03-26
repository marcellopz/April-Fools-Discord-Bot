import time
import random
import asyncio
import math
import discord
import os
import json

global rates

async def event(team1, team2, channel):
    global rates
    rates = {
        team1.name.lower(): 2,
        team2.name.lower(): 2
    }
    rounds = random.choice([5, 6, 7, 8]) # number of rounds
    print(rounds)
    dice = 3 # d4 rolls
    team1_score = [0] # array of scores
    team2_score = [0]
    lead = [] # array of who was in the lead
    time_interval = 1 # minutes
    embed0 = discord.Embed(color=0x0394fc)
    embed0.add_field(name="Match starting!", value=f'Match between {team1.mention} and {team2.mention} is starting in {time_interval} minutes! \nUpdates also every {time_interval} minutes.\n\nGet your bets ready!', inline=False)
    embed0.add_field(name=f"{team1.name} rates:", value=2.0, inline=True)
    embed0.add_field(name=f"{team2.name} rates:", value=2.0, inline=True)
    await channel.send(embed=embed0)
    
    for i in range(rounds): # game
        await asyncio.sleep(60 * time_interval)
        if (i>0.4*rounds and abs(team1_score[i]-team2_score[i])>1 and random.choice([True, False, False])) or abs(team1_score[i]-team2_score[i])>2:
            print('comeback mechanic')
            if team1_score[i]>team2_score[i]:
                team2_score[i] += 1
            else:
                team1_score[i] += 1
        team1_score.append(team1_score[i] + random.randint(1, dice))
        team2_score.append(team2_score[i] + random.randint(1, dice))
        [winner, loser, msg] = message(team1, team2, team1_score[i+1], team2_score[i+1],team1_score[i], team2_score[i], i+1, rounds)
        if i+1 is not rounds:
            msg = get_state_message(winner, loser, lead, team1.name, team2.name, msg)
        lead.append(winner)
        
        embed1=discord.Embed(color=0xba60eb)
        embed1.add_field(name="Match update", value=msg, inline=False)
        await channel.send(embed=embed1)

        [team1_rates, team2_rates] = calculate_rates(dice, rounds - i - 1, team1_score[-1], team2_score[-1])
        rates = {
            team1.name.lower(): team1_rates,
            team2.name.lower(): team2_rates
        }
        print(rates)

        embed2=discord.Embed(color=0xfaf441)
        if team1_rates and team2_rates:
            embed2.add_field(name=f"{team1.name} rates:", value=team1_rates, inline=True)
            embed2.add_field(name=f"{team2.name} rates:", value=team2_rates, inline=True)
        else:
            embed2.add_field(name="Bets are closed!",value="‎ ‎  ‎ ‎ ‎ ‎")
        print(team1_score, team2_score)
        await channel.send(embed=embed2)

    # game end
    if winner == team1.name:
        return team1
    else:
        return team2


def message(team1, team2, t1, t2, previousT1, previousT2, n, max_round): # decide what message to send
    tie = True if t1==t2 and previousT1 == previousT2 else False
    if n<=0.3*max_round: # first 30% of the messages are about early game
        if n == 0:
            stage = random.choices(['early', 'firstblood'])
        else:
            stage = 'early'
    elif n<=0.8*max_round: # messages between 30 and 80% are about mid game
        stage = 'mid'
    elif n == max_round: # end game
        stage = 'game_ending'
    else: # last 20% about late game
        stage = 'late'
    print(stage)
    if stage == 'game_ending':
        if t1 == t2:
            winner = random.choice([team1, team2])
            loser = team1 if winner == team2 else team2
        elif t1>t2:
            winner = team1
            loser = team2
        else:
            winner = team2
            loser = team1
        return([winner.name, loser.name,
            get_template(stage).format(
                winning_team = "**" + winner.name + "**",
                losing_team = "**" + loser.name + "**",
                winning_user = "**" + random.choice(winner.members).name + "**",
                losing_user = "**" + random.choice(loser.members).name + "**"
                )
            ])   
    elif tie:
        teams = [team1, team2]
        random.shuffle(teams)
        return(['tie', 'tie', 
            get_template(stage + '_tie').format(
                teamone = "**" + teams[0].name + "**",
                teamtwo = "**" + teams[1].name + "**",
                teamone_member = "**" + random.choice(teams[0].members).name + "**",
                teamtwo_member = "**" + random.choice(teams[1].members).name + "**"
                )
            ])
    else:
        oldDiff = previousT1 - previousT2
        newDiff = t1 - t2
        if oldDiff - newDiff == 0:
            if t1>t2:
                event_winner = team1
                event_loser = team2
            else:
                event_winner = team2
                event_loser = team1
        elif oldDiff - newDiff > 0:
            event_winner = team2
            event_loser = team1
        elif oldDiff - newDiff < 0:
            event_winner = team1
            event_loser = team2
        #####################################################
        if t1>t2:
            winner = team1
            loser = team2
        else:
            winner = team2
            loser = team1
        #####################################################
        return([winner.name, loser.name,
            get_template(stage).format(
                winning_team = "**" + event_winner.name + "**",
                losing_team = "**" + event_loser.name + "**",
                winning_user = "**" + random.choice(event_winner.members).name + "**",
                losing_user = "**" + random.choice(event_loser.members).name + "**"
                )
            ])        


def get_state_message(winner, loser, lead, team1, team2, msg):
    if lead:
        if winner == 'tie':
            if lead[-1] == 'tie':
                msg += f'\n\nThe game is still even!'
            else:
                msg += f'\n\n**{team1 if lead[-1] == team2 else team2}** is back in the game!'
        elif winner == lead[-1]:
            msg += f'\n**{winner}** is still in the lead!'
        elif lead[-1] == 'tie':
            msg += f'\n**{winner}** takes the lead!'
        else:
            msg += f'\n**{winner}** manages to turn it around!'
    else:
        if winner == 'tie':
            msg += f'\nThe match starts off even!'
        else:
            msg += f'\n**{winner}** starts off with a lead!'
    return msg


def get_template(file_name): # getting phrase from file
    file = open('templates/'+file_name+'.txt','r')
    templates = file.readlines()
    file.close()
    return random.choice(templates)


def calculate_rates(dice, numberRemaining, team1_score, team2_score): 
    # simulates the rest of the game and sees how many times it won over how many games
    # rates are 1/(chance of winning), so when it's a 50% the rates are 2x, when there's 30% chance the rates are 3.3x
    if numberRemaining == 0:
        return [0, 0]
    times = 0
    team1_won = 0
    team2_won = 0
    while times<20000:
        team1 = [team1_score]
        team2 = [team2_score]
        for i in range(numberRemaining):
            team1.append(team1[i] + random.randint(1, dice))
            team2.append(team2[i] + random.randint(1, dice))
        times = times + 1
        if team1[-1]==team2[-1]:
            random.choice([team1,team2])[-1] += 1
        if team1[-1]>team2[-1]:
            team1_won += 1
        else:
            team2_won += 1
    try:
        team1_rates = times/team1_won
        team2_rates = times/team2_won
    except ZeroDivisionError:
        [team1_rates, team2_rates] = [0, 0]
    return [truncate(team1_rates, 2), truncate(team2_rates, 2)]

def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

def stimulusCheck():
    for filename in os.listdir('members/'):
        with open('members/' + filename, 'r') as read_file:
            member = json.load(read_file)
        if member['coins'] < 10:
            member['coins'] = 100
            with open('members/' + filename, 'w') as write_file:
                json.dump(member, write_file, indent=4)

def getAliases(role_name):
    role_split = role_name.split('(')
    slice_object = slice(0,-1)
    team_name = role_split[0][slice_object]
    team_acronym = role_split[1][slice_object]
    resp = {
        role_name: role_name,
        team_name: role_name,
        team_acronym: role_name
    }
    return resp