create database if not exists `eHealth`;
use `eHealth`;

drop table if exists`patients`;
create table if not exists `patients` (
    `id`            int              not null    auto_increment  primary key,
    `name`          varchar(100)     not null,
    `email`         varchar(150)     not null   unique,
    `password`      varchar(256)     not null,
    `phone`         char(10),
    `profile_pic`   varchar(250) DEFAULT 'default.png'     -- TODO adicionar imagem
);

insert into patients (name, email, password, phone) values ('Netty Wrefford', 'nwrefford1@tmall.com', 'KWKxuy', '3355710502');
insert into patients (name, email, password, phone) values ('Hali Donwell', 'hdonwell2@state.tx.us', 'DmBMnFoKEW', '3788933004');
insert into patients (name, email, password, phone) values ('Justinian Krebs', 'jkrebs3@bloglines.com', 'HiPyXTdQ4CrU', '4282135927');
insert into patients (name, email, password, phone) values ('Jorry Seiller', 'jseiller0@goo.net', 'UfzBESyz', '4995358663');
insert into patients (name, email, password, phone) values ('Leroy Esche', 'lesche4@themeforest.net', 'SBo29PG', '5197321309');
insert into patients (name, email, password, phone) values ('Nady Jakubczyk', 'njakubczyk5@phoca.cz', '7IjF4q1Kk', '8614307489');
insert into patients (name, email, password, phone) values ('Eugene Bernhardt', 'ebernhardt6@1und1.de', 'EPVSCJzyZZ', '7701289577');
insert into patients (name, email, password, phone) values ('Roda Shephard', 'rshephard7@aboutads.info', 'esZHeHNVUS', '7599935717');
insert into patients (name, email, password, phone) values ('Ilario Chritchley', 'ichritchley8@php.net', 'XmVoiKD6', '3552780449');
insert into patients (name, email, password, phone) values ('Melony Grimmert', 'mgrimmert9@taobao.com', 'a3woSc6', '3702735495');
insert into patients (name, email, password, phone) values ('Mankings', 'mankings@mankings.pt', 'mankings', '9677855555');

drop table if exists `departments`;
create table if not exists `departments` (
    `id`        int             not null    auto_increment  primary key,
    `name`      varchar(100)    not null
);

insert into departments(name) values ('Dentist');
insert into departments(name) values ('Orthopedics');
insert into departments(name) values ('Psycology');
insert into departments(name) values ('Diagnostic');
insert into departments(name) values ('General treatment');
insert into departments(name) values ('X-Ray');
insert into departments(name) values ('Cardiology');

drop table if exists `doctors`;
create table if not exists `doctors` (
    `id`                int                 not null     auto_increment  primary key,
    `name`              varchar(100)        not null,
    `email`             varchar(150)        not null,
    `password`          varchar(20)         not null,
    `phone`             char(10),
    `department_id`     int                 not null,
    `profile_pic`       varchar(250)        DEFAULT 'doctor-1.jpg',
    foreign key (`department_id`) references departments(`id`)
);

insert into doctors (name, email, password, phone, department_id) values ('Kalila Nassi', 'knassi0@biglobe.ne.jp', 'uOIJbQYl', '6261570629', 1);
insert into doctors (name, email, password, phone, department_id) values ('Aggi Ferraraccio', 'aferraraccio1@jugem.jp', 'CzEy493Iv', '7366905799', 2);
insert into doctors (name, email, password, phone, department_id) values ('Sax Bellino', 'sbellino2@mapquest.com', '1vhW8QowfoXT', '8147242660', 3);
insert into doctors (name, email, password, phone, department_id) values ('Curry Roundtree', 'croundtree3@cisco.com', '3iDpXs0BDA', '7359641114', 4);
insert into doctors (name, email, password, phone, department_id) values ('Royall Proske', 'rproske4@virginia.edu', 'IA6Ynf', '9744022260', 5);
insert into doctors (name, email, password, phone, department_id) values ('Salome Cloute', 'scloute5@a8.net', '59OotLyJ', '5907429618', 1);
insert into doctors (name, email, password, phone, department_id) values ('Joanie Puig', 'jpuig6@upenn.edu', 'JKBWh4zK', '4208549125', 5);
insert into doctors (name, email, password, phone, department_id) values ('Gardener Cundy', 'gcundy7@t-online.de', 'x6ECx0y', '8834564842', 6);
insert into doctors (name, email, password, phone, department_id) values ('Gibbie Poulney', 'gpoulney8@amazonaws.com', 'oc7zhnEAP', '2919685797', 7);
insert into doctors (name, email, password, phone, department_id) values ('Martelle Very', 'mvery9@ezinearticles.com', '3Pcr3Tm8v6', '9148343125', 1);

drop table if exists `appointments`;
create table if not exists `appointments` (  
    `id`                    int     not null    auto_increment  primary key,
    `patient_id`            int     not null,
    `doctor_id`             int     not null,
    `department_id`         int,
    `date`                  date    not null,
    `message`               varchar(255),
    foreign key (`patient_id`)  references patients(`id`),
    foreign key (`doctor_id`)   references doctors(`id`)
);

