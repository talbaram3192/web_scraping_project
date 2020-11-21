create database web_scraping_project;

show databases;

use web_scraping_project;

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
type varchar(20),
name varchar(30),
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
);

create table games_players(
player_id int,
game_id int,
team_id int,
won boolean,
foreign key (player_id) references players(player_id),
foreign key (game_id) references games(game_id)
);

create table champions(
player_id int,
team_id int,
tournament_id int,
type varchar(10),
foreign key (player_id) references players(player_id),
foreign key (team_id) references teams(team_id),
foreign key (tournament_id) references tournaments(tournament_id)
);

show tables;

commit;



