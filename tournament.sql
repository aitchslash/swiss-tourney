-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE DATABASE tournament;

\c tournament;

CREATE TABLE players(
	playerID serial PRIMARY KEY,
	name text NOT NULL
);

-- TourneyID will need a refernce when/if that's created
-- default values should be put in the python args
-- Primary key combo: is it order sensitive?
-- added tourneyID to Primary Key; matchups can reoccur 
--		in a different tourney (not tested)
CREATE TABLE results(
	winner INT REFERENCES players(playerID),
	loser INT REFERENCES players(playerID),
	draw BOOLEAN,
	tourneyID INT,
	PRIMARY KEY (winner, loser, tourneyID)
)