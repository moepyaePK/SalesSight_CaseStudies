import streamlit as st
import base64
import os


def require_upload(allow_selection=False):
    """
    Check if the user has uploaded a file.
    Checks session state first, then database.
    If not found, show a warning and stop the page.
    
    Args:
        allow_selection: If True, show a selector for previous uploads
    
    Returns:
        file_path: Path to the selected file
    """
    from auth import get_current_user
    import db
    
    user = get_current_user()
    if not user:
        st.error("⚠️ Please login first")
        st.switch_page("Home.py")
        st.stop()
    
    # Get all user uploads
    uploads = db.get_user_uploads(user['id'], limit=20)
    
    if not uploads:
        st.warning("⚠️ No uploaded files found. Please upload a CSV file first.")
        st.page_link("pages/data_upload.py", label="👉 Go to Upload Page")
        st.stop()
    
    # If allow_selection is True, show a file selector
    if allow_selection and len(uploads) > 1:
        st.markdown("### 📂 Select Data File")
        
        # Create options for selectbox
        file_options = {}
        for upload in uploads:
            from datetime import datetime
            date_str = datetime.fromisoformat(upload['uploaded_at']).strftime('%Y-%m-%d %H:%M')
            size_mb = upload['file_size'] / (1024 * 1024)
            label = f"{upload['filename']} ({size_mb:.2f} MB) - {date_str}"
            file_options[label] = upload['file_path']
        
        # Check if we have a previously selected file in session
        current_path = st.session_state.get('save_path')
        
        # Find the index of current file
        default_index = 0
        if current_path:
            for idx, path in enumerate(file_options.values()):
                if path == current_path:
                    default_index = idx
                    break
        
        selected_label = st.selectbox(
            "Choose a file to analyze:",
            options=list(file_options.keys()),
            index=default_index,
            help="Select from your previously uploaded files"
        )
        
        file_path = file_options[selected_label]
        
        # Update session state with selected file
        st.session_state.save_path = file_path
        
    else:
        # Use the most recent upload
        file_path = st.session_state.get('save_path')
        
        if not file_path:
            latest_upload = uploads[0]  # Already sorted by uploaded_at DESC
            file_path = latest_upload['file_path']
            st.session_state.save_path = file_path
    
    # Verify file exists
    if not file_path or not os.path.exists(file_path):
        st.error(f"❌ File not found: {file_path if file_path else 'No path'}")
        st.warning("⚠️ The file may have been deleted. Please upload a new CSV file.")
        st.page_link("pages/data_upload.py", label="👉 Go to Upload Page")
        st.stop()
    
    return file_path


def show_file_selector():
    """
    Display a file selector in the sidebar for choosing uploaded files.
    Returns the selected file path or None.
    """
    from auth import get_current_user
    import db
    from datetime import datetime
    
    user = get_current_user()
    if not user:
        return None
    
    uploads = db.get_user_uploads(user['id'], limit=20)
    
    if not uploads:
        return None
    
    if len(uploads) == 1:
        # Only one file, no need for selector
        return uploads[0]['file_path']
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📂 Select Data File")
    
    # Create options
    file_options = {}
    display_names = []
    
    for upload in uploads:
        date_str = datetime.fromisoformat(upload['uploaded_at']).strftime('%m/%d/%y %H:%M')
        size_mb = upload['file_size'] / (1024 * 1024)
        
        # Truncate long filenames
        filename = upload['filename']
        if len(filename) > 30:
            filename = filename[:27] + "..."
        
        label = f"{filename}"
        sublabel = f"{size_mb:.1f}MB • {date_str}"
        
        display_names.append(f"{label}\n{sublabel}")
        file_options[label] = upload['file_path']
    
    # Get current selection
    current_path = st.session_state.get('save_path')
    default_index = 0
    
    if current_path:
        for idx, path in enumerate(file_options.values()):
            if path == current_path:
                default_index = idx
                break
    
    selected_label = st.sidebar.selectbox(
        "Choose file:",
        options=list(file_options.keys()),
        index=default_index,
        label_visibility="collapsed"
    )
    
    selected_path = file_options[selected_label]
    
    # Update session state
    if selected_path != current_path:
        st.session_state.save_path = selected_path
        st.rerun()
    
    return selected_path


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