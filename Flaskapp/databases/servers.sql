PRAGMA foreign_keys = ON;

Create Table If not Exists servers(
    serverID INTEGER PRIMARY KEY CHECK (serverID BETWEEN 100000 AND 999999),
    serverName text not null,
    sessionsActive integer not null DEFAULT 0 CHECK (sessionsActive >= 0),
    isPrivate INTEGER NOT NULL DEFAULT 1 CHECK (isPrivate IN (0, 1))
);

Create Table if Not Exists players(
    serverID integer not null Check (serverID BETWEEN 100000 AND 999999),
    playerName text not null
        CHECK (length(playerName) BETWEEN 1 AND 16)
        CHECK (playerName GLOB '[A-Za-z0-9_]*'),
    killCount integer Not Null DEFAULT 0 CHECK (killCount >= 0),
    deathCount Integer Not Null Default 0 CHECK (deathCount >= 0),

    primary key (serverID, playerName),
    foreign key (serverID) references servers(serverID) on delete cascade
);


