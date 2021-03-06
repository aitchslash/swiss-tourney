drop view if exists standings cascade;
drop view if exists sos;
drop view if exists losses;
drop view if exists wins;
drop view if exists tieSum;
drop view if exists ties;
drop view if exists extra;
drop view if exists exts;  



create view wins as select winner as id, count(*) as wins  
	from results where draw = false group by winner;

create view losses as select loser as id, count(*) as losses 
	from results where draw = false group by loser;

create view ties as select winner as id from results
	where draw = True
	union all
	select loser from results
	where draw = True;

create view tieSum as select id, count(*) as ties
	from ties group by id;



create view standings as select 
	players.playerid as id, 
	players.name,
	coalesce(wins.wins, 0) as w, 
	-- coalesce(losses.losses, 0) as l,
	(coalesce(wins.wins, 0) + coalesce(losses.losses, 0)) +
	coalesce(tieSum.ties, 0) as gp,
	coalesce(tieSum.ties, 0) as t,
	(coalesce(wins.wins, 0) * 2 + coalesce(tieSum.ties, 0)) as pts
	
	
from 
	players 
left join wins on players.playerid = wins.id
left join losses on players.playerid = losses.id
left join tieSum on players.playerid = tieSum.id
order by
	pts desc;
	
create view extra as
	select winner, loser from results
	union 
	select loser, winner from results;

create view exts as
	select extra.winner, extra.loser, standings.pts 
	from extra 
	join standings
		on standings.id = extra.loser;

create view sos as
	select winner as id, sum(pts) as sos from exts group by winner;

select standings.id, name, w, gp, t, pts, sos from standings join sos on sos.id = standings.id
	order by pts desc, sos desc;

