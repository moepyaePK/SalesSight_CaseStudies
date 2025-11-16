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

def custom_sidebar(logo_path="logo.png", title="SalesSight", sidebar_bg="#000000", label_color="#ffffff"):
    # Hide Streamlit default sidebar navigation (we'll render our own header and override styles)
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

    # Apply styles using inline properties (with !important) and a MutationObserver so they persist
    st.markdown(f"""
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
        
