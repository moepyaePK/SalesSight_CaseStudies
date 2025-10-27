import streamlit as st
from db import create_users_table, add_user, get_user

# Ensure table exists
create_users_table()

def register_user(username, password):
    try:
        add_user(username, password)
        return True
    except Exception as e:
        print("Error:", e)
        return False

def verify_user(username, password):
    user = get_user(username, password)
    if user:
        # ✅ Save session state
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        return True
    return False

def is_logged_in():
    return st.session_state.get("logged_in", False)

def logout():
    for key in ("logged_in", "username", "save_path"):
        st.session_state.pop(key, None)
