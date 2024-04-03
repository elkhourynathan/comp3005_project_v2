-- Create the Member table
DROP TABLE IF EXISTS Bill, Sessions, Classes, Admin, Equipment, Availability, Trainer, Routine, Member CASCADE;
CREATE TABLE Member (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    profile_info TEXT,
    fitness_goals TEXT,
    health_metrics TEXT,
    height DECIMAL(5, 2),
    weight DECIMAL(5, 2),
    goal_weight DECIMAL(5, 2),
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
    name VARCHAR(255) NOT NULL,
    schedule TEXT
);

-- Create the Availability table
CREATE TABLE Availability (
    id SERIAL PRIMARY KEY,
    trainer_id INT REFERENCES Trainer(id),
    available_start TIMESTAMP NOT NULL,
    available_end TIMESTAMP NOT NULL
);

-- Create the Admin table
CREATE TABLE Admin (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL
);

-- Create the Class table
CREATE TABLE Classes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    room VARCHAR(255),
    schedule TIMESTAMP
);

-- Create the Sessions table
CREATE TABLE Sessions (
    id SERIAL PRIMARY KEY,
    member_id INT REFERENCES Member(id),
    trainer_id INT REFERENCES Trainer(id),
    date_time TIMESTAMP
);

-- Create the Equipment table
CREATE TABLE Equipment (
    equipment_id SERIAL PRIMARY KEY,
    type VARCHAR(255),
    maintenance_schedule TIMESTAMP
);

-- Create the Bill table
CREATE TABLE Bill (
    id SERIAL PRIMARY KEY,
    member_id INT REFERENCES Member(id),
    amount DECIMAL(10, 2),
    date TIMESTAMP
);
