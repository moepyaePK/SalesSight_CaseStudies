import streamlit as st
import base64

def add_sidebar_logo(logo_path="logo.png", title="SalesSight"):

    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()

    with st.sidebar:
        st.markdown(
            f"""
            <style>
                /* Sidebar base */
                [data-testid="stSidebar"] {{
                    background-color: #ffffff !important;
                    padding-top: 0 !important;
                }}

                /* Sidebar top area */
                section[data-testid="stSidebar"] > div:first-child {{
                    padding-top: 0 !important;
                }}

                /* Container for logo + title */
                [data-testid="stSidebarNav"]::before {{
                    content: "";
                    display: flex;
                    align-items: center;
                    justify-content: flex-start;
                    height: 60px;
                    width: 100%;
                    background-color: #ffffff;
                    background-image: url("data:image/png;base64,{logo_base64}");
                    background-repeat: no-repeat;
                    background-size: 26px 26px;
                    background-position: 18px center;
                    border-bottom: 1px solid #f2f2f2;
                    position: relative;
                    z-index: 1;
                    pointer-events: none; /* Let clicks pass through */
                }}

                /* Blue title beside logo */
                [data-testid="stSidebarNav"]::after {{
                    content: "{title}";
                    position: absolute;
                    top: 18px;
                    left: 52px;
                    font-family: 'Inter', sans-serif;
                    font-weight: 600;
                    font-size: 18px;
                    color: #1E90FF;
                    z-index: 1;
                    pointer-events: none; /* Let clicks pass through */
                }}

                /* Menu container adjustment */
                [data-testid="stSidebarNav"] {{
                    margin-top: -60px !important;
                    position: relative;
                    z-index: 0;
                }}

                /* Sidebar menu links */
                [data-testid="stSidebarNav"] ul {{
                    padding-left: 10px;
                }}

                [data-testid="stSidebarNav"] li a {{
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    padding: 8px 14px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-family: 'Inter', sans-serif;
                    font-size: 15px;
                    font-weight: 500;
                    color: #4B5563 !important;
                    transition: all 0.2s ease-in-out;
                }}


                /* Active page highlight */
                [data-testid="stSidebarNav"] li a[data-testid="stSidebarNavLinkActive"] {{
                    background-color: #bbddfc !important;
                    color: #1E90FF !important;
                    font-weight: 600 !important;
                }}
            </style>
            """,
            unsafe_allow_html=True
        )