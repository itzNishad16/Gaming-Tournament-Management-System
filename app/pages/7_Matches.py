import streamlit as st
from mysql.connector import Error, IntegrityError

from db import get_connection


def get_tournaments_for_match() -> list[dict]:
    """Return tournament_id and tournament_name for the Tournament dropdown."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT tournament_id, tournament_name
            FROM tournaments
            ORDER BY tournament_name
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def get_teams_for_match(tournament_id: int) -> list[dict]:
    """Return teams that belong to the selected tournament."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT team_id, team_name
            FROM teams
            WHERE tournament_id = %s
            ORDER BY team_name
        """
        cursor.execute(query, (tournament_id,))
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def add_match(
    tournament_id: int,
    team1_id: int,
    team2_id: int,
    scheduled_at,
    round_number: int,
    status: str,
) -> tuple[bool, str]:
    """Insert one match into the matches table. Returns (success, message)."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO matches (
                tournament_id,
                team1_id,
                team2_id,
                scheduled_at,
                round_number,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (tournament_id, team1_id, team2_id, scheduled_at, round_number, status),
        )
        connection.commit()
        return True, "Match added successfully."
    except IntegrityError:
        if connection is not None:
            connection.rollback()
        return False, "This match could not be added. Check that both teams belong to the tournament."
    except Error as exc:
        if connection is not None:
            connection.rollback()
        return False, f"Database error: {exc}"
    except Exception as exc:
        if connection is not None:
            connection.rollback()
        return False, f"Could not add match: {exc}"
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def get_matches() -> list[dict]:
    """Return all matches joined with tournament and team names."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                m.match_id,
                tr.tournament_name,
                t1.team_name AS team1_name,
                t2.team_name AS team2_name,
                m.scheduled_at,
                m.round_number,
                m.status
            FROM matches m
            JOIN tournaments tr
                ON m.tournament_id = tr.tournament_id
            JOIN teams t1
                ON m.team1_id = t1.team_id
            JOIN teams t2
                ON m.team2_id = t2.team_id
            ORDER BY m.match_id
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# Header
st.title("Match Management")
st.write("Schedule and manage matches between tournament teams.")

st.divider()

# Add Match Section
st.subheader("Add Match")

try:
    tournaments_for_match = get_tournaments_for_match()
except Exception as exc:
    tournaments_for_match = []
    st.error(f"Could not load tournaments: {exc}")

if not tournaments_for_match:
    st.info("Add at least one tournament before creating a match.")
else:
    tournament_name_to_id = {
        tournament["tournament_name"]: tournament["tournament_id"]
        for tournament in tournaments_for_match
    }
    selected_tournament_name = st.selectbox(
        "Tournament",
        list(tournament_name_to_id.keys()),
    )
    tournament_id = tournament_name_to_id[selected_tournament_name]

    try:
        teams_for_match = get_teams_for_match(tournament_id)
    except Exception as exc:
        teams_for_match = []
        st.error(f"Could not load teams: {exc}")

    if len(teams_for_match) < 2:
        st.info("Add at least two teams in this tournament before creating a match.")
    else:
        team_name_to_id = {
            team["team_name"]: team["team_id"] for team in teams_for_match
        }
        team_names = list(team_name_to_id.keys())

        with st.form("add_match_form", clear_on_submit=True):
            # Team 1 and Team 2 - side by side
            col1, col2 = st.columns(2)
            with col1:
                selected_team1_name = st.selectbox("Team 1", team_names)
            with col2:
                selected_team2_name = st.selectbox("Team 2", team_names)

            # Scheduled Date and Time - full width
            scheduled_at_input = st.datetime_input("Scheduled Date and Time")

            # Round and Status - side by side
            col3, col4 = st.columns(2)
            with col3:
                round_number_input = st.number_input("Round", min_value=1, step=1, value=1)
            with col4:
                status_input = st.selectbox(
                    "Status",
                    ["SCHEDULED", "LIVE", "COMPLETED"],
                )

            match_submitted = st.form_submit_button("Add Match")

        if match_submitted:
            team1_id = team_name_to_id[selected_team1_name]
            team2_id = team_name_to_id[selected_team2_name]
            round_number = int(round_number_input)

            if team1_id == team2_id:
                st.error("Team 1 and Team 2 cannot be the same.")
            elif round_number <= 0:
                st.error("Round must be greater than 0.")
            else:
                success, message = add_match(
                    tournament_id,
                    team1_id,
                    team2_id,
                    scheduled_at_input,
                    round_number,
                    status_input,
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)

st.divider()

# All Matches Section
st.subheader("All Matches")

try:
    matches = get_matches()
    if matches:
        st.table(matches)
    else:
        st.info("No matches have been added yet.")
except Exception as exc:
    st.error(f"Could not load matches: {exc}")
