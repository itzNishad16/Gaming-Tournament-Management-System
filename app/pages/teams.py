import streamlit as st
from mysql.connector import Error, IntegrityError

from db import get_connection


def get_tournaments_for_team() -> list[dict]:
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


def get_players_for_team() -> list[dict]:
    """Return player_id, gamertag, and full_name for the Captain dropdown."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                p.player_id,
                p.gamertag,
                u.full_name
            FROM players p
            JOIN users u ON p.user_id = u.user_id
            ORDER BY u.full_name, p.gamertag
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def add_team(tournament_id: int, team_name: str, captain_id: int) -> tuple[bool, str]:
    """Insert one team into the teams table. Returns (success, message)."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO teams (tournament_id, team_name, captain_id)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (tournament_id, team_name, captain_id))
        connection.commit()
        return True, "Team added successfully."
    except IntegrityError:
        return False, "A team with this name already exists in the selected tournament."
    except Error as exc:
        return False, f"Database error: {exc}"
    except Exception as exc:
        return False, f"Could not add team: {exc}"
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def get_teams() -> list[dict]:
    """Return all teams joined with tournament and captain details."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                t.team_id,
                t.team_name,
                tr.tournament_name,
                u.full_name AS captain_name,
                p.gamertag,
                t.status,
                t.registered_at
            FROM teams t
            JOIN tournaments tr
                ON t.tournament_id = tr.tournament_id
            JOIN players p
                ON t.captain_id = p.player_id
            JOIN users u
                ON p.user_id = u.user_id
            ORDER BY t.team_id
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# Header
st.title("Team Management")
st.write("Create and manage teams for your gaming tournaments.")

st.divider()

# Add Team Section
st.subheader("Add Team")

try:
    tournaments_for_team = get_tournaments_for_team()
    players_for_team = get_players_for_team()
except Exception as exc:
    tournaments_for_team = []
    players_for_team = []
    st.error(f"Could not load data for the team form: {exc}")

if not tournaments_for_team:
    st.info("Add at least one tournament before creating a team.")
elif not players_for_team:
    st.info("Add at least one player before creating a team.")
else:
    tournament_name_to_id = {
        tournament["tournament_name"]: tournament["tournament_id"]
        for tournament in tournaments_for_team
    }
    captain_label_to_id = {
        f"{player['full_name']} ({player['gamertag']})": player["player_id"]
        for player in players_for_team
    }

    with st.form("add_team_form", clear_on_submit=True):
        # Team Name - full width
        team_name_input = st.text_input("Team Name")

        # Tournament and Captain - side by side
        col1, col2 = st.columns(2)
        with col1:
            selected_tournament_name = st.selectbox(
                "Tournament",
                list(tournament_name_to_id.keys()),
            )
        with col2:
            selected_captain_label = st.selectbox(
                "Captain",
                list(captain_label_to_id.keys()),
            )

        team_submitted = st.form_submit_button("Add Team")

    if team_submitted:
        team_name = team_name_input.strip()
        tournament_id = tournament_name_to_id[selected_tournament_name]
        captain_id = captain_label_to_id[selected_captain_label]

        if team_name == "":
            st.error("Team Name cannot be empty.")
        else:
            success, message = add_team(tournament_id, team_name, captain_id)
            if success:
                st.success(message)
            else:
                st.error(message)

st.divider()

# All Teams Section
st.subheader("All Teams")

try:
    teams = get_teams()
    if teams:
        st.table(teams)
    else:
        st.info("No teams have been added yet.")
except Exception as exc:
    st.error(f"Could not load teams: {exc}")
