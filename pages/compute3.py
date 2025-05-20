import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Set page config
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
    
    .computation-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .variable-tag {
        display: inline-block;
        background-color: #e7f3ff;
        color: #1976d2;
        padding: 0.25rem 0.5rem;
        margin: 0.25rem;
        border-radius: 15px;
        font-size: 0.8rem;
        border: 1px solid #bbdefb;
    }
    
    .operation-badge {
        display: inline-block;
        background-color: #4caf50;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8rem;
    }
    
    .operation-badge.subtract {
        background-color: #ff9800;
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
    
    .compute-btn {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🧮 Compute New Variables Tool</h1>
    <p>Create new calculated variables from existing columns</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'original_df' not in st.session_state:
    st.session_state.original_df = None
if 'computed_df' not in st.session_state:
    st.session_state.computed_df = None
if 'variable_count' not in st.session_state:
    st.session_state.variable_count = 1
if 'variable_configs' not in st.session_state:
    st.session_state.variable_configs = []
if 'used_variables' not in st.session_state:
    st.session_state.used_variables = set()
if 'computations_applied' not in st.session_state:
    st.session_state.computations_applied = False

# Helper functions
def get_available_columns():
    """Get columns that haven't been used in computations"""
    if st.session_state.df is None:
        return []
    
    # Get numeric columns only
    numeric_cols = st.session_state.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    # Remove already used variables
    available_cols = [col for col in numeric_cols if col not in st.session_state.used_variables]
    return available_cols

def validate_computation(new_var_name, selected_vars, operation):
    """Validate a computation configuration"""
    errors = []
    
    # Check if variable name is provided
    if not new_var_name.strip():
        errors.append("Variable name cannot be empty")
    
    # Check if variable name already exists
    if st.session_state.df is not None and new_var_name in st.session_state.df.columns:
        errors.append(f"Variable '{new_var_name}' already exists")
    
    # Check if variable name is already in configurations
    existing_vars = [config['new_variable'] for config in st.session_state.variable_configs if config['new_variable']]
    if new_var_name in existing_vars:
        errors.append(f"Variable '{new_var_name}' is already being computed")
    
    # Check selected variables
    if len(selected_vars) == 0:
        errors.append("Please select at least one variable")
    
    if operation == "Subtraction" and len(selected_vars) != 2:
        errors.append("Subtraction requires exactly 2 variables")
    
    return errors

def compute_variable(df, selected_vars, operation):
    """Compute new variable based on operation"""
    if operation == "Addition":
        return df[selected_vars].sum(axis=1)
    elif operation == "Subtraction":
        result = df[selected_vars[0]] - df[selected_vars[1]]
        # Replace negative values with 0
        return result.clip(lower=0)
    return None

def apply_all_computations():
    """Apply all computations to create computed dataframe"""
    if st.session_state.df is None:
        return None
    
    computed_df = st.session_state.df.copy()
    
    for config in st.session_state.variable_configs:
        if not config['new_variable'] or not config['variables'] or not config['operation']:
            continue
            
        new_var = config['new_variable']
        selected_vars = config['variables']
        operation = config['operation']
        
        # Compute the new variable
        computed_df[new_var] = compute_variable(computed_df, selected_vars, operation)
    
    return computed_df

def initialize_variable_configs(count):
    """Initialize the variable configurations"""
    st.session_state.variable_configs = [
        {
            'new_variable': '',
            'operation': 'Addition',
            'variables': []
        } for _ in range(count)
    ]

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
            st.session_state.original_df = df.copy()
            
            # Reset computations when new file is uploaded
            st.session_state.variable_configs = []
            st.session_state.used_variables = set()
            st.session_state.computed_df = None
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
    
    # Get available columns for new computations
    available_cols = get_available_columns()
    
    # Ask for the number of variables to compute
    st.subheader("Setup Variable Computations")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        variable_count = st.number_input(
            "How many new variables do you want to compute?",
            min_value=1,
            max_value=20,  # Limit to a reasonable number
            value=st.session_state.variable_count
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("Set Up Computations", key="setup_button"):
            st.session_state.variable_count = variable_count
            initialize_variable_configs(variable_count)
            st.rerun()
    
    # Show computation configuration if setup is done
    if st.session_state.variable_configs:
        st.markdown("---")
        st.subheader("📝 Configure Your Computations")
        
        # Track used variables in this configuration session
        currently_used_vars = set()
        
        # Create configurations for each variable
        for i, config in enumerate(st.session_state.variable_configs):
            st.markdown(f"### New Variable {i+1}")
            
            col1, col2, col3 = st.columns([2, 1, 3])
            
            with col1:
                new_var_name = st.text_input(
                    "New Variable Name",
                    value=config['new_variable'],
                    key=f"var_name_{i}"
                )
                st.session_state.variable_configs[i]['new_variable'] = new_var_name
            
            with col2:
                operation = st.selectbox(
                    "Operation",
                    ["Addition", "Subtraction"],
                    index=0 if config['operation'] == 'Addition' else 1,
                    key=f"operation_{i}"
                )
                st.session_state.variable_configs[i]['operation'] = operation
            
            with col3:
                # Determine available columns for this specific computation
                # Exclude variables that have been used in previous configurations in this session
                current_available_cols = [col for col in available_cols if col not in currently_used_vars]
                
                if operation == "Addition":
                    selected_vars = st.multiselect(
                        "Select Variables to Add",
                        options=current_available_cols,
                        default=config['variables'],
                        key=f"selected_vars_{i}"
                    )
                else:  # Subtraction
                    selected_vars = st.multiselect(
                        "Select Variables for Subtraction (First - Second)",
                        options=current_available_cols,
                        default=config['variables'],
                        max_selections=2,
                        key=f"selected_vars_{i}"
                    )
                
                st.session_state.variable_configs[i]['variables'] = selected_vars
                
                # Add these selected variables to currently used vars
                for var in selected_vars:
                    currently_used_vars.add(var)
            
            # Show preview of operation if all required fields are filled
            if new_var_name and selected_vars:
                if operation == "Addition":
                    formula = " + ".join(selected_vars)
                else:  # Subtraction
                    if len(selected_vars) == 2:
                        formula = f"{selected_vars[0]} - {selected_vars[1]} (negative results → 0)"
                    else:
                        formula = "Incomplete: Need exactly 2 variables"
                
                st.markdown(f"""
                <div style="padding: 10px; background-color: #f0f2f6; border-radius: 5px; margin-top: 5px;">
                    <strong>Preview:</strong> {new_var_name} = {formula}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
        
        # Apply computations button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🧮 COMPUTE VARIABLES", type="primary", use_container_width=True):
                # Validate all configurations
                all_valid = True
                errors = []
                
                for i, config in enumerate(st.session_state.variable_configs):
                    config_errors = validate_computation(
                        config['new_variable'],
                        config['variables'],
                        config['operation']
                    )
                    
                    if config_errors:
                        all_valid = False
                        errors.append(f"Variable {i+1}: {', '.join(config_errors)}")
                
                if all_valid:
                    try:
                        # Apply computations
                        st.session_state.computed_df = apply_all_computations()
                        
                        # Mark used variables
                        for config in st.session_state.variable_configs:
                            for var in config['variables']:
                                st.session_state.used_variables.add(var)
                        
                        st.session_state.computations_applied = True
                        st.success("✅ All variables computed successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error computing variables: {str(e)}")
                else:
                    for error in errors:
                        st.error(error)
    
    # Show results if computations have been applied
    if st.session_state.computations_applied and st.session_state.computed_df is not None:
        st.markdown("---")
        st.subheader("📊 Computation Results")
        
        # Display the summary and the computed dataframe
        computed_df = st.session_state.computed_df
        
        # Summary of new variables
        new_vars = [config['new_variable'] for config in st.session_state.variable_configs 
                   if config['new_variable'] and config['variables']]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Variables Created", len(new_vars))
        with col2:
            st.metric("Total Columns", len(computed_df.columns))
        with col3:
            memory_usage = computed_df.memory_usage(deep=True).sum() / 1024 / 1024
            st.metric("Memory Usage", f"{memory_usage:.1f} MB")
        
        # Display computations summary
        st.subheader("Computed Variables Summary")
        
        summary_data = []
        for config in st.session_state.variable_configs:
            if not config['new_variable'] or not config['variables']:
                continue
                
            new_var = config['new_variable']
            
            if config['operation'] == "Addition":
                formula = " + ".join(config['variables'])
            else:  # Subtraction
                formula = f"{config['variables'][0]} - {config['variables'][1]} (negative → 0)"
            
            # Calculate statistics
            col_data = computed_df[new_var]
            summary_data.append({
                'Variable': new_var,
                'Formula': formula,
                'Mean': f"{col_data.mean():.2f}",
                'Min': f"{col_data.min():.2f}",
                'Max': f"{col_data.max():.2f}",
                'Zeros': f"{(col_data == 0).sum()}",
                'Non-null': f"{col_data.count()}"
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
        # Show data preview
        st.subheader("Data Preview")
        st.dataframe(computed_df.head(10), use_container_width=True)
        
        # Download section
        st.markdown("---")
        st.subheader("💾 Download Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download as CSV
            csv_buffer = io.StringIO()
            computed_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"computed_variables_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                help="Download data with computed variables as CSV"
            )
        
        with col2:
            # Download as Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                computed_df.to_excel(writer, sheet_name='Computed Data', index=False)
            excel_data = excel_buffer.getvalue()
            
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name=f"computed_variables_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download data with computed variables as Excel"
            )
        
        with col3:
            # Download only new variables
            new_vars_df = computed_df[new_vars]
            new_vars_csv = new_vars_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download New Variables Only",
                data=new_vars_csv,
                file_name=f"new_variables_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                help="Download only the newly computed variables"
            )

else:
    # Show instructions when no file is uploaded
    st.markdown("""
    <div style="border: 2px dashed #ccc; border-radius: 10px; padding: 2rem; text-align: center; background-color: #f8f9fa; margin: 1rem 0;">
        <h3>📁 No file uploaded yet</h3>
        <p>Please upload a CSV or Excel file using the sidebar to get started.</p>
        <p><strong>Requirements:</strong> File must contain numeric columns for computations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show features
    st.subheader("✨ Tool Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 Computation Options:**
        - **Specify number of variables** you want to compute
        - **Addition:** Sum multiple variables together
        - **Subtraction:** Subtract one variable from another
        - **Smart handling:** Negative results automatically become zero
        """)
    
    with col2:
        st.markdown("""
        **🔒 Smart Constraints:**
        - Variables used in one computation won't appear in subsequent ones
        - Subtraction requires exactly 2 variables
        - Comprehensive validation before computation
        - Easy download in CSV or Excel format
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🧮 Built with Streamlit | Compute New Variables Tool v1.0</p>
</div>
""", unsafe_allow_html=True)
