import streamlit as st
from auth import login_user
from config import Config

st.set_page_config(page_title="SalesSight - Login", layout="wide")

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
col1, col2 = st.columns([1, 1])

with col1:
    st.title("🔐 Welcome Back!")
    st.write("Login to access your SalesSight dashboard")
    
    # Show success message if just registered
    if 'registered_email' in st.session_state:
        st.success(f"✅ Account created! Please login with: {st.session_state['registered_email']}")
        del st.session_state['registered_email']
    
    with st.form("login_form"):
        email = st.text_input(
            "Email Address",
            placeholder="your.email@example.com",
            key="login_email"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        col_a, col_b = st.columns([1, 1])
        with col_a:
            remember_me = st.checkbox("Remember me")
        with col_b:
            st.markdown(
                "<div style='text-align: right; padding-top: 5px;'>"
                "<a href='#' style='color: #1E90FF; text-decoration: none;'>Forgot password?</a>"
                "</div>",
                unsafe_allow_html=True
            )
        
        submit_button = st.form_submit_button("Login", use_container_width=True)
        
        if submit_button:
            if not email or not password:
                st.error("⚠️ Please enter both email and password")
            else:
                with st.spinner("Logging in..."):
                    result = login_user(email, password)
                    
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        st.balloons()
                        # Redirect to dashboard
                        st.switch_page("pages/dashboard.py")
                    else:
                        st.error(f"❌ {result['message']}")
                        
                        # Show hint about rate limiting if too many attempts
                        if "too many" in result['message'].lower():
                            st.warning(
                                f"⏰ For security, login is temporarily locked after "
                                f"{Config.MAX_LOGIN_ATTEMPTS} failed attempts. "
                                f"Please try again in {Config.LOGIN_TIMEOUT_MINUTES} minutes."
                            )

with col2:
    st.markdown("### Quick Demo")
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 10px;
            color: white;
            margin-top: 50px;
        ">
            <h3 style="color: white; margin-top: 0;">🚀 New to SalesSight?</h3>
            <p style="margin-bottom: 20px;">
                Experience the power of AI-driven sales analytics. 
                Create your free account in less than a minute!
            </p>
            <ul style="list-style: none; padding: 0;">
                <li style="margin: 10px 0;">✅ No credit card required</li>
                <li style="margin: 10px 0;">✅ Upload unlimited datasets</li>
                <li style="margin: 10px 0;">✅ AI-powered forecasting</li>
                <li style="margin: 10px 0;">✅ Beautiful visualizations</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# Don't have account section
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("Don't have an account yet?")
with col2:
    if st.button("📝 Sign Up", use_container_width=True):
        st.switch_page("pages/register.py")

# Security notice
st.markdown(
    """
    <div style="
        text-align: center;
        color: #888;
        font-size: 12px;
        margin-top: 30px;
        padding: 10px;
    ">
        🔒 Your connection is secure. We use industry-standard encryption to protect your data.
    </div>
    """,
    unsafe_allow_html=True
)