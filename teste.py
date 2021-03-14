import random
import time
import teste2

def chanceOfWinning(dice, numberRemaining, team1_score, team2_score):
    times = 0
    team1_won = 0
    team2_won = 0
    while times<10000:
        team1 = [team1_score]
        team2 = [team2_score]
        for i in range(numberRemaining):
            team1.append(team1[i] + random.randint(1, dice))
            team2.append(team2[i] + random.randint(1, dice))
        times = times + 1
        #print(x,y)
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
    return [team1_rates, team2_rates]
    
    #print(f'team1 odds: {100*team1_won/times}%\nteam2 odds: {100*team2_won/times}%\nteam1 rates: {1/(team1_won/times)}\nteam2 rates: {1/(team2_won/times)}')


print(teste2.variavel)