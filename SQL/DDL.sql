-- Create the Member table
DROP TABLE IF EXISTS Bill, Sessions, Classes, Admin,Member_Classes, Equipment, Availability, Trainer, Routine, Member, Room CASCADE;
CREATE TABLE Member (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    profile_info TEXT,
    fitness_goals TEXT,
    health_metrics TEXT,
    height FLOAT,
    weight FLOAT,
    goal_weight FLOAT,
    goal_workouts_per_week INT
);

-- Create the Routine table
CREATE TABLE Routine (
    id SERIAL PRIMARY KEY,
    member_id INT REFERENCES Member(id),
    type VARCHAR(255) NOT NULL,
    date DATE NOT NULL
);

-- Create the Trainer table
CREATE TABLE Trainer (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL
);

-- Create the Availability table
CREATE TABLE Availability (
    id SERIAL PRIMARY KEY,
    trainer_id INT REFERENCES Trainer(id),
    available_start TIMESTAMP NOT NULL,
    available_end TIMESTAMP NOT NULL,
    open BOOLEAN DEFAULT TRUE
);

-- Create the Admin table
CREATE TABLE Admin (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL
);

-- Create the Room table
CREATE TABLE Room (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255)
);

-- Create the Class table
CREATE TABLE Classes (
    id SERIAL PRIMARY KEY,
    availability_id INT REFERENCES Availability(id),
    room_id INT REFERENCES Room(id),
    name VARCHAR(255)
);


-- Create the Member_Classes table
CREATE TABLE Member_Classes (
    member_id INT REFERENCES Member(id),
    class_id INT REFERENCES Classes(id),
    PRIMARY KEY (member_id, class_id)
);

-- Create the Sessions table
CREATE TABLE Sessions (
    id SERIAL PRIMARY KEY,
    member_id INT REFERENCES Member(id),
    availability_id INT REFERENCES Availability(id)
);

-- Create the Equipment table
CREATE TABLE Equipment (
    id SERIAL PRIMARY KEY,
    type VARCHAR(255),
    last_maintained TIMESTAMP,
    next_maintenance TIMESTAMP
);

-- Create the Bill table
CREATE TABLE Bill (
    id SERIAL PRIMARY KEY,
    member_id INT REFERENCES Member(id),
    amount FLOAT,
    paid BOOLEAN,
    type VARCHAR(255),
    date TIMESTAMP
);


-- Indexes for member id related tables
CREATE INDEX idx_member_name on Member(name);
CREATE INDEX idx_availability_trainer_id on Availability(trainer_id);
CREATE INDEX idx_member_classes_id on Member_Classes(member_id);
