DROP TABLE IF EXISTS clients;

CREATE TABLE clients
(
    name TEXT PRIMARY KEY,
    info TEXT
);

DROP TABLE IF EXISTS suspicious_activities;

CREATE TABLE suspicious_activities
(
    time          date default now(),
    target_name   TEXT REFERENCES clients (name),
    attacker_info TEXT,
    PRIMARY KEY (time, target_name, attacker_info)
);


INSERT INTO clients
values ('John Doe', 'hello world');
INSERT INTO suspicious_activities(target_name, attacker_info)
values ('John Doe', 'somethin');