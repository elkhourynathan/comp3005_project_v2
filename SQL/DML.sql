-- Mock data inserts
-- Inserting Members
INSERT INTO Member (username, password, name, profile_info, fitness_goals, health_metrics, height, weight, goal_weight, goal_workouts_per_week) VALUES
('test', 'test', 'Test User', 'Test Profile', 'Test Goals', 'Test Metrics', 180, 85, 75, 3),
('johndoe', 'password', 'John Doe', 'I love gym', 'Lose weight, Build muscle', 'No known issues', 180, 85, 75, 3),
('janedoe', 'password', 'Jane Doe', 'Me love run', 'Increase stamina, Run a marathon', 'Asthma', 165, 60, 58, 5);

-- Inserting Trainers
INSERT INTO Trainer (username, password, name, schedule) VALUES
('trainer_tom', 'password', 'Tom', 'Flexible'),
('trainer_tina', 'password', 'Tina', 'Mornings');

-- Inserting Admins
INSERT INTO Admin (username, password, name) VALUES
('admin_alice', 'alicepass', 'Alice Johnson'),
('admin_bob', 'bobspass', 'Bob White');

-- Insert Availability assume TrainerID 1 is Tom and TrainerID 2 is Tina
INSERT INTO Availability (trainer_id, available_start, available_end) VALUES
(1, '2024-04-01 09:00:00', '2024-04-01 12:00:00'),
(1, '2024-04-02 14:00:00', '2024-04-02 16:00:00'),
(2, '2024-04-01 08:00:00', '2024-04-01 11:00:00');

-- Inserting Classes
INSERT INTO Classes (name, room, schedule) VALUES
('Yoga Basics', 'Room A', '2024-04-03 10:00:00'),
('Advanced Cardio', 'Room B', '2024-04-04 08:00:00');

-- Inserting Sessions (assume MemberID 1 is John Doe, TrainerID 1 is Tom Smith)
-- INSERT INTO Sessions (member_id, trainer_id, date_time) VALUES
-- (1, 1, '2024-04-01 10:00:00'),
-- (1, 1, '2024-04-02 15:00:00');

-- Inserting Equipment
INSERT INTO Equipment (type, maintenance_schedule) VALUES
('Treadmill', '2024-05-01'),
('Rowing Machine', '2024-05-15');

-- Inserting Bills for John Doe
-- INSERT INTO Bill (member_id, amount, date) VALUES
-- (1, 100.00, '2024-03-01'),
-- (1, 150.00, '2024-04-01');

-- Inserting Routines for John Doe
INSERT INTO Routine (member_id, type, date) VALUES
(1, 'Cardio', '2024-03-31'),
(1, 'Strength', '2024-04-01');
