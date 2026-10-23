import streamlit as st
from mysql.connector import Error, IntegrityError

from db import get_connection


def get_matches_for_result() -> list[dict]:
    """Return matches with tournament and team names for the Match dropdown."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                m.match_id,
                m.team1_id,
                m.team2_id,
                tr.tournament_name,
                t1.team_name AS team1_name,
                t2.team_name AS team2_name
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


def add_result(
    match_id: int,
    winner_team_id: int,
    team1_score: int,
    team2_score: int,
) -> tuple[bool, str]:
    """Insert one row into match_results. Returns (success, message)."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO match_results (
                match_id,
                winner_team_id,
                team1_score,
                team2_score
            )
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (match_id, winner_team_id, team1_score, team2_score),
        )
        connection.commit()
        return True, "Match result added successfully."
    except IntegrityError:
        if connection is not None:
            connection.rollback()
        return False, "A result for this match already exists."
    except Error as exc:
        if connection is not None:
            connection.rollback()
        return False, f"Database error: {exc}"
    except Exception as exc:
        if connection is not None:
            connection.rollback()
        return False, f"Could not add result: {exc}"
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def get_results() -> list[dict]:
    """Return all match results joined with tournament, team, and winner names."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                r.result_id,
                r.match_id,
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
            ORDER BY r.result_id
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# Header
st.title("Result Management")
st.write("Record and view results for completed tournament matches.")

st.divider()

# Add Result Section
st.subheader("Add Result")

try:
    matches_for_result = get_matches_for_result()
except Exception as exc:
    matches_for_result = []
    st.error(f"Could not load matches: {exc}")

if not matches_for_result:
    st.info("Add at least one match before recording a result.")
else:
    match_label_to_match = {}
    for match in matches_for_result:
        label = (
            f"{match['tournament_name']} - "
            f"{match['team1_name']} vs {match['team2_name']} - "
            f"Match {match['match_id']}"
        )
        match_label_to_match[label] = match

    selected_match_label = st.selectbox("Match", list(match_label_to_match.keys()))
    selected_match = match_label_to_match[selected_match_label]

    winner_label_to_id = {
        selected_match["team1_name"]: selected_match["team1_id"],
        selected_match["team2_name"]: selected_match["team2_id"],
    }

    with st.form("add_result_form", clear_on_submit=True):
        # Winner - full width
        selected_winner_name = st.selectbox("Winner", list(winner_label_to_id.keys()))

        # Team 1 Score and Team 2 Score - side by side
        col1, col2 = st.columns(2)
        with col1:
            team1_score_input = st.number_input(
                "Team 1 Score",
                min_value=0,
                step=1,
                value=0,
            )
        with col2:
            team2_score_input = st.number_input(
                "Team 2 Score",
                min_value=0,
                step=1,
                value=0,
            )

        result_submitted = st.form_submit_button("Add Result")

    if result_submitted:
        match_id = selected_match["match_id"]
        winner_team_id = winner_label_to_id[selected_winner_name]
        team1_score = int(team1_score_input)
        team2_score = int(team2_score_input)

        if winner_team_id not in (selected_match["team1_id"], selected_match["team2_id"]):
            st.error("The winner must be one of the two teams in this match.")
        elif team1_score < 0 or team2_score < 0:
            st.error("Scores cannot be negative.")
        else:
            success, message = add_result(
                match_id,
                winner_team_id,
                team1_score,
                team2_score,
            )
            if success:
                st.success(message)
            else:
                st.error(message)

st.divider()

# All Results Section
st.subheader("All Results")

try:
    results = get_results()
    if results:
        st.table(results)
    else:
        st.info("No results have been added yet.")
except Exception as exc:
    st.error(f"Could not load results: {exc}")
