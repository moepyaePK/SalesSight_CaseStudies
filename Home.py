import streamlit as st
from auth import is_logged_in, logout

st.set_page_config(page_title="SalesSight - Home", layout="wide")

st.title("💼 Welcome to SalesSight!")
st.write("Gain insights from your sales data with interactive dashboards and forecasting tools.")

# col1, col2 = st.columns(2)
# with col1:
#     st.image("https://cdn-icons-png.flaticon.com/512/992/992703.png", width=250)
# with col2:
#     st.markdown("""
#     ### 📊 What you can do
#     - Upload and visualize your sales data  
#     - View top products and sales trends  
#     - Forecast future sales performance
#     """)

st.markdown("---")

if is_logged_in():
    st.success(f"You're logged in as **{st.session_state['username']}**.")
    if st.button("Go to Dashboard"):
        st.switch_page("dashboard.py")
    if st.button("Logout"):
        logout()
        st.experimental_rerun()
else:
    st.info("Please log in or register to access the Dashboard.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Login"):
            st.switch_page("pages/login.py")
    with col2:
        if st.button("📝 Register"):
            st.switch_page("pages/register.py")
