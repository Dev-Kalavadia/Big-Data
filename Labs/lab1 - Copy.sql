-- The MySQL database lab
-- We are going to create database for students and course enrollements: we use the following schema

create database university;
use university;

-- student(sid, sname)
-- course(cid, cname, limit)
-- course_enroll(cid, sid, pid)

create table student(
sid integer,
sname varchar(20)
);

-- Add a couple of instances to the table student 

insert into student values (1, "Omar");
Insert into student(sid, sname) values (1, "ola");

-- We can check the content of the table with
select * from student;

-- Wait! We are not supposed to have duplicate IDs (business requirement)
-- First lets drop the duplicate record
delete from student where sname = "ola";

-- You can add a unique constraint to the Sid column in the student table to enforce the requirement that IDs should not be duplicated. You can do this by running the following command:
ALTER TABLE student ADD PRIMARY KEY (sid);

-- This will add a unique (primary actually) constraint on the Sid column, so when you try to insert a duplicate value into that column, an error will be thrown and the insert will be "rolled back".
insert into student values (1, "ola"); -- expect an error
insert into student values (2, "ola");


-- we can continue creating the remaining course tables
create table course(
cid integer,
cname varchar(20),
climit integer
);




