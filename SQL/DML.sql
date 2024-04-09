-- Inserting Members
INSERT INTO Member (username, password, name, profile_info, fitness_goals, health_metrics, height, weight, goal_weight, goal_workouts_per_week) VALUES
('test', 'test', 'Test User', 'Test Profile', 'Test Goals', 'Test Metrics', 180, 85, 75, 3),
('johnsmith', 'password', 'John Smith', 'I love gym', 'Lose weight, Build muscle', 'No known issues', 180, 85, 75, 3),
('janedoe', 'password', 'Jane Doe', 'Me love run', 'Increase stamina, Run a marathon', 'Asthma', 165, 60, 58, 5);

-- Inserting Trainers
INSERT INTO Trainer (username, password, name) VALUES
('trainer_tom', 'tompas', 'Tom'),
('trainer_tina', 'tompass', 'Tina');

-- Inserting Admins
INSERT INTO Admin (username, password, name) VALUES
('admin_alice', 'alicepass', 'Alice'),
('admin_bob', 'bobspass', 'Bob');


-- Insert Availability for tom and tina
INSERT INTO Availability (trainer_id, available_start, available_end, open) VALUES
(1, '2024-04-01 09:00:00', '2024-04-01 10:00:00', False),
(1, '2024-04-02 14:00:00', '2024-04-02 15:00:00', False),
(2, '2024-04-01 08:00:00', '2024-04-01 09:00:00', True);
(1, '2024-04-01 06:00:00', '2024-04-01 07:00:00', False);


-- Inserting Sessions
INSERT INTO Sessions (member_id, availability_id) VALUES
(1,4);

INSERT INTO Room (name) VALUES
('Room A'),
('Room B');

-- Inserting Classes
INSERT INTO Classes (availability_id, room_id, name) VALUES
(1, 1,'Yoga Basics'),
(2, 2,'Cycling Class');

-- Insert a Member_Class 
INSERT INTO Member_Class (member_id, class_id) VALUES
(1, 1);

-- Inserting Equipment
INSERT INTO Equipment (type, last_maintained, next_maintenance) VALUES
('Treadmill', '2024-05-01', '2024-06-01'),
('Rowing Machine', '2024-05-15', '2024-06-15'),
('Dumbbells', '2024-06-01', '2024-07-01'),
('Barbell', '2024-06-01', '2024-07-01'),
('Kettlebell', '2024-06-01', '2024-07-01'),
('Bench Press', '2024-06-01', '2024-07-01'),
('Squat Rack', '2024-06-01', '2024-07-01');


-- Inserting Routines 
INSERT INTO Routine (member_id, type, date) VALUES
(1, 'Cardio', '2024-03-31'),
(1, 'Strength', '2024-04-01'),
(2, 'Cardio', '2024-04-01'),
(2, 'Strength', '2024-04-02'),
(3, 'Cardio', '2024-04-01'),
(3, 'Strength', '2024-04-02');

-- Some unprocessed bills
INSERT INTO Bill (member_id, amount, type, paid, date) VALUES
(1, 100, 'Membership', False, '2024-04-01'),
(2, 100, 'Membership', False, '2024-04-01'),
(3, 100, 'Membership', False, '2024-04-01');