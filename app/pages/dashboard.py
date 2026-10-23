import streamlit as st

from db import get_connection

ALLOWED_TABLES = (
    "games",
    "tournaments",
    "players",
    "teams",
    "matches",
    "match_results",
)


def get_count(table_name: str) -> int:
    """Return how many rows are in the given table."""
    if table_name not in ALLOWED_TABLES:
        raise ValueError("This table is not allowed for counting.")

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = f"SELECT COUNT(*) FROM {table_name}"
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0]
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def get_recent_tournaments() -> list[dict]:
    """Return the latest 5 tournaments with game name, format, and status."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                t.tournament_name,
                g.game_name,
                t.format,
                t.status
            FROM tournaments t
            JOIN games g ON t.game_id = g.game_id
            ORDER BY t.tournament_id DESC
            LIMIT 5
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def get_recent_matches() -> list[dict]:
    """Return the latest 5 matches with tournament, teams, time, and status."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                tr.tournament_name,
                t1.team_name AS team1_name,
                t2.team_name AS team2_name,
                m.scheduled_at,
                m.status
            FROM matches m
            JOIN tournaments tr
                ON m.tournament_id = tr.tournament_id
            JOIN teams t1
                ON m.team1_id = t1.team_id
            JOIN teams t2
                ON m.team2_id = t2.team_id
            ORDER BY m.match_id DESC
            LIMIT 5
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def get_player_tournaments() -> list[dict]:
    """Return all tournaments with game details for player view."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                t.tournament_name,
                g.game_name,
                t.format,
                t.status,
                t.start_date,
                t.end_date
            FROM tournaments t
            JOIN games g ON t.game_id = g.game_id
            ORDER BY t.start_date DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def get_player_matches() -> list[dict]:
    """Return recent matches with tournament and team details for player view."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                tr.tournament_name,
                t1.team_name AS team1_name,
                t2.team_name AS team2_name,
                m.scheduled_at,
                m.status
            FROM matches m
            JOIN tournaments tr
                ON m.tournament_id = tr.tournament_id
            JOIN teams t1
                ON m.team1_id = t1.team_id
            JOIN teams t2
                ON m.team2_id = t2.team_id
            ORDER BY m.scheduled_at DESC
            LIMIT 10
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def get_player_results() -> list[dict]:
    """Return recent match results with tournament and team details for player view."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                tr.tournament_name,
                t1.team_name AS team1_name,
                t2.team_name AS team2_name,
                r.team1_score,
                r.team2_score,
                w.team_name AS winner_name,
                r.completed_at
            FROM match_results r
            JOIN matches m
                ON r.match_id = m.match_id
            JOIN tournaments tr
                ON m.tournament_id = tr.tournament_id
            JOIN teams t1
                ON m.team1_id = t1.team_id
            JOIN teams t2
                ON m.team2_id = t2.team_id
            JOIN teams w
                ON r.winner_team_id = w.team_id
            ORDER BY r.completed_at DESC
            LIMIT 10
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# Get current user role
user_role = st.session_state.get("user_role")

# ADMIN DASHBOARD
if user_role == "ADMIN":
    st.title("Dashboard")
    st.write("Gaming Tournament Manager overview")

    st.divider()

    # Overview Section
    st.subheader("Overview")

    try:
        games = get_count("games")
        tournaments = get_count("tournaments")
        players = get_count("players")
        teams = get_count("teams")
        matches = get_count("matches")
        results = get_count("match_results")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Games", games)
        with col2:
            st.metric("Tournaments", tournaments)
        with col3:
            st.metric("Players", players)

        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("Teams", teams)
        with col5:
            st.metric("Matches", matches)
        with col6:
            st.metric("Results", results)
    except Exception as exc:
        st.error(f"Could not load dashboard counts: {exc}")

    st.divider()

    # Quick Actions Section
    st.subheader("Quick Actions")

    col_action1, col_action2, col_action3, col_action4 = st.columns(4)

    with col_action1:
        if st.button("Add Game", use_container_width=True):
            st.switch_page("pages/games.py")

    with col_action2:
        if st.button("Add Tournament", use_container_width=True):
            st.switch_page("pages/tournaments.py")

    with col_action3:
        if st.button("Add Player", use_container_width=True):
            st.switch_page("pages/players.py")

    with col_action4:
        if st.button("Add Team", use_container_width=True):
            st.switch_page("pages/teams.py")

    st.divider()

    # Recent Tournaments Section
    st.subheader("Recent Tournaments")

    try:
        recent_tournaments = get_recent_tournaments()
        if recent_tournaments:
            st.table(recent_tournaments)
        else:
            st.info("No tournaments have been added yet.")
    except Exception as exc:
        st.error(f"Could not load recent tournaments: {exc}")

    st.divider()

    # Recent Matches Section
    st.subheader("Recent Matches")

    try:
        recent_matches = get_recent_matches()
        if recent_matches:
            st.table(recent_matches)
        else:
            st.info("No matches have been added yet.")
    except Exception as exc:
        st.error(f"Could not load recent matches: {exc}")

# PLAYER DASHBOARD
elif user_role == "PLAYER":
    st.title("Player Dashboard")
    st.write("View tournaments, matches and results.")

    st.divider()

    # Overview Section
    st.subheader("Overview")

    try:
        games = get_count("games")
        tournaments = get_count("tournaments")
        matches = get_count("matches")
        results = get_count("match_results")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Available Games", games)
        with col2:
            st.metric("Tournaments", tournaments)
        with col3:
            st.metric("Matches", matches)
        with col4:
            st.metric("Results", results)
    except Exception as exc:
        st.error(f"Could not load dashboard counts: {exc}")

    st.divider()

    # Available Tournaments Section
    st.subheader("Available Tournaments")

    try:
        player_tournaments = get_player_tournaments()
        if player_tournaments:
            st.table(player_tournaments)
        else:
            st.info("No tournaments available.")
    except Exception as exc:
        st.error(f"Could not load tournaments: {exc}")

    st.divider()

    # Recent Matches Section
    st.subheader("Recent Matches")

    try:
        player_matches = get_player_matches()
        if player_matches:
            st.table(player_matches)
        else:
            st.info("No matches scheduled.")
    except Exception as exc:
        st.error(f"Could not load matches: {exc}")

    st.divider()

    # Recent Results Section
    st.subheader("Recent Results")

    try:
        player_results = get_player_results()
        if player_results:
            st.table(player_results)
        else:
            st.info("No results available.")
    except Exception as exc:
        st.error(f"Could not load results: {exc}")

# Fallback for unauthorized access
else:
    st.title("Access Denied")
    st.write("Please log in to access the dashboard.")
    st.info("Use the Login page to authenticate.")
