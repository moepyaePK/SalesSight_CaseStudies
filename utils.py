import streamlit as st
import base64

def add_sidebar_logo(logo_path="logo.png", title="SalesSight"):
    # Convert logo to base64
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()

    with st.sidebar:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
                <img src="data:image/png;base64,{logo_base64}" width="40">
                <h2 style="color:#1E90FF; margin: 0;">{title}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
