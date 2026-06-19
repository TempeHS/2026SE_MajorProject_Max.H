PRAGMA foreign_keys = ON;

Create Table If Not Exists Logins(
    Email Text Primary Key Not Null,
    passingWord Text Not Null,
    userID Integer Unique Not Null Check (userID BETWEEN 100000 AND 999999)
);

Create Table If not Exists servers(
    serverHost Text PRIMARY KEY NOT NULL,
    serverPort INTEGER NOT NULL DEFAULT 25565 CHECK (serverPort BETWEEN 1 AND 65535),
    userID Integer Not Null Check (userID BETWEEN 100000 AND 999999),
    serverName text not null,
    sessionsActive integer not null DEFAULT 0 CHECK (sessionsActive >= 0),
    isPrivate INTEGER NOT NULL DEFAULT 1 CHECK (isPrivate IN (0, 1)),

    foreign key (userID) references Logins(userID) on delete cascade
);

Create Table If Not Exists players(
    serverHost Text not null,
    playerName Text not null
        CHECK (length(playerName) BETWEEN 1 AND 32),
    killCount integer Not Null DEFAULT 0 CHECK (killCount >= 0),
    deathCount Integer Not Null Default 0 CHECK (deathCount >= 0),
    currentLife integer Not Null Default 3 Check (currentLife >= 0),

    Primary Key (serverHost, playerName),
    foreign key (serverHost) references servers(serverHost) on delete cascade
);

Create Table If Not Exists serverKills(
    serverHost Text Not Null,
    playerKillerName text Not null
        CHECK (length(playerKillerName) BETWEEN 1 AND 32),
    playerKilledName text not null
        CHECK (length(playerKilledName) BETWEEN 1 AND 32),
    weaponUsed text not null,
    timeOfDeath datetime not null default current_timestamp,

    foreign key (serverHost) references servers(serverHost) on delete cascade
);




