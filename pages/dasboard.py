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
                module_name = file.replace('.py', '')
                module_title = module_name.replace('_', ' ').title()
                module_desc = module_name.replace('_', ' ')
                f.write(f"# {file}\n")
                f.write("import streamlit as st\n\n")
                f.write("def run():\n")
                f.write(f"    st.title(\"{module_title}\")\n\n")
                f.write("    # Add back button\n")
                f.write("    if st.button(\"← Back to Dashboard\"):\n")
                f.write("        st.session_state.current_module = None\n")
                f.write("        st.experimental_rerun()\n\n")
                f.write(f"    st.write(\"This is the {module_desc} module.\")\n\n")
                f.write("    # Add sample content specific to each module\n")
                f.write(f"    content_generator('{module_name}')\n\n")
                f.write("def content_generator(module_name):\n")
                f.write("    \"\"\"Generate sample content based on the module name\"\"\"\n")
                f.write("    if module_name == 'data_analysis':\n")
                f.write("        st.subheader(\"Sample Data Analysis\")\n")
                f.write("        st.write(\"Here you can perform exploratory data analysis on your datasets.\")\n")
                f.write("        st.code(\"\"\"\n")
                f.write("import pandas as pd\n")
                f.write("import numpy as np\n\n")
                f.write("# Load your data\n")
                f.write("data = pd.read_csv('your_data.csv')\n\n")
                f.write("# Display basic statistics\n")
                f.write("data.describe()\n")
                f.write("        \"\"\")\n")
        
                f.write("    elif module_name == 'data_visualization':\n")
                f.write("        st.subheader(\"Data Visualization Tools\")\n")
                f.write("        st.write(\"Create various plots and charts to visualize your data.\")\n")
                f.write("        \n")
                f.write("        import pandas as pd\n")
                f.write("        import numpy as np\n")
                f.write("        \n")
                f.write("        chart_data = pd.DataFrame(\n")
                f.write("            np.random.randn(20, 3),\n")
                f.write("            columns=['A', 'B', 'C'])\n")
                f.write("        \n")
                f.write("        st.line_chart(chart_data)\n")
        
                f.write("    elif module_name == 'machine_learning':\n")
                f.write("        st.subheader(\"Machine Learning Models\")\n")
                f.write("        st.write(\"Train and evaluate machine learning models.\")\n")
                f.write("        st.code(\"\"\"\n")
                f.write("from sklearn.model_selection import train_test_split\n")
                f.write("from sklearn.ensemble import RandomForestClassifier\n")
                f.write("from sklearn.metrics import accuracy_score\n\n")
                f.write("# Split data\n")
                f.write("X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)\n\n")
                f.write("# Train model\n")
                f.write("model = RandomForestClassifier()\n")
                f.write("model.fit(X_train, y_train)\n\n")
                f.write("# Evaluate\n")
                f.write("accuracy = accuracy_score(y_test, model.predict(X_test))\n")
                f.write("        \"\"\")\n")
        
                f.write("    elif module_name == 'data_processing':\n")
                f.write("        st.subheader(\"Data Processing Pipeline\")\n")
                f.write("        st.write(\"Clean, transform, and prepare your data for analysis.\")\n")
                f.write("        st.code(\"\"\"\n")
                f.write("# Data cleaning example\n")
                f.write("def clean_data(df):\n")
                f.write("    # Remove duplicates\n")
                f.write("    df = df.drop_duplicates()\n")
                f.write("    \n")
                f.write("    # Handle missing values\n")
                f.write("    df = df.fillna(df.mean())\n")
                f.write("    \n")
                f.write("    # Remove outliers\n")
                f.write("    # ...\n")
                f.write("    \n")
                f.write("    return df\n")
                f.write("        \"\"\")\n")
        
                f.write("    elif module_name == 'statistics':\n")
                f.write("        st.subheader(\"Statistical Analysis\")\n")
                f.write("        st.write(\"Perform statistical tests and analysis on your data.\")\n")
                f.write("        \n")
                f.write("        import numpy as np\n")
                f.write("        \n")
                f.write("        data = np.random.normal(0, 1, 1000)\n")
                f.write("        st.write(\"Sample statistics for normal distribution:\")\n")
                f.write("        st.write(f\"Mean: {np.mean(data):.4f}\")\n")
                f.write("        st.write(f\"Standard Deviation: {np.std(data):.4f}\")\n")
                f.write("        st.write(f\"Min: {np.min(data):.4f}\")\n")
                f.write("        st.write(f\"Max: {np.max(data):.4f}\")\n")
        
                f.write("    elif module_name == 'reporting':\n")
                f.write("        st.subheader(\"Automated Reports\")\n")
                f.write("        st.write(\"Generate and export reports from your data.\")\n")
                f.write("        \n")
                f.write("        st.download_button(\n")
                f.write("            label=\"Download Sample Report\",\n")
                f.write("            data=\"This is a sample report content\",\n")
                f.write("            file_name=\"sample_report.txt\",\n")
                f.write("            mime=\"text/plain\"\n")
                f.write("        )\n")
        
                f.write("    elif module_name == 'file_management':\n")
                f.write("        st.subheader(\"File Management\")\n")
                f.write("        st.write(\"Upload, download, and manage your data files.\")\n")
                f.write("        \n")
                f.write("        uploaded_file = st.file_uploader(\"Choose a file\")\n")
                f.write("        if uploaded_file is not None:\n")
                f.write("            st.write(\"Filename:\", uploaded_file.name)\n")
                f.write("            st.write(\"File size:\", uploaded_file.size, \"bytes\")\n")
            
                f.write("    elif module_name == 'settings':\n")
                f.write("        st.subheader(\"Dashboard Settings\")\n")
                f.write("        st.write(\"Configure your dashboard preferences.\")\n")
                f.write("        \n")
                f.write("        st.selectbox(\"Theme\", [\"Light\", \"Dark\", \"Custom\"])\n")
                f.write("        st.slider(\"Update frequency (minutes)\", 1, 60, 5)\n")
                f.write("        st.checkbox(\"Enable notifications\")\n")
        
                f.write("    elif module_name == 'user_management':\n")
                f.write("        st.subheader(\"User Management\")\n")
                f.write("        st.write(\"Manage user accounts and permissions.\")\n")
                f.write("        \n")
                f.write("        st.text_input(\"Username\")\n")
                f.write("        st.text_input(\"Password\", type=\"password\")\n")
                f.write("        st.selectbox(\"User Role\", [\"Admin\", \"Analyst\", \"Viewer\"])\n")
        
                f.write("    elif module_name == 'dashboard_home':\n")
                f.write("        st.subheader(\"Dashboard Overview\")\n")
                f.write("        st.write(\"Welcome to the SNT Dashboard!\")\n")
                f.write("        \n")
                f.write("        st.metric(label=\"Active Users\", value=\"42\", delta=\"4\")\n")
                f.write("        st.metric(label=\"Processed Data\", value=\"1.2 GB\", delta=\"0.3 GB\")\n")
                f.write("        st.metric(label=\"Models Deployed\", value=\"7\", delta=\"-1\")\n")
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
