import streamlit as st
import importlib
import os
import sys

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

# Main function to run the dashboard
def main():
    st.title("SNT Dashboard")
    
    # If a module is selected, import and run it
    if st.session_state.current_module:
        try:
            # Extract module name without .py extension
            module_name = st.session_state.current_module.replace('.py', '')
            
            # Add current directory to path for imports
            base_dir = os.path.abspath(os.path.dirname(__file__))
            if base_dir not in sys.path:
                sys.path.append(base_dir)
            
            # Import the selected module with special handling for set_page_config
            # We need to modify the module's globals to skip the set_page_config call
            import types
            
            # First, we'll create a fake streamlit module that ignores set_page_config
            fake_st = types.ModuleType('streamlit')
            
            # Copy all attributes from the real streamlit module
            for attr in dir(st):
                if attr != '__name__':  # Keep the original module name
                    setattr(fake_st, attr, getattr(st, attr))
            
            # Replace set_page_config with a no-op function
            def dummy_set_page_config(*args, **kwargs):
                pass
            
            fake_st.set_page_config = dummy_set_page_config
            
            # Store the original module
            original_st = sys.modules.get('streamlit')
            
            # Replace streamlit with our fake module temporarily
            sys.modules['streamlit'] = fake_st
            
            # Now import the module (it will use our fake streamlit)
            module = importlib.import_module(f"pages.{module_name}")
            
            # Restore the original streamlit module
            sys.modules['streamlit'] = original_st
            
            # Add a back button
            if st.button("← Back to Dashboard"):
                st.session_state.current_module = None
                st.experimental_rerun()
                
            # Run the module
            if hasattr(module, 'run'):
                module.run()
            else:
                # If run() doesn't exist, try to execute the module's code anyways
                # by calling all functions that seem like main functions
                executed = False
                
                # For compute_new.py, we need to re-initialize session state
                # This seems to be needed by your compute_new module
                if module_name == "compute_new" and hasattr(module, 'st'):
                    # The standard session state variables from compute_new.py
                    session_vars = ['df', 'original_df', 'num_computations', 
                                   'computations', 'used_variables', 'computed_df', 
                                   'computations_applied']
                    
                    # Initialize any missing variables
                    for var in session_vars:
                        if var not in st.session_state:
                            st.session_state[var] = None
                    
                    executed = True
                
                # Look for main function or content at module level
                if hasattr(module, 'main'):
                    module.main()
                    executed = True
                
                if not executed:
                    st.error(f"Module '{module_name}' doesn't have a run() or main() function")
                    st.info("Please modify your module to include a run() function that contains all the main code.")
            
            return
        except Exception as e:
            st.error(f"Error loading or running module: {str(e)}")
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