insert into appointments (patient_id, doctor_id, department_id, date, message) values (1, 1, 1, '2022-06-21', 'Duis bibendum. Morbi non quam nec dui luctus rutrum.');
insert into appointments (patient_id, doctor_id, department_id, date, message) values (2, 2, 2, '2022-07-29', null);
insert into appointments (patient_id, doctor_id, department_id, date, message) values (3, 3, 3, '2021-12-04', null);
insert into appointments (patient_id, doctor_id, department_id, date, message) values (4, 4, 4, '2022-08-06', 'Quisque ut erat. Curabitur gravida nisi at nibh.');
insert into appointments (patient_id, doctor_id, department_id, date, message) values (5, 5, 5, '2022-09-29', 'Integer ac neque.');
insert into appointments (patient_id, doctor_id, department_id, date, message) values (6, 6, 1, '2022-01-08', 'Aenean fermentum.');
insert into appointments (patient_id, doctor_id, department_id, date, message) values (7, 7, 5, '2022-04-16', null);
insert into appointments (patient_id, doctor_id, department_id, date, message) values (8, 8, 6, '2022-07-13', null);
insert into appointments (patient_id, doctor_id, department_id, date, message) values (9, 9, 7, '2021-11-22', 'Aenean lectus.');
insert into appointments (patient_id, doctor_id, department_id, date, message) values (10, 10, 1, '2022-03-07', 'Ut tellus. Nulla ut erat id mauris vulputate elementum.');
insert into appointments (patient_id, doctor_id, department_id, date, message) values (1, 1, 1, '2021-12-25', null);
insert into appointments (patient_id, doctor_id, department_id, date, message) values (2, 2, 2, '2022-07-17', null);
insert into appointments (patient_id, doctor_id, department_id, date, message) values (3, 3, 3, '2022-05-30', null);
insert into appointments (patient_id, doctor_id, department_id, date, message) values (4, 4, 4, '2022-03-01', 'Maecenas ut massa quis augue luctus tincidunt.');
insert into appointments (patient_id, doctor_id, department_id, date, message) values (5, 5, 5, '2022-04-06', null);

drop table if exists `comments`;
create table if not exists `comments` (
    `id`        int             not null        auto_increment  primary key,
    `author`    varchar(100)    not null,
    `email`     varchar(150)    not null,
    `text`      varchar(255)    not null
);

insert into comments (author, email, text) values ('Janella Dameisele', 'jdameisele0@adobe.com', 'Curabitur gravida nisi at nibh. In hac habitasse platea dictumst.');
insert into comments (author, email, text) values ('Florette Ren', 'fren1@mit.edu', 'Fusce congue, diam id ornare imperdiet, sapien urna pretium nisl, ut volutpat sapien arcu sed augue.');
insert into comments (author, email, text) values ('Lynne Luckett', 'lluckett2@gmpg.org', 'Sed ante. Vivamus tortor.');
insert into comments (author, email, text) values ('Ozzie Nevett', 'onevett3@businesswire.com', 'Donec ut mauris eget massa tempor convallis. Nulla neque libero, convallis eget, eleifend luctus, ultricies eu, nibh.');
insert into comments (author, email, text) values ('Sheree Daly', 'sdaly4@vk.com', 'Integer pede justo, lacinia eget, tincidunt eget, tempus vel, pede.');

drop table if exists `exams`;
create table if not exists `exams` (
    `id`            int             not null    auto_increment  primary key,
    `code`          varchar(100)    not null,
    `patient_id`    int             not null,
    `test_results`  varchar(200)    not null
);

insert into exams (code, patient_id, test_results) values ('QWERTYUI', 1, 'You took an arrow to the knee!');
insert into exams (code, patient_id, test_results) values ('GYUBHGDS', 2, 'You have heterochromia.');
insert into exams (code, patient_id, test_results) values ('POJGBTSG', 6, 'You were bitten by a radioactive spider.');
insert into exams (code, patient_id, test_results) values ('CFBGSRFJ', 9, 'You have schizophrenia!');
insert into exams (code, patient_id, test_results) values ('PHGFXVRT', 6, 'You are just stupid.');
insert into exams (code, patient_id, test_results) values ('PNBHYCHC', 4, 'You like matlab (disability).');
insert into exams (code, patient_id, test_results) values ('KINBBGXB', 1, 'You are an alcoholic.');
insert into exams (code, patient_id, test_results) values ('PNEGGFDS', 7, 'You have a god complex.');
insert into exams (code, patient_id, test_results) values ('ZRTCYREG', 3, 'You are color blind.');
insert into exams (code, patient_id, test_results) values ('NHYFCGFT', 2, 'You are insignificant in the grand scheme of things.');
insert into exams (code, patient_id, test_results) values ('BHGGIFDS', 7, 'You are fine.');
insert into exams (code, patient_id, test_results) values ('YVCDUXUV', 8, 'You are dislexic.');
insert into exams (code, patient_id, test_results) values ('LJVFTDCG', 8, 'You have asthma.');
insert into exams (code, patient_id, test_results) values ('EHCFYCIX', 2, 'You are having an early life crisis.');
insert into exams (code, patient_id, test_results) values ('NHFDXDEY', 1, 'You are unable to follow SQL syntax.');
insert into exams (code, patient_id, test_results) values ('UDSEFVJI', 9, 'You walk too fast.');