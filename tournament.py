#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

# ---- to do list ----
#   bye implementation - if count is even addPlayer
#   cursor.execute(open("schema.sql", "r").read())
#   newstr = "".join(oldstr.split('\n'))

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

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

def registerPlayer2(name):
    subString = "INSERT INTO players (name) values (%s)", (name,)
    statement = subString[0] + ", " + str(subString[1])
    connect2(statement)

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


def playerStandings(tourneyID=1):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    # uses 3 views
    return connect2(open('tester.sql', "r").read(), True)

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
    
def swissPairings2():
    standings = playerStandings()
    
    # get prior match-ups from results
    results = connect2('select winner, loser from results', True)
    
    # get round number, assume everyone has played 
    #   equal number of games before swissPairings can be called
    roundNumber = standings[0][3] + 1
    numMatches = countPlayers() / 2
    # generate trivial solution from standings
    #   with no dupes it's maximized 
    pairings = []
    for i in range(0, numMatches):
        pairings.append((standings[i*2][0], standings[i*2][1], 
            standings[i*2+1][0], standings[i*2+1][1]))
    # duplicate matchups impossible for rounds <= 2
    if roundNumber <= 2:
        return pairings
    # for later rounds need to check for duplicates
    
    # create disallowed list
    disallowed = []
    for matchup in results:
        disallowed.append(matchup)
        disallowed.append((matchup[1], matchup[0]))

    # loop through pairings checking for duplicates
    dupes = False
    for pairing in pairings:
        if (pairing[0], pairing[2]) in disallowed:
            dupes = True
    if dupes == False:
        return pairings
    else:
        print "DUPES!!!!"
        # get player list (w/ points?)
        # make pairs (if pts, could evaluate here?)
        # evaluate 
    return pairings

def generatePairs(players):
    a = players[0]
    holder = []
    for i in range(1,len(players)): # could call count players
        pairOne = (a, players[0])
        holder = [pairOne]
        for remainder in generatePairs(players[1:i]+players[i+1:]):
            holder.append(remainder)


# just for testing ATM, might not need
def checkDupes(pairings):
    results = connect2('select winner, loser from results', True)
    disallowed = []
    for matchup in results:
        disallowed.append(matchup)
        disallowed.append((matchup[1], matchup[0]))

    print disallowed # test print

    # loop through pairings checking for duplicates
    dupes = False
    for pairing in pairings:
        print pairing[0], pairing[2] #test print
        if (pairing[0], pairing[2]) in disallowed:
            dupes = True
    if dupes == False:
        return pairings
    else:
        print "DUPES"
 
def swissPairings():
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
    # check if even number - only for extra credit - do later
    # countPlayers()
    # if odd
    # registerPlayer "bye" # this would/shoud only happen in the first round
    #   might want to update standings....
    #
    # design pairings
    # no problem at top or bottom - all wins and all losses will never
    #   have played one another
    # ooh, prepare for ties - 3 pts/w, 1pt/t maybe
    #   and perhaps enhanced rankings too
    #
    # grab count
    # derive total rounds from count
    # grab wins from standings
    # rounds completed is top player's win count
    # round 1 is win count = 0, etc
    # sort players by id - maybe not necessary
    # grab playerID's if not done yet
    
    # if rounds = 1 or 0, no worries
    # no worries where wins = 0 or wins = rounds completed
    # fire those off
    # if none remain done
    # deal with the rest

    # or brute force
    standings = playerStandings()
    # get prior match-up from results
    results = connect2('select winner, loser from results', True)
    
    numMatches = countPlayers() / 2
    pairings = []
    for i in range(0, numMatches):
        pairings.append((standings[i*2][0], standings[i*2][1], 
            standings[i*2+1][0], standings[i*2+1][1]))
    return pairings
    

