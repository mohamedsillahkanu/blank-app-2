import streamlit as st
import importlib

# Set page configuration
st.set_page_config(
    page_title="SNT Dashboard",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for module navigation
if 'current_module' not in st.session_state:
    st.session_state.current_module = None

# Main function to run the dashboard
def main():
    st.title("SNT Dashboard")
    
    # If a module is selected, import and run it
    if st.session_state.current_module:
        try:
            # Extract module name without .py extension
            module_name = st.session_state.current_module.replace('.py', '')
            
            # Import the selected module dynamically
            module = importlib.import_module(f"modules.{module_name}")
            # Run the module
            module.run()
            return
        except ImportError as e:
            st.error(f"Error loading module: {e}")
    
    # Otherwise, show the main dashboard with the 10 boxes
    st.header("Select a Module")
    
    # Define the modules with their descriptions and icons
    modules = {
        "data_analysis.py": {"icon": "📊", "desc": "Analyze your data with various techniques"},
        "data_visualization.py": {"icon": "📈", "desc": "Create insightful visualizations"},
        "machine_learning.py": {"icon": "🤖", "desc": "Train and deploy ML models"},
        "data_processing.py": {"icon": "⚙️", "desc": "Process and transform your data"},
        "statistics.py": {"icon": "📉", "desc": "Statistical analysis and testing"},
        "reporting.py": {"icon": "📝", "desc": "Generate automated reports"},
        "file_management.py": {"icon": "📁", "desc": "Manage your data files"},
        "settings.py": {"icon": "⚙️", "desc": "Configure dashboard settings"},
        "user_management.py": {"icon": "👥", "desc": "Manage users and permissions"},
        "dashboard_home.py": {"icon": "🏠", "desc": "Dashboard overview and metrics"}
    }
    
    # Create 2 columns
    col1, col2 = st.columns(2)
    
    # First column - first 5 modules
    with col1:
        for name, info in list(modules.items())[:5]:
            st.subheader(f"{info['icon']} {name.replace('.py', '').replace('_', ' ').title()}")
            st.write(info['desc'])
            if st.button(f"Open {name.replace('.py', '').replace('_', ' ').title()}", key=f"btn_{name}"):
                st.session_state.current_module = name
                st.experimental_rerun()
            st.divider()
    
    # Second column - next 5 modules
    with col2:
        for name, info in list(modules.items())[5:]:
            st.subheader(f"{info['icon']} {name.replace('.py', '').replace('_', ' ').title()}")
            st.write(info['desc'])
            if st.button(f"Open {name.replace('.py', '').replace('_', ' ').title()}", key=f"btn_{name}"):
                st.session_state.current_module = name
                st.experimental_rerun()
            st.divider()

if __name__ == "__main__":
    main()
