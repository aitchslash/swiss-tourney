drop view if exists standings;
drop view if exists losses;
drop view if exists wins;
drop view if exists ties;

create view wins as select winner as id, count(*) as wins  
	from results where draw = false group by winner;

create view losses as select loser as id, count(*) as losses 
	from results where draw = false group by loser;

select 
	players.playerid as id, 
	players.name,
	coalesce(wins.wins, 0) as w, 
	-- coalesce(losses.losses, 0) as l,
	(coalesce(wins.wins, 0) + coalesce(losses.losses, 0)) as gp
from 
	players 
left join wins on players.playerid = wins.id
left join losses on players.playerid = losses.id
order by
	wins.wins;