#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

# ---- to do list ---- nb
#   bye implementation - if count is even addPlayer
#   tie implementation - DONE
#   tourney implementation - underway
#   remove tester.sql/withTies.sql from git
#   cursor.execute(open("schema.sql", "r").read())
#   newstr = "".join(oldstr.split('\n'))

import psycopg2

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

# set dataReturn to True if you want data returned
def connect2(statement, dataReturn=False):
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    c.execute(statement)
    if dataReturn:
        stuff = c.fetchall()
    else:
        db.commit()
    db.close()
    if dataReturn:
        return stuff 

def deleteMatches():
    connect2("DELETE FROM results")

def deletePlayers():
    connect2("DELETE FROM players")

def countPlayers():
    return int(connect2("SELECT COUNT(*) FROM players", True)[0][0])

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    c = db.cursor()
    c.execute("INSERT INTO players (name) values (%s)", (name,))
    db.commit()
    db.close()

def nameFromID(playerID):
    name = connect2('select name from players where playerID=%s' % (playerID), True)
    return name[0][0]

def playerStandingsOld(tiesEnabled=False, tourneyID=1):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played

      With tiesEnabled=True tuples in list contain (id, name, wins, matches, ties, points)
      sorted by points
    """
    if tiesEnabled: 
        return connect2(open('withTies.sql', "r").read(), True)
    else: 
        return connect2(open('tester.sql', "r").read(), True)

def playerStandings(tiesEnabled=False, tourneyID=1):
    tiesStatement = '''
drop view if exists losses;
drop view if exists wins;
drop view if exists tieSum;
drop view if exists ties;

create view wins as select winner as id, count(*) as wins  
    from results where draw = false AND tourneyID=%s  group by winner;

create view losses as select loser as id, count(*) as losses 
    from results where draw = false AND tourneyID=%s group by loser;

create view ties as select winner as id from results
    where draw = True
    union all
    select loser from results
    where draw = True
    AND tourneyID=%s;

create view tieSum as select id, count(*) as ties
    from ties group by id;

select players.playerid as id, 
    players.name,
    coalesce(wins.wins, 0) as w, 
    (coalesce(wins.wins, 0) + coalesce(losses.losses, 0)) +
    coalesce(tieSum.ties, 0) as gp,
    coalesce(tieSum.ties, 0) as t,
    (coalesce(wins.wins, 0) * 2 + coalesce(tieSum.ties, 0)) as pts
from players 
    left join wins on players.playerid = wins.id
    left join losses on players.playerid = losses.id
    left join tieSum on players.playerid = tieSum.id
order by
    pts desc;''' % (tourneyID, tourneyID, tourneyID)

    noTiesStatement = '''
    drop view if exists standings;
drop view if exists ties cascade;
drop view if exists losses cascade;
drop view if exists wins;

create view wins as select winner as id, count(*) as wins  
    from results where draw = false AND tourneyID=%s group by winner;

create view losses as select loser as id, count(*) as losses 
    from results where draw = false AND tourneyID=%s group by loser;

select 
    players.playerid as id, 
    players.name,
    coalesce(wins.wins, 0) as w, 
    (coalesce(wins.wins, 0) + coalesce(losses.losses, 0)) as gp
from 
    players 
left join wins on players.playerid = wins.id
left join losses on players.playerid = losses.id
order by
    wins.wins;''' % (tourneyID, tourneyID)
    
    if tiesEnabled: 
        return connect2(tiesStatement, True)
    else: 
        return connect2(noTiesStatement, True)

def reportMatch(winner, loser, draw=False, tourneyID=1):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    
    if winner != loser:
        db = connect()
        c = db.cursor()
        c.execute("INSERT INTO results (winner, loser, draw, tourneyID) values (%s, %s, %s, %s)", (winner, loser, draw, tourneyID))
        db.commit()
        db.close()
    else:
        print "Two players are needed for a match"
    
def swissPairings(tiesEnabled=False):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings(tiesEnabled)
    # get round number, assume everyone has played 
    #   equal number of games before swissPairings can be called
    roundNumber = standings[0][3] + 1
    numMatches = countPlayers() / 2
    # generate trivial solution from standings
    #   with no dupes it's maximized 
    pairings = []
    # duplicate matchups impossible for rounds <= 2
    if roundNumber <= 2:
        for i in range(0, numMatches):
            pairings.append((standings[i*2][0], standings[i*2][1], 
                standings[i*2+1][0], standings[i*2+1][1]))
        return pairings
    # for later rounds need to check for duplicates
    else:
        bestPairTuples = getBestPairings(tiesEnabled)
        # need to get in correct format
        for pair in bestPairTuples:
            pairings.append((pair[0], nameFromID(pair[0]),
                            pair[1], nameFromID(pair[1])))
        return pairings

def swissPairings2(tiesEnabled=False, tourneyID=1):
    standings = playerStandings(tiesEnabled, tourneyID)
    # rip 'em apart and zip 'em back together again
    pass 

def makePointsDict(tiesEnabled=False):
    pts = {}
    standings = playerStandings(tiesEnabled)
    # check for ties enabled, if not
    if not tiesEnabled:
        for player in standings:
            pts[player[0]] = int(player[2]*2)
    # else, with ties enabled
    else:
        for player in standings:
            pts[player[0]] = int(player[5])
    return pts

def getBestPairings(tiesEnabled=False):
    # iniialize holder
    bestHolder = []
    results = connect2('select winner, loser from results', True)
    standings = playerStandings() # may be redundant, test removal, nb
    playerList = makePlayerList()
    ptsDict = makePointsDict()
    # create disallowed list
    disallowed = []
    for matchup in results:
        disallowed.append(matchup)
        disallowed.append((matchup[1], matchup[0]))
    for pairSet in genPairs(playerList):
        #print "back in getBestPairings" # nb
        ptDifference = 0
        for pair in pairSet:
            reverse = (pair[1], pair[0]) 
            if (pair in disallowed or reverse in disallowed):
                ptDifference += 10 # crude, should refactor
            ptDifference +=  abs(ptsDict[pair[0]] - ptsDict[pair[1]])
        if ptDifference == 0: return pairSet #, would be a good shortcut, nb
        bestHolder.append([ptDifference, pairSet])
    bestHolder.sort(key=lambda x: x[0])
    return bestHolder[0][1] #first/best one, set index
        

def makePlayerList():
    # get player list and do a bit of formatting
    playerTuples = connect2("SELECT playerID FROM players", True)
    playerList = []
    for item in playerTuples:
        playerList.append(item[0])
    return playerList

#   count call count players, nb
def genPairs(playerList):
    #print "called genPairs" #nb
    if len(playerList) < 2:
        yield playerList
        return
    first = playerList[0]
    for i in range(1, len(playerList)):
        pair = (first, playerList[i])
        for remainder in genPairs(playerList[1:i]+playerList[i+1:]):
            yield [pair] + remainder
