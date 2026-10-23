import streamlit as st
from mysql.connector import Error

from db import get_connection


def get_user_by_username(username: str) -> dict | None:
    """Return user data for the given username, or None if not found."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT user_id, username, email, password_hash, full_name, role
            FROM users
            WHERE username = %s
        """
        cursor.execute(query, (username,))
        return cursor.fetchone()
    except Error as exc:
        st.error(f"Database error: {exc}")
        return None
    except Exception as exc:
        st.error(f"Could not fetch user: {exc}")
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def verify_password(input_password: str, stored_hash: str) -> bool:
    """Verify if the input password matches the stored hash.
    
    For simplicity in this beginner-friendly implementation,
    we compare plain text passwords. In production, use proper hashing.
    """
    return input_password == stored_hash


def login_user(username: str, password: str) -> tuple[bool, str]:
    """Attempt to log in a user. Returns (success, message)."""
    user = get_user_by_username(username)
    
    if user is None:
        return False, "User not found."
    
    if verify_password(password, user["password_hash"]):
        # Store user info in session state
        st.session_state.logged_in = True
        st.session_state.user_id = user["user_id"]
        st.session_state.username = user["username"]
        st.session_state.user_role = user["role"]
        st.session_state.full_name = user["full_name"]
        return True, "Login successful."
    else:
        return False, "Incorrect password."


def logout_user():
    """Clear the user session and redirect to login."""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.user_role = None
    st.session_state.full_name = None


def is_logged_in() -> bool:
    """Check if a user is currently logged in."""
    return st.session_state.get("logged_in", False)


def get_current_user_role() -> str | None:
    """Get the current user's role."""
    return st.session_state.get("user_role")


def is_admin() -> bool:
    """Check if the current user is an admin."""
    return get_current_user_role() == "ADMIN"


def is_player() -> bool:
    """Check if the current user is a player."""
    return get_current_user_role() == "PLAYER"
