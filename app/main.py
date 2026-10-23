import streamlit as st

from auth import is_logged_in, is_admin, is_player, logout_user, get_current_user_role

st.set_page_config(
    page_title="Gaming Tournament Manager",
    page_icon="🎮",
)

st.sidebar.title("🎮 Gaming Tournament Manager")

# Initialize session state if not exists
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "full_name" not in st.session_state:
    st.session_state.full_name = None

# Show logout button if logged in
if is_logged_in():
    user_info = f"{st.session_state.full_name} ({st.session_state.user_role})"
    st.sidebar.write(f"Logged in as: {user_info}")
    if st.sidebar.button("Logout"):
        logout_user()
        st.rerun()

# Determine which pages to show based on authentication status
if not is_logged_in():
    # Not logged in - show only login page
    pages = {
        "AUTH": [
            st.Page("pages/login.py", title="Login", icon="🔑", default=True),
        ],
    }
elif is_admin():
    # Admin - show all pages
    pages = {
        "MAIN": [
            st.Page("pages/dashboard.py", title="Dashboard", icon="📊", default=True),
        ],
        "MANAGEMENT": [
            st.Page("pages/games.py", title="Games", icon="🎮"),
            st.Page("pages/tournaments.py", title="Tournaments", icon="🏆"),
            st.Page("pages/players.py", title="Players", icon="👤"),
            st.Page("pages/teams.py", title="Teams", icon="👥"),
            st.Page("pages/6_Team_Members.py", title="Team Members", icon="🔗"),
        ],
        "COMPETITION": [
            st.Page("pages/7_Matches.py", title="Matches", icon="⚔️"),
            st.Page("pages/8_Results.py", title="Results", icon="🏅"),
        ],
    }
elif is_player():
    # Player - show only dashboard for now
    pages = {
        "MAIN": [
            st.Page("pages/dashboard.py", title="Dashboard", icon="📊", default=True),
        ],
    }
else:
    # Fallback - show login page
    pages = {
        "AUTH": [
            st.Page("pages/login.py", title="Login", icon="🔑", default=True),
        ],
    }

pg = st.navigation(pages)
pg.run()
