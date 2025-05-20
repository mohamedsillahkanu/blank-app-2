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
    
    .add-computation-btn {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
    }
    
    .remove-computation-btn {
        background-color: #dc3545;
        color: white;
        border: none;
        padding: 0.25rem 0.5rem;
        border-radius: 3px;
        cursor: pointer;
        font-size: 0.8rem;
    }
    
    .operation-symbol {
        font-size: 1.5rem;
        font-weight: bold;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
    }
    
    .floating-add-button {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background-color: #4285F4;
        color: white;
        font-size: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        cursor: pointer;
        z-index: 1000;
        border: none;
    }
    
    .floating-add-button:hover {
        background-color: #1a73e8;
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    
    .computation-form {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .computation-form-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    
    .new-computation-indicator {
        background-color: #e7f3ff;
        color: #1976d2;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
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
if 'computations' not in st.session_state:
    st.session_state.computations = []
if 'used_variables' not in st.session_state:
    st.session_state.used_variables = set()
if 'computed_df' not in st.session_state:
    st.session_state.computed_df = None
if 'computations_applied' not in st.session_state:
    st.session_state.computations_applied = False
if 'computation_forms' not in st.session_state:
    st.session_state.computation_forms = 1
if 'form_visibility' not in st.session_state:
    st.session_state.form_visibility = [True]
if 'last_operation' not in st.session_state:
    st.session_state.last_operation = None

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
    
    # Check if variable name is already in computations
    existing_vars = [comp['new_variable'] for comp in st.session_state.computations]
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
    
    for computation in st.session_state.computations:
        new_var = computation['new_variable']
        selected_vars = computation['variables']
        operation = computation['operation']
        
        # Compute the new variable
        computed_df[new_var] = compute_variable(computed_df, selected_vars, operation)
    
    return computed_df

def add_new_computation_form():
    """Add a new computation form"""
    st.session_state.computation_forms += 1
    st.session_state.form_visibility.append(True)
    st.session_state.last_operation = "add_form"

def remove_computation_form(form_index):
    """Remove a computation form"""
    st.session_state.form_visibility[form_index] = False
    st.session_state.last_operation = "remove_form"

def reset_form_after_add(form_index):
    """Reset the form inputs after a computation is added"""
    # We'll handle the form reset by using unique keys that include the index
    # The state is automatically reset when the key changes
    pass

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
            st.session_state.computations = []
            st.session_state.used_variables = set()
            st.session_state.computed_df = None
            st.session_state.computations_applied = False
            st.session_state.computation_forms = 1
            st.session_state.form_visibility = [True]
            
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
    
    # Show existing computations
    if st.session_state.computations:
        st.subheader("📝 Configured Computations")
        
        for i, computation in enumerate(st.session_state.computations):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                operation_class = "subtract" if computation['operation'] == "Subtraction" else ""
                vars_html = "".join([f'<span class="variable-tag">{var}</span>' for var in computation['variables']])
                
                st.markdown(f"""
                <div class="computation-card">
                    <h4>{computation['new_variable']} = </h4>
                    <span class="operation-badge {operation_class}">{computation['operation']}</span>
                    <div>{vars_html}</div>
                    {f"<small>Formula: {computation['variables'][0]} - {computation['variables'][1]} (negatives → 0)</small>" if computation['operation'] == "Subtraction" else f"<small>Formula: {' + '.join(computation['variables'])}</small>"}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"❌ Remove", key=f"remove_{i}", help="Remove this computation"):
                    # Remove from used variables
                    for var in computation['variables']:
                        st.session_state.used_variables.discard(var)
                    
                    # Remove computation
                    st.session_state.computations.pop(i)
                    st.session_state.computations_applied = False
                    st.rerun()
    
    # Add new computation forms section
    st.markdown("---")
    st.subheader("➕ New Variable Computations")
    
    if available_cols:
        for form_idx in range(st.session_state.computation_forms):
            if st.session_state.form_visibility[form_idx]:
                with st.container():
                    st.markdown(f"""
                    <div class="computation-form">
                        <div class="computation-form-header">
                            <h4>Computation #{form_idx + 1}</h4>
                            <span class="new-computation-indicator">New</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Form inputs
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        new_var_name = st.text_input(
                            "New Variable Name",
                            key=f"new_var_input_{form_idx}",
                            help="Enter the name for your new calculated variable"
                        )
                    
                    # Column for operation selection with centered operation symbol
                    with col2:
                        operation = st.selectbox(
                            "Operation",
                            ["Addition", "Subtraction"],
                            key=f"operation_{form_idx}",
                            help="Choose the mathematical operation"
                        )
                        
                        # Display operation symbol
                        operation_symbol = "+" if operation == "Addition" else "-"
                        st.markdown(f"""
                        <div class="operation-symbol">
                            {operation_symbol}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        if form_idx > 0:  # Only show remove button for additional forms
                            st.write("") # Spacer
                            st.write("") # Spacer for alignment
                            if st.button("❌", key=f"remove_form_{form_idx}", 
                                        help="Remove this computation form"):
                                remove_computation_form(form_idx)
                                st.rerun()
                    
                    # Variable selection based on operation
                    if operation == "Addition":
                        selected_vars = st.multiselect(
                            "Select Variables to Add",
                            available_cols,
                            key=f"selected_vars_{form_idx}",
                            help="Select all variables you want to add together"
                        )
                    else:  # Subtraction
                        selected_vars = st.multiselect(
                            "Select Variables for Subtraction",
                            available_cols,
                            key=f"selected_vars_{form_idx}",
                            max_selections=2,
                            help="Select exactly 2 variables (first - second). Negative results will be set to 0."
                        )
                        
                        if len(selected_vars) == 2:
                            st.info(f"💡 Formula: {selected_vars[0]} - {selected_vars[1]} (negatives → 0)")
                    
                    # Add computation button
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        if st.button("➕ Add Computation", key=f"add_comp_btn_{form_idx}", 
                                    type="primary", use_container_width=True):
                            # Validate computation
                            errors = validate_computation(new_var_name, selected_vars, operation)
                            
                            if errors:
                                for error in errors:
                                    st.error(f"❌ {error}")
                            else:
                                # Add computation
                                new_computation = {
                                    'new_variable': new_var_name.strip(),
                                    'variables': selected_vars,
                                    'operation': operation
                                }
                                
                                st.session_state.computations.append(new_computation)
                                
                                # Mark variables as used
                                for var in selected_vars:
                                    st.session_state.used_variables.add(var)
                                
                                st.session_state.computations_applied = False
                                reset_form_after_add(form_idx)
                                st.success(f"✅ Computation for '{new_var_name}' added successfully!")
                                st.rerun()
        
        # Add the floating "+" button to add a new computation form
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("➕ Add Another Variable", 
                        key="add_another_variable",
                        help="Add another variable computation form",
                        use_container_width=True):
                add_new_computation_form()
                st.rerun()
        
    else:
        st.markdown("""
        <div class="warning-message">
            ⚠️ <strong>No available numeric columns</strong><br>
            All numeric columns have been used in computations or no numeric columns are available.
        </div>
        """, unsafe_allow_html=True)
    
    # Apply all computations button
    if st.session_state.computations and not st.session_state.computations_applied:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🧮 **COMPUTE ALL VARIABLES**", 
                        type="primary", 
                        help="Apply all computations and create new variables",
                        use_container_width=True):
                try:
                    # Apply all computations
                    st.session_state.computed_df = apply_all_computations()
                    st.session_state.computations_applied = True
                    
                    st.markdown("""
                    <div class="success-message">
                        ✅ <strong>Success!</strong> All computations have been applied successfully!
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error computing variables: {str(e)}")
    
    # Show computed results
    if st.session_state.computations_applied and st.session_state.computed_df is not None:
        st.markdown("---")
        st.subheader("📊 Computation Results")
        
        # Summary of new variables
        new_vars = [comp['new_variable'] for comp in st.session_state.computations]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Variables Created", len(new_vars))
        with col2:
            st.metric("Total Columns", len(st.session_state.computed_df.columns))
        with col3:
            memory_usage = st.session_state.computed_df.memory_usage(deep=True).sum() / 1024 / 1024
            st.metric("Memory Usage", f"{memory_usage:.1f} MB")
        
        # Show summary of new variables with statistics
        if st.checkbox("📈 Show New Variables Summary"):
            summary_data = []
            for var in new_vars:
                col_data = st.session_state.computed_df[var]
                summary_data.append({
                    'Variable': var,
                    'Mean': f"{col_data.mean():.2f}",
                    'Min': f"{col_data.min():.2f}",
                    'Max': f"{col_data.max():.2f}",
                    'Zeros': f"{(col_data == 0).sum()}",
                    'Non-null': f"{col_data.count()}"
                })
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)
        
        # Download section
        st.markdown("---")
        st.subheader("💾 Download Computed Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download as CSV
            csv_buffer = io.StringIO()
            st.session_state.computed_df.to_csv(csv_buffer, index=False)
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
                st.session_state.computed_df.to_excel(writer, sheet_name='Computed Data', index=False)
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
            log_data = []
            for comp in st.session_state.computations:
                if comp['operation'] == 'Addition':
                    formula = ' + '.join(comp['variables'])
                else:
                    formula = f"{comp['variables'][0]} - {comp['variables'][1]} (negatives → 0)"
                
                log_data.append({
                    'New_Variable': comp['new_variable'],
                    'Operation': comp['operation'],
                    'Source_Variables': ', '.join(comp['variables']),
                    'Formula': formula
                })
            
            log_df = pd.DataFrame(log_data)
            log_csv = log_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Log",
                data=log_csv,
                file_name="computations_log.csv",
                mime="text/csv",
                help="Download computations log"
            )
    
    # Data preview section
    if st.checkbox("👀 Show Data Preview"):
        st.markdown("---")
        st.subheader("📊 Data Preview")
        
        if st.session_state.computations_applied and st.session_state.computed_df is not None:
            st.write("**Data with computed variables (first 10 rows):**")
            
            # Highlight new columns
            new_vars = [comp['new_variable'] for comp in st.session_state.computations]
            preview_df = st.session_state.computed_df.head(10)
            
            # Show preview
            st.dataframe(preview_df, use_container_width=True, height=400)
            
            # Show only new variables
            if st.checkbox("📊 Show only new variables"):
                st.dataframe(preview_df[new_vars], use_container_width=True)
        else:
            st.write("**Original data (first 10 rows):**")
            st.dataframe(df.head(10), use_container_width=True, height=400)
            
            if st.session_state.computations:
                st.info("💡 Click 'COMPUTE ALL VARIABLES' to see the preview with new computed variables.")

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
        - **Addition:** Sum multiple variables
        - **Subtraction:** Subtract one variable from another
        - **Smart handling:** Negative results become zero
        - **Multiple computations:** Add as many as needed
        """)
    
    with col2:
        st.markdown("""
        **🔒 Smart Constraints:**
        - Variables used once can't be reused
        - Subtraction requires exactly 2 variables
        - Addition allows multiple variables
        - Automatic validation and error checking
        """)

# Floating button to add a new computation form (HTML version)
st.markdown("""
    <button onclick="document.getElementById('add_another_variable').click()" class="floating-add-button">+</button>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🧮 Built with Streamlit | Compute New Variables Tool v1.0</p>
</div>
""", unsafe_allow_html=True)
