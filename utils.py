import base64
import streamlit as st
from config import LOGO_PATH, SESSION_STATE_KEY_SAVEPATH


def require_upload():
    """
    Check if the user has uploaded a file.
    If not, show a warning and stop the page from rendering main content.
    """
    if SESSION_STATE_KEY_SAVEPATH not in st.session_state:
        st.warning("⚠️ Please upload a sales CSV file first on the Upload page to view analytics.")
        st.stop()


def custom_sidebar(title="SalesSight", sidebar_bg="#000000", label_color="#ffffff"):
    """
    Renders a custom sidebar with a logo and title, and applies custom styles.
    This function hides the default Streamlit sidebar navigation and injects CSS
    and JavaScript to create a persistent custom-styled sidebar.
    """
    # Hide Streamlit default sidebar navigation
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Encode logo to base64
    try:
        with open(LOGO_PATH, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        logo_base64 = ""  # Handle case where logo is not found

    # Sidebar styling
    st.markdown(
        f"""
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
        """,
        unsafe_allow_html=True,
    )

    # Apply styles using inline properties and a MutationObserver for persistence
    st.markdown(
        f"""
    <script>
    (function() {{
        function applySidebarStyles(){{
            const sidebar = document.querySelector('[data-testid="stSidebar"]') || document.querySelector('section[data-testid="stSidebar"]');
            const nav = document.querySelector('[data-testid="stSidebarNav"]');
            if(sidebar){{
                sidebar.style.setProperty('background', '{sidebar_bg}', 'important');
                sidebar.style.setProperty('color', '{label_color}', 'important');
            }}
            if(nav){{
                nav.style.setProperty('background', '{sidebar_bg}', 'important');
                // links
                nav.querySelectorAll('a').forEach(a => {{
                    a.style.setProperty('color', '{label_color}', 'important');
                    a.style.setProperty('font-weight', '500', 'important');
                }});
                // active link
                nav.querySelectorAll('a[data-testid="stSidebarNavLinkActive"]').forEach(a => {{
                    a.style.setProperty('background', 'rgba(255,255,255,0.08)', 'important');
                    a.style.setProperty('color', '{label_color}', 'important');
                    a.style.setProperty('font-weight', '700', 'important');
                }});
                // svg icons
                nav.querySelectorAll('svg').forEach(s => {{
                    s.style.setProperty('fill', '{label_color}', 'important');
                }});
            }}
        }}

        applySidebarStyles();

        const observer = new MutationObserver(() => {{ applySidebarStyles(); }});
        observer.observe(document.body, {{ childList: true, subtree: true }});
        // stop observing after 5s to avoid overhead
        setTimeout(() => observer.disconnect(), 5000);
    }})();
    </script>
    """,
        unsafe_allow_html=True,
    )

    # Sidebar structure
    with st.sidebar:
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" />' if logo_base64 else ""
        st.markdown(
            f"""
            <div class="sidebar-title">
                {logo_html}
                <span>{title}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
