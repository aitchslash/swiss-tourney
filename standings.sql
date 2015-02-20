--  might need to drop views on new matchReport
--  use cascade?  use if exists? 
--  combine into one line?  put this functionality elswhere (new MRep)?

drop view if exists standings;
drop view if exists losses;
drop view if exists wins;
drop view if exists ties;

/*
-- working, try to strip out ties below
create view wins as select winner as id, count(*) as wins 
	from results group by winner;
*/
create view wins as select winner as id, count(*) as wins  
	from results where draw = false group by winner;

create view losses as select loser as id, count(*) as losses 
	from results where draw = false group by loser;

create view ties as select * 
	from results where draw = true;


-- working thing [id/w/l/gp]

-- create view using line 1 called wins
-- create view using line 2 called losses
-- select wins.id, wins.count as wins, losses.count as losses, 
-- (wins.count + losses.count) as matches 
-- from wins join losses on wins.id = losses.id order by wins desc;

-- this works provided the views are created
-- ooops something went awry
/*
select wins.id, wins.count as wins, losses.count as losses, 
	(wins.count + losses.count) as matches 
	from wins join losses on wins.id = losses.id order by wins desc;
*/
-- try again, working
/*
select wins.id, wins, (wins +losses) as gp, losses
	from wins join losses on wins.id = losses.id order by wins desc;
*/

--turn it into a view
create view standings as select wins.id, wins, (wins +losses) as gp, losses
	from wins join losses on wins.id = losses.id order by wins desc;

-- now grab the name
-- working but need default wins = 0
/*
select players.playerID as ID, players.name, wins, gp as matches from standings
	right join players on standings.id = players.playerID order by wins desc;
*/
select players.playerID as ID, players.name, coalesce(wins, 0) as wins, coalesce(gp, 0) as matches 
	from standings right join players on 
	standings.id = players.playerID 
	order by wins desc;
