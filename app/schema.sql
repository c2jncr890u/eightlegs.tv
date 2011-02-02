
SET SESSION storage_engine = "InnoDB";
SET SESSION time_zone = "+0:00";
ALTER DATABASE CHARACTER SET "utf8";

CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    u VARCHAR(128) NOT NULL UNIQUE,
    pwdhash VARCHAR(128)
);

CREATE TABLE queries (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    q VARCHAR(128) NOT NULL UNIQUE
);

CREATE TABLE videos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    v VARCHAR(11) NOT NULL UNIQUE
);

CREATE TABLE playlists (
    uid INT NOT NULL REFERENCES users(id),
    qid INT NOT NULL REFERENCES queries(id),
    vid INT NOT NULL REFERENCES videos(id),
    PRIMARY KEY (uid,qid,vid) -- PK + find queries by (user) + find videos by (user,tag)
);

CREATE TABLE tmp (
    pk VARCHAR(20) NOT NULL PRIMARY KEY,
    expires DATETIME NOT NULL,
    json VARCHAR(2048) NOT NULL
);
