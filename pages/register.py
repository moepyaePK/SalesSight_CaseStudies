import streamlit as st
from auth import register_user
from config import Config

st.set_page_config(page_title="SalesSight - Register", layout="wide")

# ---- Hide Sidebar Completely ----
hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"], 
        [data-testid="stSidebarNav"], 
        [data-testid="stSidebarCollapsedControl"],
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        button[title="Expand sidebar"], 
        button[kind="header"], 
        [data-testid="baseButton-header"] {
            display: none !important;
        }
        [data-testid="stAppViewContainer"] {
            margin-left: 0 !important;
            width: 100% !important;
        }
        [data-testid="stVerticalBlock"] > div:first-child {
            padding-left: 0 !important;
            padding-right: 0 !important;
        }
        [data-testid="stHeaderActionElements"] {
            display: none !important;
        }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# ---- Main Content ----
st.title("📝 Create Your Account")
st.write("Join SalesSight to start analyzing your sales data")

# Create two columns for layout
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Account Information")
    
    with st.form("registration_form"):
        username = st.text_input(
            "Username",
            placeholder="Choose a unique username",
            help="3-30 characters, letters, numbers, underscores and hyphens only"
        )
        
        email = st.text_input(
            "Email Address",
            placeholder="your.email@example.com",
            help="We'll never share your email with anyone"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a strong password",
            help=f"At least {Config.MIN_PASSWORD_LENGTH} characters with uppercase, lowercase, number, and special character"
        )
        
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password"
        )
        
        # Terms and conditions checkbox
        terms_accepted = st.checkbox(
            "I agree to the Terms of Service and Privacy Policy",
            value=False
        )
        
        submit_button = st.form_submit_button("Create Account", use_container_width=True)
        
        if submit_button:
            # Validation
            if not username or not email or not password or not confirm_password:
                st.error("⚠️ Please fill in all fields")
            elif password != confirm_password:
                st.error("⚠️ Passwords do not match")
            elif not terms_accepted:
                st.error("⚠️ Please accept the Terms of Service to continue")
            else:
                # Attempt registration
                with st.spinner("Creating your account..."):
                    result = register_user(username, email, password)
                    
                    if result['success']:
                        st.success("✅ Account created successfully!")
                        st.balloons()
                        st.info("🔐 Redirecting to login page...")
                        st.session_state['registration_success'] = True
                        st.session_state['registered_email'] = email
                        # Use rerun instead of experimental_rerun
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")

with col2:
    st.markdown("### Why Choose SalesSight?")
    
    features = [
        ("📊", "Interactive Dashboards", "Visualize your sales data with beautiful, customizable charts"),
        ("🤖", "AI-Powered Forecasting", "Get accurate sales predictions using advanced machine learning"),
        ("📈", "Trend Analysis", "Identify patterns and opportunities in your sales data"),
        ("🔒", "Secure & Private", "Your data is encrypted and protected with industry-standard security"),
        ("📤", "Easy Export", "Download reports in CSV, Excel, or PDF format"),
        ("⚡", "Lightning Fast", "Process and analyze thousands of records in seconds")
    ]
    
    for icon, title, description in features:
        st.markdown(
            f"""
            <div style="
                padding: 12px;
                margin: 10px 0;
                border-left: 3px solid #1E90FF;
                background-color: #131720;
                border-radius: 5px;
            ">
                <div style="font-size: 20px; margin-bottom: 5px;">{icon} <strong>{title}</strong></div>
                <div style="color: #ffffff; font-size: 14px;">{description}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("---")

# Already have account section
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("Already have an account?")
with col2:
    if st.button("🔐 Login", use_container_width=True):
        st.switch_page("pages/login.py")

# Check if redirecting after successful registration
if 'registration_success' in st.session_state and st.session_state['registration_success']:
    st.session_state['registration_success'] = False
    st.switch_page("pages/login.py")