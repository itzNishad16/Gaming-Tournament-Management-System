import streamlit as st
from mysql.connector import Error, IntegrityError

from db import get_connection


def add_game(game_name: str, genre: str | None, description: str | None) -> tuple[bool, str]:
    """Insert one game into the games table. Returns (success, message)."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO games (game_name, genre, description)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (game_name, genre, description))
        connection.commit()
        return True, "Game added successfully."
    except IntegrityError:
        return False, "A game with this name already exists."
    except Error as exc:
        return False, f"Database error: {exc}"
    except Exception as exc:
        return False, f"Could not add game: {exc}"
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def get_games() -> list[dict]:
    """Return all games from the games table."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT game_id, game_name, genre, description
            FROM games
            ORDER BY game_id
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def delete_game(game_id: int) -> tuple[bool, str]:
    """Delete one game from the games table. Returns (success, message)."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "DELETE FROM games WHERE game_id = %s"
        cursor.execute(query, (game_id,))
        connection.commit()
        if cursor.rowcount == 0:
            return False, "Game was not found."
        return True, "Game deleted successfully."
    except IntegrityError:
        if connection is not None:
            connection.rollback()
        return False, "This game cannot be deleted because it is used by an existing tournament."
    except Error as exc:
        if connection is not None:
            connection.rollback()
        return False, f"Database error: {exc}"
    except Exception as exc:
        if connection is not None:
            connection.rollback()
        return False, f"Could not delete game: {exc}"
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# Header
st.title("Game Management")
st.write("Add and manage the games used in your tournaments.")

st.divider()

# Add Game Section
st.subheader("Add Game")

with st.form("add_game_form", clear_on_submit=True):
    game_name_input = st.text_input("Game Name")
    genre_input = st.text_input("Genre")
    description_input = st.text_area("Description")
    submitted = st.form_submit_button("Add Game")

if submitted:
    game_name = game_name_input.strip()
    genre = genre_input.strip() or None
    description = description_input.strip() or None

    if game_name == "":
        st.error("Game Name cannot be empty.")
    else:
        success, message = add_game(game_name, genre, description)
        if success:
            st.success(message)
        else:
            st.error(message)

st.divider()

# All Games Section
st.subheader("All Games")

games = []
try:
    games = get_games()
    if games:
        st.table(games)
    else:
        st.info("No games have been added yet.")
except Exception as exc:
    st.error(f"Could not load games: {exc}")

st.divider()

# Delete Game Section
st.subheader("Delete Game")

delete_message = st.session_state.pop("game_delete_msg", None)
if delete_message:
    st.success(delete_message)

if games:
    game_name_to_id = {game["game_name"]: game["game_id"] for game in games}
    selected_game_name = st.selectbox(
        "Select a game to delete",
        list(game_name_to_id.keys()),
    )
    if st.button("Delete Game"):
        game_id = game_name_to_id[selected_game_name]
        success, message = delete_game(game_id)
        if success:
            st.session_state["game_delete_msg"] = message
            st.rerun()
        else:
            st.error(message)
else:
    st.info("No games available to delete.")
