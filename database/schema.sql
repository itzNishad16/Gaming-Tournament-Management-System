-- ============================================================
-- Gaming Tournament Management System
-- Database: gaming_tournament_db
-- ============================================================

CREATE DATABASE IF NOT EXISTS gaming_tournament_db;

USE gaming_tournament_db;


-- ============================================================
-- 1. USERS
-- Stores login accounts for administrators and players.
-- ============================================================

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('ADMIN', 'PLAYER') NOT NULL DEFAULT 'PLAYER',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 2. PLAYERS
-- Each player is linked to exactly one user account.
-- ============================================================

CREATE TABLE players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    gamertag VARCHAR(50) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_players_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
);


-- ============================================================
-- 3. GAMES
-- Catalog of games for which tournaments can be created.
-- ============================================================

CREATE TABLE games (
    game_id INT AUTO_INCREMENT PRIMARY KEY,
    game_name VARCHAR(100) NOT NULL UNIQUE,
    genre VARCHAR(50),
    description TEXT
);


-- ============================================================
-- 4. TOURNAMENTS
-- Stores tournament information and configuration.
-- ============================================================

CREATE TABLE tournaments (
    tournament_id INT AUTO_INCREMENT PRIMARY KEY,
    game_id INT NOT NULL,
    tournament_name VARCHAR(150) NOT NULL,

    format ENUM(
        'ROUND_ROBIN',
        'SINGLE_ELIMINATION'
    ) NOT NULL,

    status ENUM(
        'UPCOMING',
        'ONGOING',
        'COMPLETED'
    ) NOT NULL DEFAULT 'UPCOMING',

    registration_deadline DATETIME NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    max_teams INT NOT NULL,
    players_per_team INT NOT NULL,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_tournaments_game
        FOREIGN KEY (game_id) REFERENCES games(game_id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_tournament_dates
        CHECK (end_date >= start_date),

    CONSTRAINT chk_tournament_max_teams
        CHECK (max_teams > 0),

    CONSTRAINT chk_tournament_players_per_team
        CHECK (players_per_team > 0)
);


-- ============================================================
-- 5. TEAMS
-- Each team belongs to one tournament.
-- ============================================================

CREATE TABLE teams (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    tournament_id INT NOT NULL,
    team_name VARCHAR(100) NOT NULL,
    captain_id INT NOT NULL,

    status ENUM(
        'REGISTERED',
        'ACTIVE',
        'ELIMINATED'
    ) NOT NULL DEFAULT 'REGISTERED',

    registered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_teams_tournament
        FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_teams_captain
        FOREIGN KEY (captain_id) REFERENCES players(player_id)
        ON DELETE RESTRICT,

    CONSTRAINT uq_teams_tournament_name
        UNIQUE (tournament_id, team_name)
);


-- ============================================================
-- 6. TEAM_MEMBERS
-- Junction table connecting players with teams.
-- ============================================================

CREATE TABLE team_members (
    team_member_id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT NOT NULL,
    player_id INT NOT NULL,
    joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_team_members_team
        FOREIGN KEY (team_id) REFERENCES teams(team_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_team_members_player
        FOREIGN KEY (player_id) REFERENCES players(player_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_team_members_team_player
        UNIQUE (team_id, player_id)
);


-- ============================================================
-- 7. MATCHES
-- Stores matches between two teams in a tournament.
-- ============================================================

CREATE TABLE matches (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    tournament_id INT NOT NULL,
    team1_id INT NOT NULL,
    team2_id INT NOT NULL,
    scheduled_at DATETIME NOT NULL,

    status ENUM(
        'SCHEDULED',
        'LIVE',
        'COMPLETED'
    ) NOT NULL DEFAULT 'SCHEDULED',

    round_number INT NOT NULL DEFAULT 1,

    CONSTRAINT fk_matches_tournament
        FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_matches_team1
        FOREIGN KEY (team1_id) REFERENCES teams(team_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_matches_team2
        FOREIGN KEY (team2_id) REFERENCES teams(team_id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_matches_different_teams
        CHECK (team1_id <> team2_id)
);


-- ============================================================
-- 8. MATCH_RESULTS
-- Stores the result of a completed match.
-- ============================================================

CREATE TABLE match_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL UNIQUE,
    winner_team_id INT NOT NULL,
    team1_score INT NOT NULL DEFAULT 0,
    team2_score INT NOT NULL DEFAULT 0,
    completed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_match_results_match
        FOREIGN KEY (match_id) REFERENCES matches(match_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_match_results_winner
        FOREIGN KEY (winner_team_id) REFERENCES teams(team_id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_match_results_scores
        CHECK (team1_score >= 0 AND team2_score >= 0)
);