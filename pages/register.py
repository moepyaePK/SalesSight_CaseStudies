import streamlit as st
from auth import register_user

st.title("📝 Register New Account")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Register"):
    if username and password:
        success = register_user(username, password)
        if success:
            st.success("✅ Registration successful! Please log in.")
            st.switch_page("pages/login.py")
        else:
            st.error("⚠️ Username already exists or database error.")
    else:
        st.warning("Please fill in both fields.")
