import streamlit as st
from auth import verify_user



# ---- Hide Sidebar Completely (including arrow + space) ----
hide_sidebar_style = """
    <style>
        /* Hide the sidebar completely */
        [data-testid="stSidebar"], 
        [data-testid="stSidebarNav"], 
        [data-testid="stSidebarCollapsedControl"],
        section[data-testid="stSidebar"] {
            display: none !important;
        }

        /* Hide the expand/collapse button (for older/newer versions) */
        button[title="Expand sidebar"], 
        button[kind="header"], 
        [data-testid="baseButton-header"] {
            display: none !important;
        }

        /* Remove sidebar space and expand main view fully */
        [data-testid="stAppViewContainer"] {
            margin-left: 0 !important;
            width: 100% !important;
        }

        /* Remove any internal padding */
        [data-testid="stVerticalBlock"] > div:first-child {
            padding-left: 0 !important;
            padding-right: 0 !important;
        }

        /* Optional: hide top navbar dropdown if present */
        [data-testid="stHeaderActionElements"] {
            display: none !important;
        }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)
# --------------------------------------------------------



st.title("🔑 Login")

email = st.text_input("Enter Email")
password = st.text_input("Enter Password", type="password")

if st.button("Login"):
    if verify_user(email, password):
        # st.session_state["user"] = email
        st.success("Login successful!")
        st.switch_page("pages/data_upload.py")
    else:
        st.error("Invalid email or password.")

st.markdown("---")
st.write("Don't have an account yet?")
if st.button("📝 Register"):
    st.switch_page("pages/register.py")