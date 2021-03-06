BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "task" (
	"id"	INTEGER PRIMARY KEY,
	"description"	TEXT NOT NULL,
	"long_session"	INTEGER NOT NULL DEFAULT 0,
	"tomato"	INTEGER NOT NULL DEFAULT 1,
	"done"	INTEGER NOT NULL DEFAULT 0,
	"complete_time"	INTEGER,
	"deadline"	INTEGER,
	"progress"	INTEGER NOT NULL DEFAULT 0,
	"parent"    INTEGER REFERENCES task (id) 
);
CREATE TABLE "repeated_task" (
	"id"	INTEGER,
	"title"	TEXT NOT NULL,
	"tomato"	INTEGER NOT NULL,
	"once"	INTEGER NOT NULL,
	"next_event"	INTEGER NOT NULL DEFAULT 0,
	"pattern"	TEXT NOT NULL DEFAULT '',
	"type"	TEXT NOT NULL DEFAULT '-',
	"done"	INTEGER NOT NULL DEFAULT 0,
	"last_gen"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "session" (
	"id"	INTEGER NOT NULL UNIQUE,
	"task"	INTEGER,
	"start"	INTEGER NOT NULL,
	"end"	INTEGER NOT NULL,
	"note"	TEXT,
	FOREIGN KEY("task") REFERENCES "task",
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "todo" (
	"id"	INTEGER NOT NULL UNIQUE,
	"description"	TEXT NOT NULL,
	"create_time"	INTEGER NOT NULL,
	"deadline"	INTEGER DEFAULT 0,
	"done"	INTEGER DEFAULT 0,
	"complete_time"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE INDEX IF NOT EXISTS "task_status" ON "task" (
	"done"
);
CREATE INDEX IF NOT EXISTS "session_task" ON "session" (
	"task"
);
CREATE INDEX IF NOT EXISTS "todo_done" ON "todo" (
	"done"
);
COMMIT;
