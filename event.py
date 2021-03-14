import time
import random
import asyncio
import math

global rates

async def event(team1, team2, ctx):
    global rates
    rates = {
        team1.name: 2,
        team2.name: 2
    }
    rounds = 7 # number of rounds
    dice = 3 # d4 rolls
    team1_score = [0] # array of scores
    team2_score = [0]
    lead = [] # array of who was in the lead
    time_interval = 0.2 # minutes
    await ctx.send(f'Match between {team1.mention} and {team2.mention} is starting in {time_interval} minutes! Updates also every {time_interval} minutes.\nGet your bets ready!')
    
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
        [winner, loser, msg] = message(team1, team2, team1_score[i+1], team2_score[i+1], i+1, rounds)
        if i is not rounds:
            if lead:
                if winner == 'tie':
                    if lead[-1] == 'tie':
                        msg += f'\n\nThe game is still even!'
                    else:
                        msg += f'\n\n**{team1.name if lead[-1] == team2.name else team2.name}** is back in the game!'
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
        lead.append(winner)
        await ctx.send('‎ ‎  ‎ ‎ ‎ ‎\n\n➡️ ' + msg)
        
        [team1_rates, team2_rates] = calculate_rates(dice, rounds - i - 1, team1_score[-1], team2_score[-1])
        
        rates = {
            team1.name: team1_rates,
            team2.name: team2_rates
        }
        print(rates)
        if team1_rates and team2_rates:
            await ctx.send(f'Place your bets! The rates are:\n**{team1.name}**: {round(team1_rates,2)}\n**{team2.name}**: {round(team2_rates,2)}')
        else:
            await ctx.send('Bets are closed!')
        print(team1_score, team2_score)
        

    # game end
    if team1_score[-1] == team2_score[-1]:
        winner = random.choice([team1, team2])
        await ctx.send(f'Very close game, but in the end {winner} takes the victory!')
    elif team1_score[-1]>team2_score[-1]:
        await ctx.send(f'**{team1}** wins!')
        return team1
    elif team2_score[-1]>team1_score[-1]:
        await ctx.send(f'**{team2}** wins!')
        return team2
    




def message(team1, team2, t1, t2, n, max_round): # decide what message to send
    tie = True if t1==t2 else False
    if n<=0.3*max_round: # first 30% of the messages are about early game
        if n == 0:
            stage = random.choices(['early', 'firstblood'])
        else:
            stage = 'early'
    elif n<=0.8*max_round: # messages between 30 and 80% are about mid game
        stage = 'mid'
    else: # last 20% about late game
        stage = 'late'
    
    if tie:
        teams = [team1, team2]
        random.shuffle(teams)
        return(['tie', 'tie', get_template(stage + '_tie').format(teamone = teams[0], teamtwo = teams[1])])
    else:
        if t1>t2:
            winner = team1
            loser = team2
        else:
            winner = team2
            loser = team1
        
        return([winner.name, loser.name,
            get_template(stage).format(
                winning_team = winner.name,
                losing_team = loser.name,
                winning_user = random.choice(winner.members).name,
                losing_user = random.choice(loser.members).name
                )
            ])

        
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

#message(6,5,0)