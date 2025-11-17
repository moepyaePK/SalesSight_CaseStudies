import streamlit as st
from utilities import custom_sidebar
from auth import require_auth, get_current_user, logout
from db import get_user_by_id, update_user_profile, change_password, get_user_uploads, get_user_feedback
from utils.validation import validate_email, validate_username, validate_password
import base64
from datetime import datetime, timezone
from config import Config

st.set_page_config(page_title="SalesSight - Settings", layout="wide")

# Authentication check
require_auth()

st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none !important;}
</style>
""", unsafe_allow_html=True)
custom_sidebar()

# --- Sidebar Content ---
with st.sidebar:
    st.page_link("pages/dashboard.py", label="📊 Dashboard")
    st.page_link("pages/data_upload.py", label="📂 Upload")
    st.page_link("pages/sales_forecasting.py", label="📈 Sales Forecasting")
    st.page_link("pages/setting.py", label="⚙️ Settings")
    if st.button("Logout"):
        logout()
        st.rerun()

# Get current user
user = get_current_user()
if not user:
    st.error("Unable to load user information")
    st.stop()

user_details = get_user_by_id(user['id'])

# Page Title
st.title("⚙️ Settings & Profile")
st.write("Manage your account settings and preferences")

# Create tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "🔐 Security", "📊 Activity", "🔔 Preferences"])

# ============================================
# TAB 1: Profile Information
# ============================================
with tab1:
    st.subheader("Profile Information")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Profile avatar placeholder
        st.markdown(
            f"""
            <div style="
                width: 150px;
                height: 150px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 60px;
                font-weight: bold;
                margin: 20px auto;
            ">
                {user['username'][0].upper()}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Account info
        st.info(f"""
        **Account Created:** {datetime.fromisoformat(user_details['created_at']).strftime('%B %d, %Y') if user_details and user_details.get('created_at') else 'N/A'}
        
        **Last Login:** {datetime.fromisoformat(user_details['last_login']).strftime('%B %d, %Y %I:%M %p') if user_details and user_details.get('last_login') else 'N/A'}
        """)
    
    with col2:
        st.markdown("### Update Profile")
        
        with st.form("update_profile_form"):
            new_username = st.text_input(
                "Username",
                value=user['username'],
                help="3-30 characters, letters, numbers, underscores and hyphens only"
            )
            
            new_email = st.text_input(
                "Email Address",
                value=user['email'],
                help="This will be your new login email"
            )
            
            submit_profile = st.form_submit_button("💾 Save Changes", use_container_width=True)
            
            if submit_profile:
                # Check if anything changed
                if new_username == user['username'] and new_email == user['email']:
                    st.info("ℹ️ No changes to save")
                else:
                    # Validate if changed
                    errors = []
                    
                    if new_username != user['username']:
                        valid, error = validate_username(new_username)
                        if not valid:
                            errors.append(error)
                    
                    if new_email != user['email']:
                        valid, error = validate_email(new_email)
                        if not valid:
                            errors.append(error)
                    
                    if errors:
                        for error in errors:
                            st.error(f"❌ {error}")
                    else:
                        # Update profile
                        result = update_user_profile(
                            user['id'],
                            username=new_username if new_username != user['username'] else None,
                            email=new_email if new_email != user['email'] else None
                        )
                        
                        if result['success']:
                            st.success("✅ Profile updated successfully!")
                            # Update session state
                            if new_username != user['username']:
                                st.session_state['username'] = new_username
                            if new_email != user['email']:
                                st.session_state['email'] = new_email
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")

# ============================================
# TAB 2: Security Settings
# ============================================
with tab2:
    st.subheader("🔐 Change Password")
    st.write("Keep your account secure by using a strong password")
    
    with st.form("change_password_form"):
        current_password = st.text_input(
            "Current Password",
            type="password",
            placeholder="Enter your current password"
        )
        
        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter new password",
            help=f"At least {Config.MIN_PASSWORD_LENGTH} characters with uppercase, lowercase, number, and special character"
        )
        
        confirm_new_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Re-enter new password"
        )
        
        submit_password = st.form_submit_button("🔒 Change Password", use_container_width=True)
        
        if submit_password:
            if not current_password or not new_password or not confirm_new_password:
                st.error("⚠️ Please fill in all password fields")
            elif new_password != confirm_new_password:
                st.error("⚠️ New passwords do not match")
            elif current_password == new_password:
                st.warning("⚠️ New password must be different from current password")
            else:
                # Validate new password
                valid, error = validate_password(new_password)
                if not valid:
                    st.error(f"❌ {error}")
                else:
                    # Attempt password change
                    result = change_password(user['id'], current_password, new_password)
                    
                    if result['success']:
                        st.success("✅ Password changed successfully!")
                        st.info("Please login again with your new password")
                    else:
                        st.error(f"❌ {result['message']}")
    
    st.markdown("---")
    
    # Security information
    st.markdown("### 🛡️ Security Features")
    st.markdown("""
    Your account is protected with:
    - ✅ **Bcrypt password hashing** - Industry-standard encryption
    - ✅ **Rate limiting** - Protection against brute-force attacks
    - ✅ **Session timeout** - Automatic logout after inactivity
    - ✅ **Secure database** - PostgreSQL with encryption
    """)

