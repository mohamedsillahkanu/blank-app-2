import streamlit as st
import importlib
import os
import sys
import types
import importlib.util

# Custom CSS for better styling with light blue theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #3498db;
        --secondary-color: #2980b9;
        --light-bg: #ebf5fb;
        --dark-bg: #2c3e50;
        --text-color: #34495e;
        --light-text: #ecf0f1;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(120deg, var(--primary-color), var(--secondary-color));
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 1rem 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Module card styling */
    .module-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid var(--primary-color);
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .module-card:hover {
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .module-card h3 {
        color: var(--primary-color);
        margin-top: 0;
    }
    
    .module-card p {
        color: var(--text-color);
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 2rem;
        background-color: var(--light-bg);
        margin-top: 3rem;
        border-radius: 1rem 1rem 0 0;
        color: var(--text-color);
        border-top: 1px solid rgba(52, 152, 219, 0.2);
    }
    
    .footer p {
        margin: 0.5rem 0;
    }
    
    .footer .logo {
        font-size: 1.5rem;
        font-weight: bold;
        color: var(--primary-color);
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton button {
        background-color: var(--primary-color) !important;
        color: white !important;
        border-radius: 30px !important;
        border: none !important;
        padding: 0.3rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        background-color: var(--secondary-color) !important;
        box-shadow: 0 4px 10px rgba(52, 152, 219, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Back button styling */
    .back-button button {
        background-color: #ecf0f1 !important;
        color: var(--text-color) !important;
    }
    
    .back-button button:hover {
        background-color: #dfe6e9 !important;
    }
    
    /* Improve overall appearance */
    .block-container {
        padding-top: 0 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--primary-color);
    }
    
    /* Divider styling */
    hr {
        border-color: rgba(52, 152, 219, 0.2);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Set page configuration for the main dashboard
st.set_page_config(
    page_title="SNT Dashboard",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for module navigation
if 'current_module' not in st.session_state:
    st.session_state.current_module = None

# Function to safely import module without set_page_config issues
def import_module_safely(module_path, module_name):
    """Import a module from file path while handling set_page_config"""
    try:
        # Read the module content
        with open(module_path, 'r') as file:
            source_code = file.read()
        
        # Modify the source code to remove st.set_page_config call
        modified_code = []
        skip_line = False
        inside_config = False
        
        for line in source_code.split('\n'):
            if "st.set_page_config" in line:
                skip_line = True
                inside_config = True
                continue
            
            if inside_config:
                if ")" in line:
                    inside_config = False
                    skip_line = False
                    continue
            
            if not skip_line:
                modified_code.append(line)
        
        # Create a new module
        module = types.ModuleType(module_name)
        
        # Set the module's __file__ attribute
        module.__file__ = module_path
        
        # Add the module to sys.modules
        sys.modules[module_name] = module
        
        # Execute the modified code in the module's namespace
        exec('\n'.join(modified_code), module.__dict__)
        
        return module
    
    except Exception as e:
        st.error(f"Error loading module: {str(e)}")
        return None

# Create Header and Footer function
def render_header():
    st.markdown("""
    <div class="main-header">
        <h1>🧊 SNT Analytics Dashboard</h1>
        <p>Advanced data analysis and processing tools</p>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <div class="footer">
        <div class="logo">SNT Analytics Platform</div>
        <p>Powerful data analysis tools for your business needs</p>
        <p>© 2025 SNT Analytics - All rights reserved</p>
    </div>
    """, unsafe_allow_html=True)

# Main function to run the dashboard
def main():
    # Render the header
    render_header()
    
    # If a module is selected, run it
    if st.session_state.current_module:
        # Add a back button (styled differently)
        st.markdown('<div class="back-button">', unsafe_allow_html=True)
        if st.button("← Back to Dashboard"):
            st.session_state.current_module = None
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader(f"Running: {st.session_state.current_module.replace('.py', '').replace('_', ' ').title()}")
        
        try:
            # Extract module name without .py extension
            module_name = st.session_state.current_module.replace('.py', '')
            
            # Get the module path
            base_dir = os.path.abspath(os.path.dirname(__file__))
            pages_dir = os.path.join(base_dir, "pages")
            module_path = os.path.join(pages_dir, st.session_state.current_module)
            
            # Import the module safely (without set_page_config issues)
            module = import_module_safely(module_path, module_name)
            
            if module:
                # Try to run the module
                # First, try to call the run() function if it exists
                if hasattr(module, 'run'):
                    module.run()
                # If not, try to find a main() function
                elif hasattr(module, 'main'):
                    module.main()
                # If none of those work, we'll assume the module has already executed its code
                else:
                    st.warning(f"Module {module_name} doesn't have a run() or main() function, but its code has been executed.")
            else:
                st.error(f"Failed to load module: {st.session_state.current_module}")
            
            return
        except Exception as e:
            st.error(f"Error running module: {str(e)}")
            st.write(f"Details: {type(e).__name__}: {str(e)}")
            
    # Otherwise, show the main dashboard with the 10 boxes
    st.header("Select a Module")
    st.write("Choose one of the available modules below to begin your data analysis journey.")
    
    # Define the modules with their descriptions and icons
    modules = {
        "compute_new.py": {"icon": "📊", "desc": "Create and calculate new variables from existing columns in your dataset."},
        "data_visualization.py": {"icon": "📈", "desc": "Generate insightful visualizations and charts to understand your data better."},
        "machine_learning.py": {"icon": "🤖", "desc": "Train and deploy machine learning models with automated pipelines."},
        "data_processing.py": {"icon": "⚙️", "desc": "Clean, transform, and preprocess your data for analysis."},
        "statistics.py": {"icon": "📉", "desc": "Perform statistical tests and analyses to derive meaningful insights."},
        "reporting.py": {"icon": "📝", "desc": "Generate automated reports and dashboards from your analysis results."},
        "file_management.py": {"icon": "📁", "desc": "Manage, organize, and catalog your data files efficiently."},
        "settings.py": {"icon": "⚙️", "desc": "Configure platform settings and preferences for optimal experience."},
        "user_management.py": {"icon": "👥", "desc": "Manage user accounts, permissions, and access controls."},
        "dashboard_home.py": {"icon": "🏠", "desc": "View overview metrics and KPIs in a comprehensive dashboard."}
    }
    
    # Get the correct pages directory path
    base_dir = os.path.abspath(os.path.dirname(__file__))
    pages_dir = os.path.join(base_dir, "pages")
    
    # Create 2 columns
    col1, col2 = st.columns(2)
    
    # First column - first 5 modules
    with col1:
        for name, info in list(modules.items())[:5]:
            # Create a card for each module using HTML
            st.markdown(f"""
            <div class="module-card">
                <h3>{info['icon']} {name.replace('.py', '').replace('_', ' ').title()}</h3>
                <p>{info['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Check if the module file exists
            module_file_path = os.path.join(pages_dir, name)
            file_exists = os.path.exists(module_file_path)
            
            if not file_exists:
                st.warning(f"Module file not found: {module_file_path}")
            
            if st.button(f"Open {name.replace('.py', '').replace('_', ' ').title()}", 
                         key=f"btn_{name}", 
                         disabled=not file_exists):
                st.session_state.current_module = name
                st.experimental_rerun()
            st.markdown("<hr>", unsafe_allow_html=True)
    
    # Second column - next 5 modules
    with col2:
        for name, info in list(modules.items())[5:]:
            # Create a card for each module using HTML
            st.markdown(f"""
            <div class="module-card">
                <h3>{info['icon']} {name.replace('.py', '').replace('_', ' ').title()}</h3>
                <p>{info['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Check if the module file exists
            module_file_path = os.path.join(pages_dir, name)
            file_exists = os.path.exists(module_file_path)
            
            if not file_exists:
                st.warning(f"Module file not found: {module_file_path}")
            
            if st.button(f"Open {name.replace('.py', '').replace('_', ' ').title()}", 
                         key=f"btn_{name}", 
                         disabled=not file_exists):
                st.session_state.current_module = name
                st.experimental_rerun()
            st.markdown("<hr>", unsafe_allow_html=True)
    
    # Render the footer
    render_footer()

if __name__ == "__main__":
    main()
