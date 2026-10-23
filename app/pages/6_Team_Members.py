import streamlit as st
from mysql.connector import Error, IntegrityError

from db import get_connection


def get_teams_for_members() -> list[dict]:
    """Return team_id, team_name, and tournament_name for the Team dropdown."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                t.team_id,
                t.team_name,
                tr.tournament_name
            FROM teams t
            JOIN tournaments tr
                ON t.tournament_id = tr.tournament_id
            ORDER BY tr.tournament_name, t.team_name
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def get_players_for_members() -> list[dict]:
    """Return player_id, gamertag, and full_name for the Player dropdown."""
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


def add_team_member(team_id: int, player_id: int) -> tuple[bool, str]:
    """Insert one player into a team. Returns (success, message)."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO team_members (team_id, player_id)
            VALUES (%s, %s)
        """
        cursor.execute(query, (team_id, player_id))
        connection.commit()
        return True, "Team member added successfully."
    except IntegrityError:
        if connection is not None:
            connection.rollback()
        return False, "This player is already a member of the selected team."
    except Error as exc:
        if connection is not None:
            connection.rollback()
        return False, f"Database error: {exc}"
    except Exception as exc:
        if connection is not None:
            connection.rollback()
        return False, f"Could not add team member: {exc}"
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def get_team_members() -> list[dict]:
    """Return all team members joined with team, tournament, and player details."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                tm.team_member_id,
                t.team_name,
                tr.tournament_name,
                u.full_name,
                p.gamertag,
                tm.joined_at
            FROM team_members tm
            JOIN teams t
                ON tm.team_id = t.team_id
            JOIN tournaments tr
                ON t.tournament_id = tr.tournament_id
            JOIN players p
                ON tm.player_id = p.player_id
            JOIN users u
                ON p.user_id = u.user_id
            ORDER BY tm.team_member_id
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# Header
st.title("Team Members")
st.write("Assign players to teams and manage team composition.")

st.divider()

# Add Team Member Section
st.subheader("Assign Player to Team")

try:
    teams_for_members = get_teams_for_members()
    players_for_members = get_players_for_members()
except Exception as exc:
    teams_for_members = []
    players_for_members = []
    st.error(f"Could not load data for the team member form: {exc}")

if not teams_for_members:
    st.info("Add at least one team before adding team members.")
elif not players_for_members:
    st.info("Add at least one player before adding team members.")
else:
    team_label_to_id = {
        f"{team['team_name']} ({team['tournament_name']})": team["team_id"]
        for team in teams_for_members
    }
    player_label_to_id = {
        f"{player['full_name']} ({player['gamertag']})": player["player_id"]
        for player in players_for_members
    }

    with st.form("add_team_member_form", clear_on_submit=True):
        # Team and Player - side by side
        col1, col2 = st.columns(2)
        with col1:
            selected_team_label = st.selectbox("Team", list(team_label_to_id.keys()))
        with col2:
            selected_player_label = st.selectbox("Player", list(player_label_to_id.keys()))

        member_submitted = st.form_submit_button("Add Member")

    if member_submitted:
        team_id = team_label_to_id[selected_team_label]
        player_id = player_label_to_id[selected_player_label]
        success, message = add_team_member(team_id, player_id)
        if success:
            st.success(message)
        else:
            st.error(message)

st.divider()

# Current Team Members Section
st.subheader("Current Team Members")

try:
    team_members = get_team_members()
    if team_members:
        st.table(team_members)
    else:
        st.info("No team members have been added yet.")
except Exception as exc:
    st.error(f"Could not load team members: {exc}")