# ============================================
# TAB 3: Activity History
# ============================================
with tab3:
    st.subheader("📊 Your Activity")
    
    # Get user statistics
    uploads = get_user_uploads(user['id'])
    feedback_history = get_user_feedback(user['id'])
    
    # Stats cards
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Uploads", len(uploads))
    col2.metric("Feedback Given", len(feedback_history))
    col3.metric(
        "Account Age", 
        f"{(datetime.now(timezone.utc) - datetime.fromisoformat(user_details['created_at'])).days} days" 
        if user_details and user_details.get('created_at') else "N/A"
    )    
    st.markdown("---")
    
    # In TAB 3: Activity History, after showing recent uploads:

    st.markdown("### 🗂️ Manage Upload History")

    if uploads:
        for upload in uploads:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            col1.write(f"📄 {upload['filename']}")
            col2.write(f"{upload['file_size'] / 1024 / 1024:.2f} MB")
            col3.write(datetime.fromisoformat(upload['uploaded_at']).strftime('%m/%d/%Y'))
            
            # Add a "Use This File" button
            if col4.button("📊 Use", key=f"use_{upload['id']}"):
                st.session_state.save_path = upload['file_path']
                st.success(f"✅ Now using: {upload['filename']}")
                st.info("👈 Go to Dashboard or Sales Forecasting to analyze this file")
    
    # Feedback history
    st.markdown("### 💬 Your Feedback")
    if feedback_history:
        for fb in feedback_history[:5]:  # Show last 5
            rating_stars = "⭐" * fb['rating']
            st.markdown(
                f"""
                <div style="
                    padding: 10px;
                    border-left: 3px solid #1E90FF;
                    background-color: #F8F9FA;
                    margin: 10px 0;
                    border-radius: 5px;
                ">
                    <strong>{rating_stars}</strong> • {datetime.fromisoformat(fb['created_at']).strftime('%B %d, %Y')}
                    <br>
                    <em>{fb['comment'] if fb['comment'] else 'No comment provided'}</em>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("You haven't provided any feedback yet")

# ============================================
# TAB 4: Preferences
# ============================================
with tab4:
    st.subheader("🔔 Application Preferences")
    
    st.markdown("### Forecast Settings")
    default_forecast = st.selectbox(
        "Default Forecast Period",
        [30, 60, 90],
        index=0,
        help="Default number of days for forecasting"
    )
    
    st.markdown("### Notifications (Coming Soon)")
    email_notif = st.checkbox("Email notifications", value=True, disabled=True)
    weekly_summary = st.checkbox("Weekly summary report", value=True, disabled=True)
    
    st.markdown("### Display Settings")
    theme = st.selectbox("Theme", ["Light", "Dark"], disabled=True)
    
    st.info("💡 Tip: More preferences will be available in future updates!")
    
    if st.button("💾 Save Preferences", use_container_width=True):
        st.success("✅ Preferences saved!")

# ============================================
# Danger Zone
# ============================================
st.markdown("---")
st.markdown("### ⚠️ Danger Zone")

with st.expander("🗑️ Delete Account", expanded=False):
    st.warning("""
    **Warning:** This action cannot be undone. All your data, including:
    - Profile information
    - Uploaded files
    - Forecasts
    - Feedback
    
    will be permanently deleted.
    """)
    
    delete_confirm = st.text_input(
        "Type 'DELETE' to confirm",
        placeholder="DELETE"
    )
    
    if st.button("🗑️ Permanently Delete Account", type="secondary"):
        if delete_confirm == "DELETE":
            st.error("Account deletion is not yet implemented. Please contact support.")
        else:
            st.warning("Please type 'DELETE' to confirm")