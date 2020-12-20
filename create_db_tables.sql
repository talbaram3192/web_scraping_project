create database web_scraping_project;

show databases;

use web_scraping_project;


select * from players;

select first_name from players where ranking_SGL != 0 order by ranking_SGL;

SET SQL_SAFE_UPDATES = 0;

-- delete from champions;
-- delete from teams;
-- delete from games_players;
-- delete from games;
-- delete from players;
-- delete from tournaments;
-- delete from last_meeting;



create table players(
player_id int auto_increment primary key,
first_name varchar(25),
last_name varchar(25),
ranking_DBL int,
ranking_SGL int,
career_high_DBL int,
career_high_SGL int,
turned_pro int,
weight float,
height float,
total_prize_money int,
country varchar(25),
birth date
);

create table teams(
team_id int auto_increment primary key,
name varchar(25)
);

create table tournaments(
tournament_id int auto_increment primary key,
year int,
type varchar(35),
name varchar(50),
location varchar(40),
date date,
SGL_draw int,
DBL_draw int,
surface varchar(20),
prize_money int
);

create table games(
game_ID int auto_increment primary key,
tournament_id int,
score varchar(30),
round varchar(25),
foreign key (tournament_id) references tournaments(tournament_id)
on delete cascade
);

create table last_meeting(
game_ID int,
round varchar(25),
tourn_name varchar(50),
venue varchar(50),
same_winner boolean,
foreign key (game_ID) references games(game_ID)
on delete cascade
);


create table games_players(
player_id int,
game_id int,
team_id int,
won boolean,
foreign key (player_id) references players(player_id) on delete cascade,
foreign key (team_id) references teams(team_id) on delete cascade,
foreign key (game_id) references games(game_id) on delete cascade
);


create table champions(
player_id int,
team_id int,
tournament_id int,
type varchar(10),
foreign key (player_id) references players(player_id) on delete cascade,
foreign key (team_id) references teams(team_id) on delete cascade,
foreign key (tournament_id) references tournaments(tournament_id) on delete cascade
);

-- alter table champions add team_id int;
-- alter table champions add foreign key (team_id) references teams (team_id);


show tables;

commit;



