import streamlit as st
import importlib
import os
import sys
import types
import inspect

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

# Function to extract module code and create a clean run function
def create_module_function(module_path):
    try:
        with open(module_path, 'r') as file:
            code = file.read()
        
        # Remove the set_page_config call from the code
        lines = code.split('\n')
        filtered_lines = []
        skip_line = False
        config_removed = False
        
        for line in lines:
            if 'st.set_page_config(' in line and not config_removed:
                skip_line = True
                config_removed = True
            elif skip_line and ')' in line:
                skip_line = False
                continue
            
            if not skip_line:
                filtered_lines.append(line)
        
        module_code = '\n'.join(filtered_lines)
        
        # Create a function that will execute the module code
        def run_function():
            # Create a new module namespace
            module_globals = {
                'st': st,
                '__name__': '__main__',
                '__file__': module_path,
            }
            
            # Execute the module code in this namespace
            exec(module_code, module_globals)
        
        return run_function
    
    except Exception as e:
        st.error(f"Error creating module function: {str(e)}")
        return None

# Main function to run the dashboard
def main():
    st.title("SNT Dashboard")
    
    # If a module is selected, execute it
    if st.session_state.current_module:
        try:
            # Get module path
            base_dir = os.path.abspath(os.path.dirname(__file__))
            module_path = os.path.join(base_dir, "pages", st.session_state.current_module)
            
            # Back button
            if st.button("← Back to Dashboard"):
                st.session_state.current_module = None
                st.experimental_rerun()
            
            # Create and run the module function
            run_function = create_module_function(module_path)
            if run_function:
                run_function()
            else:
                st.error(f"Could not create a runnable function from {st.session_state.current_module}")
            
            return
        except Exception as e:
            st.error(f"Error running module: {str(e)}")
            st.code(f"Details: {type(e).__name__}: {str(e)}", language="python")
            
            if st.button("← Back to Dashboard"):
                st.session_state.current_module = None
                st.experimental_rerun()
    
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
