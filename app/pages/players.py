import streamlit as st
from mysql.connector import Error, IntegrityError

from db import get_connection


def add_player(
    full_name: str,
    username: str,
    email: str,
    gamertag: str,
) -> tuple[bool, str]:
    """Insert a user and a matching player in one transaction."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

        user_query = """
            INSERT INTO users (username, email, password_hash, full_name, role)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(
            user_query,
            (username, email, "TEMP_PASSWORD", full_name, "PLAYER"),
        )
        user_id = cursor.lastrowid

        player_query = """
            INSERT INTO players (user_id, gamertag)
            VALUES (%s, %s)
        """
        cursor.execute(player_query, (user_id, gamertag))
        connection.commit()
        return True, "Player added successfully."
    except IntegrityError as exc:
        if connection is not None:
            connection.rollback()
        error_text = str(exc).lower()
        if "username" in error_text:
            return False, "This username is already taken."
        if "email" in error_text:
            return False, "This email is already registered."
        if "gamertag" in error_text:
            return False, "This gamertag is already taken."
        return False, "This player could not be added because a unique value already exists."
    except Error as exc:
        if connection is not None:
            connection.rollback()
        return False, f"Database error: {exc}"
    except Exception as exc:
        if connection is not None:
            connection.rollback()
        return False, f"Could not add player: {exc}"
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def get_players() -> list[dict]:
    """Return all players joined with their user account details."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                p.player_id,
                u.full_name,
                u.username,
                u.email,
                p.gamertag,
                p.created_at
            FROM players p
            JOIN users u ON p.user_id = u.user_id
            ORDER BY p.player_id
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# Header
st.title("Player Management")
st.write("Add and manage players participating in your gaming tournaments.")

st.divider()

# Add Player Section
st.subheader("Add Player")

with st.form("add_player_form", clear_on_submit=True):
    # Full Name - full width
    full_name_input = st.text_input("Full Name")

    # Username and Email - side by side
    col1, col2 = st.columns(2)
    with col1:
        username_input = st.text_input("Username")
    with col2:
        email_input = st.text_input("Email")

    # Gamertag - full width
    gamertag_input = st.text_input("Gamertag")

    player_submitted = st.form_submit_button("Add Player")

if player_submitted:
    full_name = full_name_input.strip()
    username = username_input.strip()
    email = email_input.strip()
    gamertag = gamertag_input.strip()

    if full_name == "":
        st.error("Full Name cannot be empty.")
    elif username == "":
        st.error("Username cannot be empty.")
    elif email == "":
        st.error("Email cannot be empty.")
    elif gamertag == "":
        st.error("Gamertag cannot be empty.")
    else:
        success, message = add_player(full_name, username, email, gamertag)
        if success:
            st.success(message)
        else:
            st.error(message)

st.divider()

# All Players Section
st.subheader("All Players")

try:
    players = get_players()
    if players:
        st.table(players)
    else:
        st.info("No players have been added yet.")
except Exception as exc:
    st.error(f"Could not load players: {exc}")
