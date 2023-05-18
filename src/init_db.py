import sqlite3
import pandas as pd
# initializes database definitions and primary key to avoid inserting duplicates into dataset
# you can also use this file to just test stuff, get visualizations from the db. like a query GUI (without the G).

def run_init_db():
    # Connect to the database
    conn = sqlite3.connect('example.db')

    #conn.execute(f'DROP TABLE PLAYER_TABLE') 
    definition = 'summonerId REAL PRIMARY KEY, summonerName REAL, leaguePoints REAL, rank REAL, wins REAL, losses REAL, veteran REAL, inactive REAL, freshBlood REAL, hotStreak REAL, tier REAL, request_region REAL, queue REAL'   
    conn.execute(f'CREATE TABLE IF NOT EXISTS player_table ({definition})')

    #conn.execute(f'DROP TABLE match_table') 
    definition = 'match_id REAL PRIMARY KEY'   
    conn.execute(f'CREATE TABLE IF NOT EXISTS match_table ({definition})')    

    # Create the definition in sql for performance_table, taking all the keys from final_object
    definition = 'assists REAL, baronKills REAL, bountyLevel REAL, champExperience REAL, champLevel REAL, championId REAL, championName REAL, championTransform REAL, consumablesPurchased REAL, damageDealtToBuildings REAL, damageDealtToObjectives REAL, damageDealtToTurrets REAL, damageSelfMitigated REAL, deaths REAL, detectorWardsPlaced REAL, doubleKills REAL, dragonKills REAL, firstBloodAssist REAL, firstBloodKill REAL, firstTowerAssist REAL, firstTowerKill REAL, gameEndedInEarlySurrender REAL, gameEndedInSurrender REAL, goldEarned REAL, goldSpent REAL, individualPosition REAL, inhibitorKills REAL, inhibitorTakedowns REAL, inhibitorsLost REAL, item0 REAL, item1 REAL, item2 REAL, item3 REAL, item4 REAL, item5 REAL, item6 REAL, itemsPurchased REAL, killingSprees REAL, kills REAL, lane REAL, largestCriticalStrike REAL, largestKillingSpree REAL, largestMultiKill REAL, longestTimeSpentLiving REAL, magicDamageDealt REAL, magicDamageDealtToChampions REAL, magicDamageTaken REAL, neutralMinionsKilled REAL, nexusKills REAL, nexusLost REAL, nexusTakedowns REAL, objectivesStolen REAL, objectivesStolenAssists REAL, participantId REAL, pentaKills REAL, physicalDamageDealt REAL, physicalDamageDealtToChampions REAL, physicalDamageTaken REAL, profileIcon REAL, puuid REAL, quadraKills REAL, riotIdName REAL, riotIdTagline REAL, role REAL, sightWardsBoughtInGame REAL, spell1Casts REAL, spell2Casts REAL, spell3Casts REAL, spell4Casts REAL, summoner1Casts REAL, summoner1Id REAL, summoner2Casts REAL, summoner2Id REAL, summonerId REAL, summonerLevel REAL, summonerName REAL, teamEarlySurrendered REAL, teamId REAL, teamPosition REAL, timeCCingOthers REAL, timePlayed REAL, totalDamageDealt REAL, totalDamageDealtToChampions REAL, totalDamageShieldedOnTeammates REAL, totalDamageTaken REAL, totalHeal REAL, totalHealsOnTeammates REAL, totalMinionsKilled REAL, totalTimeCCDealt REAL, totalTimeSpentDead REAL, totalUnitsHealed REAL, tripleKills REAL, trueDamageDealt REAL, trueDamageDealtToChampions REAL, trueDamageTaken REAL, turretKills REAL, turretTakedowns REAL, turretsLost REAL, unrealKills REAL, visionScore REAL, visionWardsBoughtInGame REAL, wardsKilled REAL, wardsPlaced REAL, win REAL, match_identifier REAL, duration REAL, f1 REAL, f2 REAL, f3 REAL, f4 REAL, f5 REAL, calculated_player_performance REAL'
    conn.execute(f'CREATE TABLE IF NOT EXISTS performance_table ({definition})')

    conn.commit()
    conn.close()



if __name__ == '__main__':
    run_init_db()