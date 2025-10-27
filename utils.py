import streamlit as st
import base64


def require_upload():
    """
    Check if the user has uploaded a file.
    If not, show a warning and stop the page from rendering main content.
    """
    if "save_path" not in st.session_state:
        st.warning("⚠️ Please upload a sales CSV file first on the Upload page to view analytics.")
        st.stop()

def custom_sidebar(logo_path="logo.png", title="SalesSight"):
    # Hide Streamlit default sidebar navigation
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

    # Encode logo to base64
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()

    # Sidebar styling
    st.markdown(f"""
        <style>
        .sidebar-title {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 18px;
            color: #1E90FF;
            margin-bottom: 25px;
        }}
        .sidebar-title img {{
            width: 30px;
            height: 30px;
        }}
        </style>
    """, unsafe_allow_html=True)

    # Sidebar structure
    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-title">
                <img src="data:image/png;base64,{logo_base64}" />
                <span>{title}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
