--- Designed to run on a VM using POSTGREsql ---
--- with psycopg2 module installed ---

--- Files ---
readme.txt - this file
tournament.sql - creates the database
tournament.py - the python code
expandedStandings.sql - a long query, w/ multiple vies

Works sufficiently to pass the tests supplied.

--- General Notes ---
If using ties or multiple tourneys please remember to pass: tiesEnabled=True and tourneyID=# into swissPairings()

I'd prefer to implement a recursive generator to create and then evaluate all potential matches.  Currently, this works nicely for eight players but blows up with sixteen.  As such I've moved all related code to the bottom of the file and disabled it for the test.  Hopes are to get it going at some point.

---Bonus Content Notes---
#Ties Implementation
True, or tiesEnabled=True, must be passed as an arg

#Tourney Implementation
Defaults set for tourney 1 (where the test data will go)
Currently only supports two tourneys
Easy to add a third, fourth etc with ALTER TABLE
--- Could add tourney table for data integrity, but atm it seems superfluous and might break with the testing

#Opponent Match Wins
function named: expandedStandings
Currently only works with both tiesEnabled=True and tourneyID=1

#BYE Implementation
Simply adds a player when playerCount is odd
-could report match proactively, but won't unless I implement testing with random results
-no real worry about repeat matches with existing players

---- Wish List -----
--Unify connect and connect2 to work for all SQL queries.
-Add addTourney function
-Create testing suite with multi tourneys, random win generation, etc.
-Condense/refactor SQL queries (they seem unweildy)
