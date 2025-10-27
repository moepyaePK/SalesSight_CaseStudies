import streamlit as st
from auth import verify_user

st.title("🔑 Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if verify_user(username, password):
        st.session_state["user"] = username
        st.success("Login successful!")
        st.switch_page("pages/data_upload.py")
    else:
        st.error("Invalid username or password.")

