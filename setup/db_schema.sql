DROP Table if EXISTS Adoption;
DROP Table if EXISTS AdoptionApplication;
DROP Table if EXISTS BelongTo;
DROP Table if EXISTS EXPENSE;
DROP Table if EXISTS Dog;
DROP Table if EXISTS Owner;
DROP Table if EXISTS User;
DROP Table if EXISTS Breed;
DROP Table if EXISTS Adopter;


CREATE TABLE User (
	email varchar(250) NOT NULL,
	password varchar(250) NOT NULL,
	first_name varchar(100) NOT NULL,
	last_name varchar(100) NOT NULL,
	date date NOT NULL,
	cell_phone VARCHAR(100) NOT NULL,
	PRIMARY KEY (email)
);


CREATE TABLE Dog (
	dogID int(16) unsigned NOT NULL AUTO_INCREMENT,
	user varchar(250) NOT NULL,
	name varchar(100) NOT NULL,
	sex ENUM('male', 'female', 'unknown') NOT NULL,
	alteration TINYINT NOT NULL,
	description VARCHAR(250) NOT NULL,
	age int(16) NOT NULL,
	microchipID VARCHAR(250) NULL,
	surrender_date date NOT NULL,
	surrender_reason varchar(1000) NOT NULL,
	surrender_by_animal_control TINYINT NOT NULL,
	PRIMARY KEY (dogID)
);

CREATE TABLE Expense (
	dogID int(16) unsigned NOT NULL,
	date date NOT NULL,
	amount int(16) NOT NULL,
	vendor varchar(250) NOT NULL,
	optional_description varchar(1000) NULL,
	PRIMARY KEY (dogID, date, vendor)
);

CREATE TABLE AdoptionApplication (
	application_num int(16) unsigned NOT NULL AUTO_INCREMENT,
	adopter varchar(250) NOT NULL,
	date date NOT NULL,
	status ENUM('pending approval', 'approved', 'rejected') NOT NULL Default 'pending approval',
	co_applicant_first_name varchar(100) NULL,
	co_applicant_last_name varchar(100) NULL,
	PRIMARY KEY (application_num)
);

CREATE TABLE Adopter (
	email varchar(250) NOT NULL,
	first_name varchar(100) NOT NULL,
	last_name varchar(100) NOT NULL,
	street varchar(250) NOT NULL,
	city varchar(100) NOT NULL,
	state varchar(100) NOT NULL,
	zip_code varchar(100) NOT NULL,
	cell_phone VARCHAR(100) NOT NULL,
	PRIMARY KEY (email)
);

CREATE TABLE Adoption (
	application int(16) unsigned NOT NULL,
	dog int(16) unsigned NOT NULL,
	adoption_fee float(10) DEFAULT 0 NOT NULL,
	adoption_date date  NOT NULL,
	PRIMARY KEY (application, dog)
);

CREATE TABLE Breed (
	breed varchar(250) NOT NULL,
	PRIMARY KEY (breed)
);

CREATE TABLE BelongTo (
  dogID int(16) unsigned NOT NULL,
	breed varchar(250) NOT NULL,
  PRIMARY KEY (dogID, breed)
);


CREATE TABLE `Owner` (
	email varchar(250) NOT NULL,
	PRIMARY KEY (email)
);


-- Constraints   Foreign Keys

ALTER TABLE Owner
	ADD CONSTRAINT fk_Owner_email_User_email FOREIGN KEY (email) REFERENCES `User` (email);
	
ALTER TABLE Dog
	ADD CONSTRAINT fk_Dog_user_email_User_email FOREIGN KEY (user) REFERENCES `User` (Email);
	
ALTER TABLE Expense
	ADD CONSTRAINT fk_Expense_dogID_Dog_dogID FOREIGN KEY (dogID) REFERENCES `Dog` (dogID);
	
ALTER TABLE BelongTo
  ADD CONSTRAINT fk_BelongTo_dogID_Dog_dogID FOREIGN KEY (dogID) REFERENCES `Dog` (dogID),
  ADD CONSTRAINT fk_BelongTo_breed_Breed_breed FOREIGN KEY (breed) REFERENCES `Breed` (breed);
	
ALTER TABLE AdoptionApplication
	ADD CONSTRAINT fk_AdoptionApplication_adopter_adopter_email  FOREIGN KEY (adopter) REFERENCES `Adopter` (email);
	
ALTER TABLE Adoption
  ADD CONSTRAINT fk_Adoption_application_AdoptionApplication_application_num FOREIGN KEY (application) REFERENCES `AdoptionApplication` (application_num) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT fk_Adoption_dog_Dog_dogID FOREIGN KEY (dog) REFERENCES `Dog` (dogID) ON DELETE CASCADE ON UPDATE CASCADE;

delimiter //
CREATE TRIGGER Cal_Expense
	BEFORE INSERT
    ON Adoption FOR EACH ROW
	BEGIN

		DECLARE fee FLOAT(10);
    
		SELECT CASE WHEN surrender_by_animal_control = 1 THEN sum(amount) * 0.15 
				ELSE sum(amount) * 1.15	END INTO Fee
			FROM Expense	
			INNER JOIN Dog
			USING (dogID)
			GROUP BY dogID
            HAVING dogID = NEW.dog;
	
		SET NEW.adoption_fee = fee;
        
        IF NEW.adoption_fee IS NULL THEN
			SET NEW.adoption_fee = 0;
		END IF;
	END//


delimiter ;


