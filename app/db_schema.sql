DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS user_level;
DROP TABLE IF EXISTS appointments;

CREATE TABLE user_level (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_level TEXT UNIQUE NOT NULL
);

INSERT INTO user_level ('user_level')
VALUES
  ('scheduler'),
  ('doctor'),
  ('admin');

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  level_id INTEGER NOT NULL,
  email TEXT UNIQUE NOT NULL,
  fullName TEXT NOT NULL,
  status BOOLEAN default FALSE,
  FOREIGN KEY (level_id) REFERENCES user_level (id)
);

INSERT INTO user ('username', 'password', 'level_id', 'email', 'fullName', 'status')
VALUES
    ('admin', 'admin', 3, 'arbenjohnavillanosa@gmail.com', 'Arben John Avillanosa', TRUE),
    ('scheduler1', 'scheduler1', 1, 'scheduler1@gmail.com', 'Assistant Arben', TRUE),
    ('doctor1', 'doctor1', 2, 'doctor1@gmail.com', 'Doctor Arben', TRUE);

CREATE TABLE appointments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  schedule_time DATETIME NOT NULL,
  patient_name TEXT NOT NULL,
  doctor_id INTEGER,
  comments TEXT,
  is_accepted BOOLEAN default FALSE
);