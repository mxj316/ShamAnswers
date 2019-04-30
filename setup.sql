--
-- setup database file for ShamAnswers
--

-- create database and user, grant privileges to user
create database sham_answers_database;
create user 'username'@'localhost' identified by 'password';
grant all on sham_answers_database.* to 'username'@'localhost';
flush privileges;

-- select the database and create tables
use sham_answers_database;
-- entities
create table user(
    id int not null auto_increment primary key,
    username varchar(255) not null,
    email varchar(255) not null,
    password varchar(255) not null
);
create table question(
    id int not null auto_increment primary key,
    content varchar(255) not null,
    category varchar(255) not null,
    time_stamp timestamp not null default current_timestamp,
    user_id int not null,
    foreign key (user_id) references user(id)
);
create table letter(
    id int not null auto_increment primary key,
    alphabet_letter char(1) not null,
    user_id int not null,
    question_id int not null,
    foreign key (user_id) references user(id),
    foreign key (question_id) references question(id)
);
-- relations
create table add_letter(
    user_id int not null,
    letter_id int not null,
    time_stamp varchar(255) not null,
    foreign key (user_id) references user(id),
    foreign key (letter_id) references letter(id)
);
create table submit(
    user_id int not null,
    question_id int not null,
    time_stamp varchar(255) not null,
    foreign key (user_id) references user(id),
    foreign key (question_id) references question(id)
);
create table sub_letter(
    letter_id int not null,
    foreign key (letter_id) references letter(id)
);
