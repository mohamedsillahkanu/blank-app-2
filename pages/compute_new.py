import streamlit as st
import pandas as pd
import io
import numpy as np
from datetime import datetime

# Set page config for better layout
st.set_page_config(
    page_title="Compute New Variables Tool",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 1rem 1rem;
    }
    
    .upload-box {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
    
    .variable-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        border: 1px solid #e0e0e0;
    }
    
    .compute-container {
        background-color: #fff;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    
    .operation-box {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #b3d9ff;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🧮 Compute New Variables Tool</h1>
    <p>Upload your data file and create new computed variables</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'original_columns' not in st.session_state:
    st.session_state.original_columns = []
if 'computed_variables' not in st.session_state:
    st.session_state.computed_variables = []
if 'pending_computations' not in st.session_state:
    st.session_state.pending_computations = []
if 'file_name' not in st.session_state:
    st.session_state.file_name = ""
if 'computation_applied' not in st.session_state:
    st.session_state.computation_applied = False

# Sidebar for file upload
with st.sidebar:
    st.header("📁 File Upload")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload CSV or Excel files"
    )
    
    if uploaded_file is not None:
        try:
            # Read the file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Store in session state
            st.session_state.df = df
            st.session_state.original_columns = list(df.columns)
            st.session_state.file_name = uploaded_file.name
            
            # Reset computation states for new file
            st.session_state.computed_variables = []
            st.session_state.pending_computations = []
            st.session_state.computation_applied = False
            
            st.success(f"✅ File uploaded successfully!")
            st.info(f"📊 **File:** {uploaded_file.name}")
            st.info(f"📏 **Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
            
            # Show numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            st.info(f"🔢 **Numeric columns:** {len(numeric_cols)}")
            
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")

# Main content
if st.session_state.df is not None:
    df = st.session_state.df
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        st.error("❌ No numeric columns found in the dataset. Please upload a file with numeric data.")
    else:
        # Create computation interface
        st.markdown("""
        <div class="compute-container">
            <h3>➕ Create New Computed Variable</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Three columns layout for creating new variables
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.subheader("🏷️ Variable Name")
            new_var_name = st.text_input(
                "Enter new variable name",
                placeholder="e.g., total_cases, difference_score",
                help="Enter a unique name for your new computed variable"
            )
        
        with col2:
            st.subheader("🔢 Operation Type")
            operation = st.selectbox(
                "Choose operation",
                ["Addition", "Subtraction"],
                help="Addition: sum all selected variables | Subtraction: subtract second from first"
            )
        
        with col3:
            st.subheader("📊 Select Variables")
            if operation == "Addition":
                selected_vars = st.multiselect(
                    "Select variables to add",
                    options=numeric_cols,
                    help="Select 2 or more variables to add together"
                )
                max_vars = len(numeric_cols)
                min_vars = 2
            else:  # Subtraction
                selected_vars = st.multiselect(
                    "Select exactly 2 variables",
                    options=numeric_cols,
                    max_selections=2,
                    help="Select exactly 2 variables: result = first - second"
                )
                max_vars = 2
                min_vars = 2
        
        # Add variable button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("➕ Add to Pending Computations", 
                        type="secondary", 
                        use_container_width=True):
                
                # Validation
                errors = []
                if not new_var_name:
                    errors.append("Please enter a variable name")
                elif new_var_name in df.columns:
                    errors.append(f"Variable '{new_var_name}' already exists in the dataset")
                elif new_var_name in [comp['name'] for comp in st.session_state.pending_computations]:
                    errors.append(f"Variable '{new_var_name}' already exists in pending computations")
                elif not new_var_name.replace('_', '').replace('-', '').isalnum():
                    errors.append("Variable name should contain only letters, numbers, underscores, and hyphens")
                
                if len(selected_vars) < min_vars:
                    errors.append(f"{operation} requires at least {min_vars} variables")
                elif operation == "Subtraction" and len(selected_vars) != 2:
                    errors.append("Subtraction requires exactly 2 variables")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    # Add to pending computations
                    computation = {
                        'name': new_var_name,
                        'operation': operation,
                        'variables': selected_vars,
                        'formula': f"{' + '.join(selected_vars)}" if operation == "Addition" else f"{selected_vars[0]} - {selected_vars[1]}"
                    }
                    st.session_state.pending_computations.append(computation)
                    st.success(f"✅ Added '{new_var_name}' to pending computations!")
                    st.rerun()
        
        # Show pending computations
        if st.session_state.pending_computations:
            st.markdown("---")
            st.subheader("⏳ Pending Computations")
            
            for i, comp in enumerate(st.session_state.pending_computations):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    if comp['operation'] == "Addition":
                        operation_color = "blue"
                        operation_symbol = "+"
                    else:
                        operation_color = "orange"
                        operation_symbol = "-"
                    
                    st.markdown(f"""
                    <div class="variable-container">
                        <strong>🏷️ Variable:</strong> {comp['name']}<br>
                        <strong>🔢 Operation:</strong> <span style="color: {operation_color};">{comp['operation']}</span><br>
                        <strong>📊 Variables:</strong> {', '.join(comp['variables'])}<br>
                        <strong>📝 Formula:</strong> <code>{comp['name']} = {comp['formula']}</code>
                        {' (negative values replaced with 0)' if comp['operation'] == 'Subtraction' else ''}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"🗑️ Remove", key=f"remove_{i}", help=f"Remove {comp['name']} from pending"):
                        st.session_state.pending_computations.pop(i)
                        st.rerun()
            
            # Apply computations button
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.button("🧮 **APPLY ALL COMPUTATIONS**", 
                           type="primary", 
                           help="Apply all pending computations to create new variables",
                           use_container_width=True):
                    
                    try:
                        # Apply all computations
                        new_df = df.copy()
                        
                        for comp in st.session_state.pending_computations:
                            if comp['operation'] == "Addition":
                                # Addition: sum all selected variables
                                new_df[comp['name']] = new_df[comp['variables']].sum(axis=1)
                            else:
                                # Subtraction: first - second, replace negative with 0
                                result = new_df[comp['variables'][0]] - new_df[comp['variables'][1]]
                                new_df[comp['name']] = result.clip(lower=0)  # Replace negative with 0
                        
                        # Update session state
                        st.session_state.df = new_df
                        st.session_state.computed_variables.extend(st.session_state.pending_computations)
                        st.session_state.pending_computations = []
                        st.session_state.computation_applied = True
                        
                        st.markdown("""
                        <div class="success-message">
                            ✅ <strong>Success!</strong> All computations have been applied successfully!
                        </div>
                        """, unsafe_allow_html=True)
                        st.rerun()
                        
                    except Exception as e:
                        st.markdown(f"""
                        <div class="error-message">
                            ❌ <strong>Error applying computations:</strong> {str(e)}
                        </div>
                        """, unsafe_allow_html=True)
        
        # Show applied computations and download options
        if st.session_state.computed_variables:
            st.markdown("---")
            st.subheader("✅ Applied Computations")
            
            # Show applied computations summary
            applied_df = pd.DataFrame([
                {
                    "Variable Name": comp['name'],
                    "Operation": comp['operation'],
                    "Variables Used": ', '.join(comp['variables']),
                    "Formula": comp['formula']
                }
                for comp in st.session_state.computed_variables
            ])
            
            st.dataframe(applied_df, use_container_width=True)
            
            # Download section
            st.markdown("---")
            st.subheader("💾 Download Data with New Variables")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Download as CSV
                csv_buffer = io.StringIO()
                st.session_state.df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="computed_variables_data.csv",
                    mime="text/csv",
                    help="Download data with computed variables as CSV file"
                )
            
            with col2:
                # Download as Excel
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    st.session_state.df.to_excel(writer, sheet_name='Data with New Variables', index=False)
                excel_data = excel_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name="computed_variables_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Download data with computed variables as Excel file"
                )
            
            with col3:
                # Download computation log
                computation_log = pd.DataFrame([
                    {
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Variable_Name": comp['name'],
                        "Operation": comp['operation'],
                        "Source_Variables": ', '.join(comp['variables']),
                        "Formula": comp['formula'],
                        "Notes": "Negative values replaced with 0" if comp['operation'] == "Subtraction" else "Sum of selected variables"
                    }
                    for comp in st.session_state.computed_variables
                ])
                
                log_csv = computation_log.to_csv(index=False)
                st.download_button(
                    label="📥 Download Log",
                    data=log_csv,
                    file_name="computation_log.csv",
                    mime="text/csv",
                    help="Download computation history log"
                )
        
        # Data preview section
        if st.checkbox("👀 Show Data Preview", help="Preview first 10 rows with computed variables"):
            st.markdown("---")
            st.subheader("📊 Data Preview")
            
            # Show preview
            preview_df = st.session_state.df.head(10)
            st.dataframe(preview_df, use_container_width=True, height=400)
            
            # Highlight new variables
            if st.session_state.computed_variables:
                new_vars = [comp['name'] for comp in st.session_state.computed_variables]
                st.markdown(f"""
                <div class="success-message">
                    🆕 <strong>New computed variables:</strong> {', '.join(new_vars)}
                </div>
                """, unsafe_allow_html=True)
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", f"{len(st.session_state.df):,}")
            with col2:
                st.metric("Total Columns", f"{len(st.session_state.df.columns):,}")
            with col3:
                st.metric("Computed Variables", f"{len(st.session_state.computed_variables):,}")
            with col4:
                memory_usage = st.session_state.df.memory_usage(deep=True).sum() / 1024 / 1024
                st.metric("Memory Usage", f"{memory_usage:.1f} MB")

