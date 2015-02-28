#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament

import psycopg2

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    """ I'd love to eliminate this but I can't seem to wrap the
        user escaping into connect2"""
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

def countPlayers(tourneyID=1):
    """ Counts players for any given tourney id """
    statement = "SELECT COUNT(*) FROM players WHERE tourney%d=TRUE" % tourneyID
    return int(connect2(statement, True)[0][0])
    #return int(connect2("SELECT COUNT(*) FROM players", True)[0][0]) # nb, old line

def registerPlayer(name, tourneyID=1):
    """Adds a player to the tournament database."""
    """ Default is the test tourney, insert an arg for a diff tourney"""
    db = connect()
    c = db.cursor()
    statement = "INSERT INTO players (name, tourney%d)" % tourneyID 
    statement += "values (%s, True)"
    c.execute (statement, (name,))
    #c.execute("INSERT INTO players (name, tourney1) values (%s, True)", (name,)) # nb, old working line
    db.commit()
    db.close()

def registerExistingPlayer(playerID, tourneyID):
    """Adds already registered player to another tourney"""
    statement = "UPDATE players SET tourney%d=True where playerID=%d" % (tourneyID, playerID)
    connect2(statement)

def nameFromID(playerID):
    """ Returns full name from playerID """
    name = connect2('select name from players where playerID=%s' % (playerID), True)
    return name[0][0]

def playerStandingsOld(tiesEnabled=False, tourneyID=1):  #nb, nicer in some ways but not in use
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
    tiesStatement = '''
        drop view if exists losses cascade;
        drop view if exists wins cascade;
        drop view if exists tieSum cascade;
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
        where
            players.tourney%s = True
        order by
            pts desc;''' % (tourneyID, tourneyID, tourneyID, tourneyID)

    noTiesStatement = '''
        drop view if exists standings cascade;
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

def expandedStandings():
    """ returns standings but now point ties are sorted by strength of schedule """
    """ only for use with tourney1 and tiesEnabled, a work in progress """
    return connect2(open('expandedStandings.sql', "r").read(), True)

def reportMatch(winner, loser, draw=False, tourneyID=1):
    """Records the outcome of a single match between two players.
    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      draw: set to True for any tie.  Winner/Loser order no longer matters
    """
    db = connect()
    c = db.cursor()
    c.execute("INSERT INTO results (winner, loser, draw, tourneyID) values (%s, %s, %s, %s)", (winner, loser, draw, tourneyID))
    db.commit()
    db.close()
        
def swissPairings(tiesEnabled=False, tourneyID=1):
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
    
    if countPlayers(tourneyID=1) % 2 != 0:
        registerPlayer("BYE", tourneyID)
    if tiesEnabled = True AND tourneyID=1:
        standings = expandedStandings()
    else:    
        standings = playerStandings(tiesEnabled, tourneyID)
    # rip 'em apart and zip 'em back together again
    i, j = standings[::2], standings[1::2]
    pairings = zip(i,j)
    holder = []
    for pairing in pairings:
        holder.append((pairing[0][0], pairing [0][1], pairing[1][0], pairing [1][1]))
    return holder

# ----  ALL CODE AFTER THIS POINT EXPERIMENTAL USING RECURSION --- 
# ----  NOT USED FOR ASSIGNMENT
def swissPairingsRecursive(tiesEnabled=False, tourneyID=1):
    """Recursively generates and evaluates all possible pairings
    Works brilliantly for up to 8 players.  Blows up for 16.
    Adapting this to work for >= 16 players is a work in progress.

    Returns a list of pairs of players for the next round of a match.
  
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
    standings = playerStandings(tiesEnabled, tourneyID)
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
        bestPairTuples = getBestPairings(tiesEnabled,tourneyID)
        # need to get in correct format
        for pair in bestPairTuples:
            pairings.append((pair[0], nameFromID(pair[0]),
                            pair[1], nameFromID(pair[1])))
        return pairings

def makePointsDict(tiesEnabled=False, tourneyID=1): #nb, only used in recursive swiss
    """ Returns a dictionary key playerID, value points accrued in a tourney"""
    pts = {}
    standings = playerStandings(tiesEnabled,tourneyID)
    # check for ties enabled, if not
    if not tiesEnabled:
        for player in standings:
            pts[player[0]] = int(player[2]*2)
    # else, with ties enabled
    else:
        for player in standings:
            pts[player[0]] = int(player[5])
    return pts

def getBestPairings(tiesEnabled=False, tourneyID=1):  #nb, only used in recursive swiss
    """Evaluator for recursive swissPairings"""
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
        
def makePlayerList():  #nb, only used in recursive swiss
    """ Return prettified player list """
    playerTuples = connect2("SELECT playerID FROM players", True)
    playerList = []
    for item in playerTuples:
        playerList.append(item[0])
    return playerList

def genPairs(playerList):  # only used in recursive swiss
    """ Recursive pair generator """  
    #print "called genPairs" #nb
    if len(playerList) < 2: #   count call count players, nb
        yield playerList
        return
    first = playerList[0]
    for i in range(1, len(playerList)):  #   count call count players, nb
        pair = (first, playerList[i])
        for remainder in genPairs(playerList[1:i]+playerList[i+1:]):
            yield [pair] + remainder
