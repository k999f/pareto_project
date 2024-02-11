DROP TABLE IF EXISTS role CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS project CASCADE;
DROP TABLE IF EXISTS calculation CASCADE;
DROP TABLE IF EXISTS analysis CASCADE;
DROP TABLE IF EXISTS indicator CASCADE;
DROP TABLE IF EXISTS algorythm CASCADE;
DROP TABLE IF EXISTS task CASCADE;
DROP TABLE IF EXISTS estimation CASCADE;
DROP TABLE IF EXISTS tasks_in_analysis CASCADE;


/*                                     TABLES                                            */
/*---------------------------------------------------------------------------------------*/

CREATE TABLE role
(
	role TEXT PRIMARY KEY
);

INSERT INTO role (role)
VALUES ('auth'), ('client'), ('admin');

/*---------------------------------------------------------------------------------------*/

CREATE TABLE users
(
	id SERIAL PRIMARY KEY,
	login TEXT NOT NULL,
	password TEXT NOT NULL,
	role TEXT NOT NULL,
	UNIQUE (login),
	FOREIGN KEY (role) REFERENCES role (role)
);

INSERT INTO users (login, password, role)
VALUES ('admin', 'admin', 'admin'), ('client', 'client', 'client');

/*---------------------------------------------------------------------------------------*/

CREATE TABLE project
(
	id SERIAL PRIMARY KEY,
	user_id INT,
	name TEXT NOT NULL,
	created DATE DEFAULT current_date,
	modified DATE DEFAULT current_date,
	description TEXT,
	FOREIGN KEY (user_id) REFERENCES users (id)
);

/*---------------------------------------------------------------------------------------*/

CREATE TABLE algorythm
(
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL
);

INSERT INTO algorythm (name)
VALUES ('algorythm1'), ('algorythm2'), ('algorythm3');

/*---------------------------------------------------------------------------------------*/

CREATE TABLE indicator
(
	id SERIAL PRIMARY KEY,
	type TEXT,
	name TEXT NOT NULL
);

INSERT INTO indicator (name, type)
VALUES ('unary1', 'unary'), ('unary2', 'unary'), ('unary3', 'unary'), ('binary1', 'binary'), ('binary2', 'binary'), ('binary3', 'binary');

/*---------------------------------------------------------------------------------------*/

CREATE TABLE task
(
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL,
	type TEXT,
	data TEXT
);

INSERT INTO task (name, type, data)
VALUES ('task1', 'standard', 'Standard task'), ('task2', 'standard', 'Standard task'), ('task3', 'standard', 'Standard task');

/*---------------------------------------------------------------------------------------*/

CREATE TABLE calculation
(
	id SERIAL PRIMARY KEY,
	project_id INT,
	name TEXT NOT NULL,
	created DATE DEFAULT current_date,
	approximation TEXT,
	indicators TEXT,
	algorythm_parameters TEXT,
	task_parameters TEXT,
	algorythm_id INT,
	task_id INT,
	FOREIGN KEY (project_id) REFERENCES project (id) ON DELETE CASCADE,
	FOREIGN KEY (algorythm_id) REFERENCES algorythm (id),
	FOREIGN KEY (task_id) REFERENCES task (id) ON DELETE CASCADE
);

/*---------------------------------------------------------------------------------------*/

CREATE TABLE estimation
(
	id SERIAL PRIMARY KEY,
	project_id INT,
	name TEXT NOT NULL,
	created DATE DEFAULT current_date,
	first_front TEXT,
	second_front TEXT,
	reference_set TEXT,
	output_data TEXT,
	indicator_id INT,
	FOREIGN KEY (project_id) REFERENCES project (id) ON DELETE CASCADE,
	FOREIGN KEY (indicator_id) REFERENCES indicator (id)
);

/*---------------------------------------------------------------------------------------*/

CREATE TABLE analysis
(
	id SERIAL PRIMARY KEY,
	project_id INT,
	name TEXT NOT NULL,
	created DATE DEFAULT current_date,
	algorythm_id INT,
	algorythm_parameters TEXT,
	output_data TEXT,
	FOREIGN KEY (algorythm_id) REFERENCES algorythm (id),
	FOREIGN KEY (project_id) REFERENCES project (id) ON DELETE CASCADE
);

/*---------------------------------------------------------------------------------------*/

CREATE TABLE tasks_in_analysis
(
	analysis_id INT,
	task_id INT,
	task_parameters TEXT,
	UNIQUE (analysis_id, task_id),
	FOREIGN KEY (analysis_id) REFERENCES analysis (id) ON DELETE CASCADE,
	FOREIGN KEY (task_id) REFERENCES task (id) ON DELETE CASCADE
);

CREATE TABLE algorythms_in_analysis
(
	analysis_id INT,
	algorythm_id INT,
	algorythm_parameters TEXT,
	UNIQUE (analysis_id, algorythm_id),
	FOREIGN KEY (analysis_id) REFERENCES analysis (id) ON DELETE CASCADE,
	FOREIGN KEY (algorythm_id) REFERENCES algorythm (id) ON DELETE CASCADE
);

CREATE TABLE algorythm_parameters
(
	algorythm_id INT,
	parameter TEXT,
	FOREIGN KEY (algorythm_id) REFERENCES algorythm (id) ON DELETE CASCADE
);

INSERT INTO algorythm_parameters (algorythm_id, parameter)
VALUES ('1', 'No parameters'), ('2', 'a2_p1'), ('2', 'a2_p2'), ('3', 'a3_p1'), ('3', 'a3_p2'), ('3', 'a3_p3');

CREATE TABLE task_parameters
(
	task_id INT,
	parameter TEXT,
	FOREIGN KEY (task_id) REFERENCES task (id) ON DELETE CASCADE
);

INSERT INTO task_parameters (task_id, parameter)
VALUES ('1', 'No parameters'), ('2', 't2_p1'), ('2', 't2_p2'), ('3', 't3_p1'), ('3', 't3_p2'), ('3', 't3_p3');


/*                                     TRIGGERS                                            */
/*-----------------------------------------------------------------------------------------*/
