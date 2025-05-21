# app.py - Main dashboard file
import streamlit as st
import importlib
import os
import sys
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="SNT Dashboard",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create directory structure if it doesn't exist
def create_directory_structure():
    # Create modules directory if it doesn't exist
    if not os.path.exists("modules"):
        os.makedirs("modules")
        
    # Create __init__.py file in modules directory
    init_file = Path("modules/__init__.py")
    if not init_file.exists():
        init_file.touch()
    
    # List of module files we'll create
    module_files = [
        "data_analysis.py",
        "data_visualization.py",
        "machine_learning.py",
        "data_processing.py",
        "statistics.py",
        "reporting.py",
        "file_management.py",
        "settings.py",
        "user_management.py",
        "dashboard_home.py"
    ]
    
    # Create each module file if it doesn't exist
    for file in module_files:
        module_path = Path(f"modules/{file}")
        if not module_path.exists():
            with open(module_path, "w") as f:
                f.write(f"""# {file}
import streamlit as st

def run():
    st.title("{file.replace('.py', '').replace('_', ' ').title()}")
    
    # Add back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_module = None
        st.experimental_rerun()
    
    st.write("This is the {file.replace('.py', '').replace('_', ' ')} module.")
    
    # Add sample content specific to each module
    content_generator('{file.replace('.py', '')}')
    
def content_generator(module_name):
    """Generate sample content based on the module name"""
    if module_name == 'data_analysis':
        st.subheader("Sample Data Analysis")
        st.write("Here you can perform exploratory data analysis on your datasets.")
        st.code('''
import pandas as pd
import numpy as np

# Load your data
data = pd.read_csv('your_data.csv')

# Display basic statistics
data.describe()
        ''')
        
    elif module_name == 'data_visualization':
        st.subheader("Data Visualization Tools")
        st.write("Create various plots and charts to visualize your data.")
        
        chart_data = pd.DataFrame(
            np.random.randn(20, 3),
            columns=['A', 'B', 'C'])
        
        st.line_chart(chart_data)
        
    elif module_name == 'machine_learning':
        st.subheader("Machine Learning Models")
        st.write("Train and evaluate machine learning models.")
        st.code('''
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Evaluate
accuracy = accuracy_score(y_test, model.predict(X_test))
        ''')
        
    elif module_name == 'data_processing':
        st.subheader("Data Processing Pipeline")
        st.write("Clean, transform, and prepare your data for analysis.")
        st.code('''
# Data cleaning example
def clean_data(df):
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Handle missing values
    df = df.fillna(df.mean())
    
    # Remove outliers
    # ...
    
    return df
        ''')
        
    elif module_name == 'statistics':
        st.subheader("Statistical Analysis")
        st.write("Perform statistical tests and analysis on your data.")
        
        import numpy as np
        
        data = np.random.normal(0, 1, 1000)
        st.write("Sample statistics for normal distribution:")
        st.write(f"Mean: {np.mean(data):.4f}")
        st.write(f"Standard Deviation: {np.std(data):.4f}")
        st.write(f"Min: {np.min(data):.4f}")
        st.write(f"Max: {np.max(data):.4f}")
        
    elif module_name == 'reporting':
        st.subheader("Automated Reports")
        st.write("Generate and export reports from your data.")
        
        st.download_button(
            label="Download Sample Report",
            data="This is a sample report content",
            file_name="sample_report.txt",
            mime="text/plain"
        )
        
    elif module_name == 'file_management':
        st.subheader("File Management")
        st.write("Upload, download, and manage your data files.")
        
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            st.write("Filename:", uploaded_file.name)
            st.write("File size:", uploaded_file.size, "bytes")
            
    elif module_name == 'settings':
        st.subheader("Dashboard Settings")
        st.write("Configure your dashboard preferences.")
        
        st.selectbox("Theme", ["Light", "Dark", "Custom"])
        st.slider("Update frequency (minutes)", 1, 60, 5)
        st.checkbox("Enable notifications")
        
    elif module_name == 'user_management':
        st.subheader("User Management")
        st.write("Manage user accounts and permissions.")
        
        st.text_input("Username")
        st.text_input("Password", type="password")
        st.selectbox("User Role", ["Admin", "Analyst", "Viewer"])
        
    elif module_name == 'dashboard_home':
        st.subheader("Dashboard Overview")
        st.write("Welcome to the SNT Dashboard!")
        
        st.metric(label="Active Users", value="42", delta="4")
        st.metric(label="Processed Data", value="1.2 GB", delta="0.3 GB")
        st.metric(label="Models Deployed", value="7", delta="-1")
""")

# Create needed directories and files
create_directory_structure()

# Initialize session state for module navigation
if 'current_module' not in st.session_state:
    st.session_state.current_module = None

# Main function to run the dashboard
def main():
    st.title("SNT Dashboard")
    
    # If a module is selected, import and run it
    if st.session_state.current_module:
        try:
            # Import the selected module dynamically
            module = importlib.import_module(f"modules.{st.session_state.current_module}")
            # Run the module
            module.run()
            return
        except ImportError as e:
            st.error(f"Error loading module: {e}")
    
    # Otherwise, show the main dashboard with the 10 boxes
    st.header("Select a Module")
    
    # Define the modules with their descriptions and icons
    modules = {
        "data_analysis": {"icon": "📊", "desc": "Analyze your data with various techniques"},
        "data_visualization": {"icon": "📈", "desc": "Create insightful visualizations"},
        "machine_learning": {"icon": "🤖", "desc": "Train and deploy ML models"},
        "data_processing": {"icon": "⚙️", "desc": "Process and transform your data"},
        "statistics": {"icon": "📉", "desc": "Statistical analysis and testing"},
        "reporting": {"icon": "📝", "desc": "Generate automated reports"},
        "file_management": {"icon": "📁", "desc": "Manage your data files"},
        "settings": {"icon": "⚙️", "desc": "Configure dashboard settings"},
        "user_management": {"icon": "👥", "desc": "Manage users and permissions"},
        "dashboard_home": {"icon": "🏠", "desc": "Dashboard overview and metrics"}
    }
    
    # Create a grid of 2x5 using columns
    col1, col2 = st.columns(2)
    
    # First row
    with col1:
        create_module_tiles(list(modules.items())[:5])
    
    # Second row
    with col2:
        create_module_tiles(list(modules.items())[5:])

def create_module_tiles(module_items):
    for name, info in module_items:
        # Create a card-like container for each module
        with st.container():
            st.markdown(f"""
            <div style="padding: 10px; border-radius: 5px; border: 1px solid #ddd; margin-bottom: 10px;">
                <h3>{info['icon']} {name.replace('_', ' ').title()}</h3>
                <p>{info['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Button to open the module
            if st.button(f"Open {name.replace('_', ' ').title()}", key=f"btn_{name}"):
                st.session_state.current_module = name
                st.experimental_rerun()

if __name__ == "__main__":
    main()
