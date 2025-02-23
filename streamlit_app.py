# config.py
import streamlit as st

def apply_custom_style():
    st.markdown("""
        <style>
            /* Sidebar styling */
            [data-testid=stSidebar] {
                background-color: var(--sidebar-bg);
                border-right: 1px solid var(--border-color);
            }
            
            [data-testid=stSidebarNav] {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            
            [data-testid=stSidebarNav] > ul {
                padding-top: 2rem;
                gap: 0.5rem;
            }
            
            [data-testid=stSidebarNav] span {
                word-wrap: break-word;
                white-space: pre-wrap;
            }
            
            /* Style sidebar nav links */
            [data-testid=stSidebarNav] a {
                width: 100%;
                padding: 0.75rem 1rem;
                border-radius: 0.5rem;
                transition: all 0.3s ease;
                margin-bottom: 0.5rem;
                background: var(--card-bg);
                color: var(--text-color) !important;
                border: 1px solid transparent;
            }
            
            [data-testid=stSidebarNav] a:hover {
                background: var(--accent-color);
                color: white !important;
                transform: translateX(5px);
            }
            
            [data-testid=stSidebarNav] a:active,
            [data-testid=stSidebarNav] a.active {
                background: var(--accent-color);
                color: white !important;
                border-color: var(--accent-color);
            }
            
            /* Sidebar header */
            .sidebar-header {
                text-align: center;
                padding: 1rem;
                margin-bottom: 1rem;
                border-bottom: 2px solid var(--accent-color);
                background: var(--gradient);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            /* Theme selector container */
            .theme-selector {
                padding: 1rem;
                margin-top: 2rem;
                border-top: 1px solid var(--border-color);
            }
            
            /* Animation for page transitions */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .main-content {
                animation: fadeIn 0.5s ease-out;
            }
            
            /* Footer */
            .sidebar-footer {
                position: fixed;
                bottom: 0;
                left: 0;
                width: inherit;
                padding: 1rem;
                text-align: center;
                background: var(--sidebar-bg);
                border-top: 1px solid var(--border-color);
                font-size: 0.8rem;
                color: var(--text-color);
            }
            
            /* Icon emojis in sidebar */
            [data-testid=stSidebarNav] span:first-child {
                margin-right: 0.5rem;
                font-size: 1.2rem;
            }
        </style>
    """, unsafe_allow_html=True)

    # Add sidebar header
    st.sidebar.markdown('<div class="sidebar-header"><h2>🗺️ GeoSpatial Tool</h2></div>', unsafe_allow_html=True)
    
    # Add theme selector to sidebar
    with st.sidebar:
        st.markdown('<div class="theme-selector">', unsafe_allow_html=True)
        st.selectbox("🎨 Theme", list(themes.keys()), key='theme_selector')
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add footer
        st.markdown(
            '<div class="sidebar-footer">Version 1.0.0<br>© 2024 GeoSpatial Tool</div>',
            unsafe_allow_html=True
        )

# Place this in your pages folder structure:
# pages/
#   📊_Data_Analysis.py
#   🗺️_Map_Visualization.py
#   📈_Reports.py
#   ⚙️_Settings.py
