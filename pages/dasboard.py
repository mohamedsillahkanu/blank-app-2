import streamlit as st
import importlib
import os
import sys
import types
import importlib.util

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

# Main function to run the dashboard
def main():
    st.title("SNT Dashboard")
    
    # If a module is selected, run it
    if st.session_state.current_module:
        # Add a back button
        if st.button("← Back to Dashboard"):
            st.session_state.current_module = None
            st.experimental_rerun()
        
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
    
    # Define the modules with their descriptions and icons
    modules = {
        "compute_new.py": {"icon": "📊", "desc": "Analyze your data with various techniques"},
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
    
    # Get the correct pages directory path
    base_dir = os.path.abspath(os.path.dirname(__file__))
    pages_dir = os.path.join(base_dir, "pages")
    
    # Create 2 columns
    col1, col2 = st.columns(2)
    
    # First column - first 5 modules
    with col1:
        for name, info in list(modules.items())[:5]:
            st.subheader(f"{info['icon']} {name.replace('.py', '').replace('_', ' ').title()}")
            st.write(info['desc'])
            
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
            st.divider()
    
    # Second column - next 5 modules
    with col2:
        for name, info in list(modules.items())[5:]:
            st.subheader(f"{info['icon']} {name.replace('.py', '').replace('_', ' ').title()}")
            st.write(info['desc'])
            
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
            st.divider()

if __name__ == "__main__":
    main()
