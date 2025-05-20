import streamlit as st
import pandas as pd
import io
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
    
    .computation-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .new-computation-container {
        background-color: #e8f5e9;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #4caf50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stats-container {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #b3d9ff;
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
    
    .operation-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    
    .addition-badge {
        background-color: #d4edda;
        color: #155724;
    }
    
    .subtraction-badge {
        background-color: #f8d7da;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🧮 Compute New Variables Tool</h1>
    <p>Create new variables by adding or subtracting existing columns</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'original_df' not in st.session_state:
    st.session_state.original_df = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = ""
if 'computations' not in st.session_state:
    st.session_state.computations = []
if 'used_variables' not in st.session_state:
    st.session_state.used_variables = set()
if 'computations_applied' not in st.session_state:
    st.session_state.computations_applied = False

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
            st.session_state.df = df.copy()
            st.session_state.original_df = df.copy()
            st.session_state.file_name = uploaded_file.name
            
            # Reset computations for new file
            st.session_state.computations = []
            st.session_state.used_variables = set()
            st.session_state.computations_applied = False
            
            st.success(f"✅ File uploaded successfully!")
            st.info(f"📊 **File:** {uploaded_file.name}")
            st.info(f"📏 **Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
            
            # Show numeric columns info
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            st.info(f"🔢 **Numeric columns:** {len(numeric_cols)}")
            
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")

# Main content
if st.session_state.df is not None:
    df = st.session_state.df
    
    # Get numeric columns only
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    available_columns = [col for col in numeric_columns if col not in st.session_state.used_variables]
    
    st.header("🧮 Create New Variables")
    
    # Show existing computations
    if st.session_state.computations:
        st.subheader("📋 Existing Computations")
        
        for i, comp in enumerate(st.session_state.computations):
            st.markdown(f"""
            <div class="computation-container">
                <h4>🔢 {comp['new_variable']}</h4>
                <span class="operation-badge {'addition-badge' if comp['operation'] == 'Addition' else 'subtraction-badge'}">
                    {comp['operation']}
                </span>
                <p><strong>Formula:</strong> {comp['formula']}</p>
                <p><strong>Variables used:</strong> {', '.join(comp['variables'])}</p>
                <small><strong>Created:</strong> {comp['timestamp']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # New computation section
    st.markdown("""
    <div class="new-computation-container">
        <h3>➕ Add New Computation</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if len(available_columns) < 2:
        st.markdown("""
        <div class="warning-message">
            ⚠️ <strong>Not enough variables available!</strong> 
            You need at least 2 numeric columns to create computations.
            Available columns: {col_count}
        </div>
        """.format(col_count=len(available_columns)), unsafe_allow_html=True)
        
        if available_columns:
            st.write("**Available columns:**", available_columns)
    else:
        # Create two columns for the interface
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🏷️ New Variable Name")
            new_variable_name = st.text_input(
                "Variable Name",
                placeholder="Enter new variable name (e.g., total_cases)",
                help="Enter a name for your new computed variable"
            )
            
            # Operation selection
            st.subheader("🔄 Operation Type")
            operation = st.radio(
                "Choose operation:",
                ["Addition", "Subtraction"],
                help="Addition: sum all selected variables | Subtraction: subtract second from first (min 0)"
            )
        
        with col2:
            st.subheader("📊 Select Variables")
            
            if operation == "Addition":
                selected_vars = st.multiselect(
                    "Select variables to add:",
                    available_columns,
                    help="Select 2 or more variables to add together"
                )
                min_vars = 2
                max_vars = len(available_columns)
            else:  # Subtraction
                selected_vars = st.multiselect(
                    "Select exactly 2 variables:",
                    available_columns,
                    help="First variable - Second variable (result will be >= 0)"
                )
                min_vars = 2
                max_vars = 2
            
            # Validation
            if selected_vars:
                if operation == "Addition":
                    formula = " + ".join(selected_vars)
                    if len(selected_vars) >= 2:
                        st.success(f"✅ Formula: **{formula}**")
                    else:
                        st.warning(f"⚠️ Select at least 2 variables for addition")
                else:  # Subtraction
                    if len(selected_vars) == 2:
                        formula = f"{selected_vars[0]} - {selected_vars[1]}"
                        st.success(f"✅ Formula: **{formula}** (minimum 0)")
                    elif len(selected_vars) > 2:
                        st.error(f"❌ Select exactly 2 variables for subtraction")
                    else:
                        st.warning(f"⚠️ Select exactly 2 variables for subtraction")
        
        # Add computation button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            can_add = (
                new_variable_name.strip() != "" and
                len(selected_vars) >= min_vars and
                len(selected_vars) <= max_vars and
                new_variable_name not in df.columns and
                new_variable_name not in [comp['new_variable'] for comp in st.session_state.computations]
            )
            
            if st.button("➕ **ADD COMPUTATION**", 
                        type="primary", 
                        disabled=not can_add,
                        help="Add this computation to the list",
                        use_container_width=True):
                
                # Create computation record
                computation = {
                    'new_variable': new_variable_name.strip(),
                    'operation': operation,
                    'variables': selected_vars,
                    'formula': formula,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Add to computations list
                st.session_state.computations.append(computation)
                
                # Add variables to used set
                st.session_state.used_variables.update(selected_vars)
                
                st.success(f"✅ Computation added: **{new_variable_name}**")
                st.rerun()
            
            # Show validation messages
            if new_variable_name.strip() == "":
                st.error("❌ Please enter a variable name")
            elif new_variable_name in df.columns:
                st.error("❌ Variable name already exists in the dataset")
            elif new_variable_name in [comp['new_variable'] for comp in st.session_state.computations]:
                st.error("❌ Variable name already used in computations")
            elif len(selected_vars) < min_vars:
                st.error(f"❌ Select at least {min_vars} variables")
            elif len(selected_vars) > max_vars:
                st.error(f"❌ Select at most {max_vars} variables")
    
    # Apply computations section
    if st.session_state.computations:
        st.markdown("---")
        st.subheader("🚀 Apply All Computations")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 **APPLY ALL COMPUTATIONS**", 
                        type="primary",
                        help="Apply all computations to create new variables",
                        use_container_width=True):
                
                try:
                    # Start with original dataframe
                    result_df = st.session_state.original_df.copy()
                    
                    # Apply each computation
                    for comp in st.session_state.computations:
                        if comp['operation'] == 'Addition':
                            # Addition: sum all selected variables
                            result_df[comp['new_variable']] = result_df[comp['variables']].sum(axis=1)
                        else:  # Subtraction
                            # Subtraction: first - second, minimum 0
                            var1, var2 = comp['variables'][0], comp['variables'][1]
                            result_df[comp['new_variable']] = (result_df[var1] - result_df[var2]).clip(lower=0)
                    
                    # Update session state
                    st.session_state.df = result_df
                    st.session_state.computations_applied = True
                    
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
    
    # Show results after applying computations
    if st.session_state.computations_applied:
        st.markdown("---")
        st.subheader("📊 Results Summary")
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Original Columns", len(st.session_state.original_df.columns))
        with col2:
            st.metric("New Columns", len(st.session_state.computations))
        with col3:
            st.metric("Total Columns", len(st.session_state.df.columns))
        with col4:
            st.metric("Variables Used", len(st.session_state.used_variables))
        
        # Download section
        st.markdown("---")
        st.subheader("💾 Download Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download as CSV
            csv_buffer = io.StringIO()
            st.session_state.df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name="computed_variables.csv",
                mime="text/csv",
                help="Download data with computed variables as CSV"
            )
        
        with col2:
            # Download as Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                st.session_state.df.to_excel(writer, sheet_name='Data with Computed Variables', index=False)
            excel_data = excel_buffer.getvalue()
            
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name="computed_variables.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download data with computed variables as Excel"
            )
        
        with col3:
            # Download computations log
            computations_df = pd.DataFrame(st.session_state.computations)
            comp_csv = computations_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Log",
                data=comp_csv,
                file_name="computations_log.csv",
                mime="text/csv",
                help="Download computations log"
            )
    
    # Data preview section
    if st.checkbox("👀 Show Data Preview", help="Preview first 10 rows of data"):
        st.markdown("---")
        st.subheader("📊 Data Preview")
        
        # Show new columns first if they exist
        if st.session_state.computations_applied:
            new_columns = [comp['new_variable'] for comp in st.session_state.computations]
            reordered_columns = new_columns + [col for col in st.session_state.df.columns if col not in new_columns]
            preview_df = st.session_state.df[reordered_columns]
            
            st.info(f"💡 Showing data with {len(new_columns)} new computed variables (highlighted first)")
        else:
            preview_df = st.session_state.df
            st.info("💡 Showing original data. Apply computations to see new variables.")
        
        st.dataframe(
            preview_df.head(10),
            use_container_width=True,
            height=400
        )
    
    # Reset computations button
    if st.session_state.computations:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🗑️ **RESET ALL COMPUTATIONS**", 
                        help="Clear all computations and start over",
                        use_container_width=True):
                st.session_state.computations = []
                st.session_state.used_variables = set()
                st.session_state.computations_applied = False
                st.session_state.df = st.session_state.original_df.copy()
                st.rerun()

else:
    # Show instructions when no file is uploaded
    st.markdown("""
    <div class="upload-box">
        <h3>📁 No file uploaded yet</h3>
        <p>Please upload a CSV or Excel file using the sidebar to get started.</p>
        <p><strong>Requirements:</strong> File must contain at least 2 numeric columns</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show features
    st.subheader("✨ Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🧮 Computation Types:**
        - **Addition**: Sum 2+ variables
        - **Subtraction**: Subtract second from first (min 0)
        
        **🔒 Smart Validation:**
        - Variables can only be used once
        - Duplicate names prevented
        - Type checking for numeric columns
        """)
    
    with col2:
        st.markdown("""
        **📊 Advanced Features:**
        - **Multi-step workflow**: Add → Apply → Download
        - **Real-time preview**: See formulas as you build
        - **Computation log**: Track all operations
        - **Reset functionality**: Start over anytime
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🧮 Built with Streamlit | Compute New Variables Tool v1.0</p>
</div>
""", unsafe_allow_html=True)