else:
    # Show instructions when no file is uploaded
    st.markdown("""
    <div class="upload-box">
        <h3>📁 No file uploaded yet</h3>
        <p>Please upload a CSV or Excel file using the sidebar to get started.</p>
        <p><strong>Supported formats:</strong> .csv, .xlsx, .xls</p>
        <p><strong>Requirements:</strong> File must contain numeric columns for computations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show features
    st.subheader("✨ Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - **➕ Addition Operations** - Sum multiple variables together
        - **➖ Subtraction Operations** - Subtract one variable from another
        - **🔄 Automatic handling** - Negative values replaced with zero
        - **📊 Variable validation** - Ensures only numeric columns are used
        """)
    
    with col2:
        st.markdown("""
        - **⏳ Pending system** - Review before applying computations
        - **💾 Multiple download formats** - CSV, Excel, computation log
        - **👀 Live preview** - See results before downloading
        - **📝 Formula tracking** - Keep record of all computations
        """)
    
    # Show operation examples
    st.subheader("🧮 Operation Examples")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="operation-box">
            <h4>➕ Addition Example</h4>
            <p><strong>Variables:</strong> cases_2021, cases_2022, cases_2023</p>
            <p><strong>Formula:</strong> total_cases = cases_2021 + cases_2022 + cases_2023</p>
            <p><strong>Result:</strong> Sum of all three variables</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="operation-box">
            <h4>➖ Subtraction Example</h4>
            <p><strong>Variables:</strong> total_population, affected_population</p>
            <p><strong>Formula:</strong> unaffected = total_population - affected_population</p>
            <p><strong>Result:</strong> Difference (negative values become 0)</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🧮 Built with Streamlit | Compute New Variables Tool v1.0</p>
</div>
""", unsafe_allow_html=True)
