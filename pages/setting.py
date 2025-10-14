import streamlit as st
from utils import add_sidebar_logo


st.set_page_config(page_title="SalesSight - Settings", layout="wide")

add_sidebar_logo()
st.title("⚙️ Settings")
st.write("Configure your SalesSight preferences here.")

