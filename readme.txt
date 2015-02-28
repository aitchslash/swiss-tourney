Files work sufficiently to pass the tests.

If usings ties or multiple tourneys please remember to pass: tiesEnabled=True and tourneyID=# into swissPairings()

---Bonus Content Notes---
Ties Implementation
True, or tiesEnabled=True, must be passed as an arg

Tourney Implementation
Defaults set for tourney 1 (where the test data will go)
Currently only supports two tourneys
Easy to add a third, fourth etc with ALTER TABLE
--- Could add tourney table for data integrity, but atm it seems superfluous and might break with the testing

Opponent Match Wins
function named: expandedStandings
Currently only works with both tiesEnabled=True and tourneyID=1


---- Wish List -----
-Get def Connect2 to work for all SQL queries.
-Add addTourney function
-Create testing suite with multi tourneys, random win generation, etc.
-Condense/refactor SQL queries (they seem unweildy)
-Unify connect and connect2