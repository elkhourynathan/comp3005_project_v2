-- Create the Member table
DROP TABLE IF EXISTS Bill, Sessions,Classes, Admin, Equipment, Availability, Trainer, Routine, Member CASCADE;
CREATE TABLE Member (
    ID SERIAL PRIMARY KEY,
    Username VARCHAR(255) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Name VARCHAR(255) NOT NULL,
    ProfileInfo TEXT,
    FitnessGoals TEXT,
    HealthMetrics TEXT,
    Height DECIMAL(5, 2),
    Weight DECIMAL(5, 2),
    GoalWeight DECIMAL(5, 2),
    GoalWorkoutsPerWeek INT
);

-- Create the Routine table
CREATE TABLE Routine (
    ID SERIAL PRIMARY KEY,
    MemberID INT REFERENCES Member(ID),
    Type VARCHAR(255) NOT NULL,
    Date DATE NOT NULL
);

-- Create the Trainer table
CREATE TABLE Trainer (
    ID SERIAL PRIMARY KEY,
    Username VARCHAR(255) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Name VARCHAR(255) NOT NULL,
    Schedule TEXT
);

-- Create the Availability table
CREATE TABLE Availability (
    ID SERIAL PRIMARY KEY,
    TrainerID INT REFERENCES Trainer(ID),
    AvailableStart TIMESTAMP NOT NULL,
    AvailableEnd TIMESTAMP NOT NULL
);

-- Create the Admin table
CREATE TABLE Admin (
    ID SERIAL PRIMARY KEY,
    Username VARCHAR(255) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Name VARCHAR(255) NOT NULL
);

-- Create the Class table
CREATE TABLE Classes (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(255),
    Room VARCHAR(255),
    Schedule TIMESTAMP
);

-- Create the Sessions table
CREATE TABLE Sessions (
    ID SERIAL PRIMARY KEY,
    MemberID INT REFERENCES Member(ID),
    TrainerID INT REFERENCES Trainer(ID),
    DateTime TIMESTAMP
);

-- Create the Equipment table
CREATE TABLE Equipment (
    EquipmentID SERIAL PRIMARY KEY,
    Type VARCHAR(255),
    MaintenanceSchedule TIMESTAMP
);

-- Create the Bill table
CREATE TABLE Bill (
    ID SERIAL PRIMARY KEY,
    MemberID INT REFERENCES Member(ID),
    Amount DECIMAL(10, 2),
    Date TIMESTAMP
);
