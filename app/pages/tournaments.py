import streamlit as st
from mysql.connector import Error, IntegrityError

from db import get_connection


def get_games_for_tournament() -> list[dict]:
    """Return game_id and game_name for the tournament Game dropdown."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT game_id, game_name
            FROM games
            ORDER BY game_name
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def add_tournament(
    game_id: int,
    tournament_name: str,
    format_value: str,
    registration_deadline,
    start_date,
    end_date,
    max_teams: int,
    players_per_team: int,
    description: str | None,
) -> tuple[bool, str]:
    """Insert one tournament into the tournaments table. Returns (success, message)."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO tournaments (
                game_id,
                tournament_name,
                format,
                registration_deadline,
                start_date,
                end_date,
                max_teams,
                players_per_team,
                description
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                game_id,
                tournament_name,
                format_value,
                registration_deadline,
                start_date,
                end_date,
                max_teams,
                players_per_team,
                description,
            ),
        )
        connection.commit()
        return True, "Tournament added successfully."
    except IntegrityError as exc:
        return False, f"Database error: {exc}"
    except Error as exc:
        return False, f"Database error: {exc}"
    except Exception as exc:
        return False, f"Could not add tournament: {exc}"
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def get_tournaments() -> list[dict]:
    """Return all tournaments joined with game names."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                t.tournament_id,
                t.tournament_name,
                g.game_name,
                t.format,
                t.status,
                t.start_date,
                t.end_date,
                t.max_teams,
                t.players_per_team
            FROM tournaments t
            JOIN games g ON t.game_id = g.game_id
            ORDER BY t.tournament_id
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# Header
st.title("Tournament Management")
st.write("Create and manage gaming tournaments.")

st.divider()

# Add Tournament Section
st.subheader("Add Tournament")

try:
    games_for_dropdown = get_games_for_tournament()
except Exception as exc:
    games_for_dropdown = []
    st.error(f"Could not load games for the tournament form: {exc}")

if not games_for_dropdown:
    st.info("Add at least one game before creating a tournament.")
else:
    game_name_to_id = {
        game["game_name"]: game["game_id"] for game in games_for_dropdown
    }

    with st.form("add_tournament_form", clear_on_submit=True):
        # Tournament Name - full width
        tournament_name_input = st.text_input("Tournament Name")

        # Game and Format - side by side
        col1, col2 = st.columns(2)
        with col1:
            selected_game_name = st.selectbox("Game", list(game_name_to_id.keys()))
        with col2:
            format_input = st.selectbox(
                "Format",
                ["ROUND_ROBIN", "SINGLE_ELIMINATION"],
            )

        # Registration Deadline and Start Date - side by side
        col3, col4 = st.columns(2)
        with col3:
            registration_deadline_input = st.datetime_input("Registration Deadline")
        with col4:
            start_date_input = st.date_input("Start Date")

        # End Date - full width
        end_date_input = st.date_input("End Date")

        # Maximum Teams and Players Per Team - side by side
        col5, col6 = st.columns(2)
        with col5:
            max_teams_input = st.number_input("Maximum Teams", min_value=1, step=1, value=8)
        with col6:
            players_per_team_input = st.number_input(
                "Players Per Team",
                min_value=1,
                step=1,
                value=1,
            )

        # Description - full width
        tournament_description_input = st.text_area("Description")

        tournament_submitted = st.form_submit_button("Add Tournament")

    if tournament_submitted:
        tournament_name = tournament_name_input.strip()
        game_id = game_name_to_id[selected_game_name]
        description = tournament_description_input.strip() or None
        max_teams = int(max_teams_input)
        players_per_team = int(players_per_team_input)

        if tournament_name == "":
            st.error("Tournament Name cannot be empty.")
        elif end_date_input < start_date_input:
            st.error("End Date cannot be before Start Date.")
        elif max_teams <= 0:
            st.error("Maximum Teams must be greater than 0.")
        elif players_per_team <= 0:
            st.error("Players Per Team must be greater than 0.")
        else:
            success, message = add_tournament(
                game_id,
                tournament_name,
                format_input,
                registration_deadline_input,
                start_date_input,
                end_date_input,
                max_teams,
                players_per_team,
                description,
            )
            if success:
                st.success(message)
            else:
                st.error(message)

st.divider()

# All Tournaments Section
st.subheader("All Tournaments")

try:
    tournaments = get_tournaments()
    if tournaments:
        st.table(tournaments)
    else:
        st.info("No tournaments have been added yet.")
except Exception as exc:
    st.error(f"Could not load tournaments: {exc}")
