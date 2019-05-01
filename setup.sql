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
    password varchar(255) not null,
    admin boolean not null
);
create table question(
    id int not null auto_increment primary key,
    content varchar(255) not null,
    category varchar(255) not null,
    time_stamp timestamp not null default current_timestamp,
    completed boolean not null,
    user_id int not null,
    foreign key (user_id) references user(id)
);
create table letter(
    id int not null auto_increment primary key,
    alphabet_letter char(1) not null,
    votes int not null default 0,
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

-- insert data into database
insert into user(username, email, password, admin) values('Coolsnail123', 'raj@case.edu', 'Skyrim', 1);
insert into user(username, email, password, admin) values('SgtPepper', 'pepperkep@case.edu', 'Inside', 1);
insert into user(username, email, password, admin) values('Meshy00', 'organizer@case.edu', 'DivinityTho', 1);
insert into user(username, email, password, admin) values('Andre3000', 'micycle@case.edu', 'Motorcycle', 0);
insert into user(username, email, password, admin) values('JosephJoeStarII', 'noobmaster69@case.edu', 'MemeLord', 1);

insert into question(content, category, user_id) values('Are Javadoc comments the coolest thing ever?', 'Option 1', select user_id from user where username = 'Coolsnail123');
insert into question(content, category, user_id) values('Is Hot Pie the key to everything?', 'Option 2', select user_id from user where username = 'Andre3000');

insert into letter(alphabet_letter, user_id, question_id) values('Y', 2, 1);
insert into letter(alphabet_letter, user_id, question_id) values('E', 3, 1);
insert into letter(alphabet_letter, user_id, question_id) values('T', 5, 1);
insert into letter(alphabet_letter, user_id, question_id) values('E', 4, 1);
insert into letter(alphabet_letter, user_id, question_id) values('O', 1, 2);
insert into letter(alphabet_letter, user_id, question_id) values('K', 2, 2);
