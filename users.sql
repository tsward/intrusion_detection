-- CS 880 - Spring 2019 
-- Final Project 
-- User Database - SQL Source File 
 

use CS880

drop table usr;

 
/* TODO: break down with more tables? */
CREATE TABLE usr 
(
   ssn         INTEGER(9),
   username     CHAR(50),
   pwd          CHAR(50),
   fname		CHAR(25),
   lname		CHAR(25),
   email        char(50),
   administrator INTEGER(1),
   dnum         INTEGER(4),
   login_attempts       INTEGER(1),
   locked       INTEGER(1),
   
 
   PRIMARY KEY (ssn) 
); 
 
INSERT INTO usr VALUES 


(123456789, 'admin','password','Tim','Ward', 'tsward6@gmail.com', 1, 0001, 0, 0),
(234567890,'ericthemidget','ackackack','Eric','Lynch', 'etm@gmail.com', 0, 0001, 0, 0), 
(345678901,'dabadass','12345678','JD','Harmier', 'dabadass@yahoo.com', 0, 0002, 5, 0),
(456789012,'scoresman','pegging4life','Ronnie','Mund', 'scoresman69@gmail.com', 0, 0003, 2, 0),
(567890123,'drremulak','iamdrremulak','Sebastian','Remulak', 'drremulak@gmail.com', 0, 0003, 1, 0); 
 
 
 

SELECT * FROM usr; 
 
