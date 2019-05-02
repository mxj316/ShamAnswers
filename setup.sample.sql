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
    completed boolean not null default 0,
    user_id int not null,
    foreign key (user_id) references user(id) on delete cascade
);
create table letter(
    id int not null auto_increment primary key,
    alphabet_letter char(1) not null,
    time_stamp timestamp not null default current_timestamp,
    votes int not null default 0,
    user_id int not null,
    question_id int not null,
    sub_letter_id int,
    foreign key (user_id) references user(id),
    foreign key (question_id) references question(id),
    foreign key (sub_letter_id) references letter(id)
);
-- relations
create table submit(
    user_id int not null,
    question_id int not null,
    time_stamp timestamp not null default current_timestamp,
    foreign key (user_id) references user(id),
    foreign key (question_id) references question(id)
);
create table vote(
    user_id int not null,
    letter_id int not null,
    foreign key (user_id) references user(id),
    foreign key (letter_id) references letter(id)
);

-- insert data into database (temporary data for testing if needed)
insert into user(username, email, password) values('Coolsnail123', 'raj@case.edu', 'Skyrim');
insert into user(username, email, password) values('SgtPepper', 'pepperkep@case.edu', 'Inside');
insert into user(username, email, password) values('Meshy00', 'organizer@case.edu', 'DivinityTho');
insert into user(username, email, password) values('Andre3000', 'micycle@case.edu', 'Motorcycle');
insert into user(username, email, password) values('JosephJoeStarII', 'noobmaster69@case.edu', 'MemeLord');

insert into question(content, category, user_id) values('Are Javadoc comments the coolest thing ever?', 'Advice', 1);
insert into question(content, category, user_id) values('Is Hot Pie the key to everything?', 'Humor', 4);

insert into letter(alphabet_letter, user_id, question_id, sub_letter_id) values('Y', 2, 2, null);
insert into letter(alphabet_letter, user_id, question_id, sub_letter_id) values('E', 2, 2, 1);
insert into letter(alphabet_letter, user_id, question_id, sub_letter_id) values('T', 2, 2, 1);
insert into letter(alphabet_letter, user_id, question_id, sub_letter_id) values('E', 4, 1, 2);
insert into letter(alphabet_letter, user_id, question_id, sub_letter_id) values('O', 1, 2, 3);
insert into letter(alphabet_letter, user_id, question_id, sub_letter_id) values('K', 2, 2, 4);
