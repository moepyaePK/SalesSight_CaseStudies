import streamlit as st
from pages.data_upload import data_extraction
from utils import add_sidebar_logo



# ---- Page Config ----
st.set_page_config(page_title="SalesSight - Dashboard", layout="wide")

add_sidebar_logo()

if "save_path" in st.session_state:
    metrics = data_extraction(st.session_state.save_path)  # ✅ Works
    st.write(metrics)
else:
    st.warning("Please upload a file first.")

# def call_the_function(file):
#     data_extraction(file)    