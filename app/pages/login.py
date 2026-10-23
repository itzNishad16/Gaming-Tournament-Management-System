import streamlit as st

from auth import login_user


st.title("Login")
st.write("Enter your credentials to access the Gaming Tournament Manager.")

st.divider()

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

# If already logged in, show message and redirect option
if st.session_state.logged_in:
    st.success(f"Welcome, {st.session_state.full_name}!")
    st.info("You are already logged in. Use the Logout button in the sidebar to log out.")
else:
    with st.form("login_form"):
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        username = username_input.strip()
        password = password_input.strip()

        if username == "":
            st.error("Username cannot be empty.")
        elif password == "":
            st.error("Password cannot be empty.")
        else:
            success, message = login_user(username, password)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

st.divider()

st.info("Note: For this demo, passwords are stored as plain text. In production, use proper password hashing.")
