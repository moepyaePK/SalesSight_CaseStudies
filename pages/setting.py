import streamlit as st
from utils import add_sidebar_logo
from auth import is_logged_in


if not is_logged_in():
    st.warning("⚠️ Please login to continue.")
    st.switch_page("Home.py")
    st.stop()


st.set_page_config(page_title="SalesSight - Settings", layout="wide")

add_sidebar_logo()
st.title("⚙️ Settings")
st.write("Configure your SalesSight preferences here.")

