import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Set page config for better layout
st.set_page_config(
    page_title="Column Renamer Tool",
    page_icon="🔄",
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
    
    .column-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
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
    
    .apply-button {
        background-color: #28a745 !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        padding: 15px 30px !important;
        border-radius: 10px !important;
        border: none !important;
        width: 100% !important;
        margin: 20px 0 !important;
    }
    
    .apply-button:hover {
        background-color: #218838 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🔄 Column Renamer Tool</h1>
    <p>Upload your data file and rename columns interactively</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'original_columns' not in st.session_state:
    st.session_state.original_columns = []
if 'renamed_columns' not in st.session_state:
    st.session_state.renamed_columns = {}
if 'file_name' not in st.session_state:
    st.session_state.file_name = ""
if 'changes_applied' not in st.session_state:
    st.session_state.changes_applied = False

# Function to check if there are any changes
def has_changes(form_data, original_columns):
    for col in original_columns:
        if form_data.get(f"rename_{col}", col) != col:
            return True
    return False

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
            st.session_state.changes_applied = False
            
            st.success(f"✅ File uploaded successfully!")
            st.info(f"📊 **File:** {uploaded_file.name}")
            st.info(f"📏 **Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
            
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")

# Main content
if st.session_state.df is not None:
    df = st.session_state.df
    
    # Create form to prevent auto-rerun on text input changes
    with st.form("column_renaming_form"):
        # Create two columns for layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header("📋 Original Columns")
            
            # Search functionality
            search_term = st.text_input("🔍 Search columns", "", help="Filter columns by name")
            
            # Filter columns based on search
            filtered_columns = [col for col in st.session_state.original_columns 
                              if search_term.lower() in col.lower()]
            
            st.info(f"Showing {len(filtered_columns)} of {len(st.session_state.original_columns)} columns")
            
            # Display original columns
            for col in filtered_columns:
                st.markdown(f"""
                <div class="column-container">
                    <strong>{col}</strong><br>
                    <small>Type: {str(df[col].dtype)} | Non-null: {df[col].count()}/{len(df)}</small>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.header("✏️ New Column Names")
            
            # Column renaming interface
            new_names = {}
            for col in filtered_columns:
                # Get current value from session state if changes were applied
                if st.session_state.changes_applied and col in st.session_state.renamed_columns:
                    current_value = st.session_state.renamed_columns[col]
                else:
                    current_value = col
                
                new_name = st.text_input(
                    f"Rename '{col}'",
                    value=current_value,
                    key=f"rename_{col}",
                    help=f"Enter new name for column '{col}'"
                )
                new_names[col] = new_name
        
        # Create three columns for the buttons
        btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
        
        with btn_col1:
            # Reset button
            reset_clicked = st.form_submit_button(
                "🔄 Reset All",
                help="Reset all column names to original",
                use_container_width=True
            )
        
        with btn_col2:
            # Apply renaming button - center and larger
            apply_clicked = st.form_submit_button(
                "🔄 APPLY COLUMN RENAMING",
                type="primary",
                help="Apply all column name changes",
                use_container_width=True
            )
        
        with btn_col3:
            st.write("")  # Empty column for spacing
    
    # Handle button clicks
    if reset_clicked:
        st.session_state.renamed_columns = {}
        st.session_state.changes_applied = False
        st.rerun()
    
    if apply_clicked:
        # Check if there are actually changes to apply
        changes_to_apply = {}
        for col in st.session_state.original_columns:
            new_name = new_names.get(col, col)
            if new_name != col:
                changes_to_apply[col] = new_name
            else:
                changes_to_apply[col] = col
        
        # Apply the changes
        st.session_state.renamed_columns = changes_to_apply
        st.session_state.changes_applied = True
        
        # Show success message
        if any(old != new for old, new in changes_to_apply.items()):
            st.markdown("""
            <div class="success-message">
                ✅ <strong>Success!</strong> Column renaming has been applied successfully!
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ No changes were made to column names.")
    
    # Show changes summary if changes have been applied
    if st.session_state.changes_applied and st.session_state.renamed_columns:
        changes_df = pd.DataFrame([
            {"Original Column": old, "New Column": new}
            for old, new in st.session_state.renamed_columns.items()
            if old != new
        ])
        
        if not changes_df.empty:
            st.markdown("---")
            st.subheader("📝 Applied Changes")
            st.dataframe(changes_df, use_container_width=True)
            
            # Download section
            st.markdown("---")
            st.subheader("💾 Download Renamed Data")
            
            # Create renamed dataframe
            renamed_df = df.rename(columns=st.session_state.renamed_columns)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Download as CSV
                csv_buffer = io.StringIO()
                renamed_df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="rename_columns.csv",
                    mime="text/csv",
                    help="Download renamed data as CSV file"
                )
            
            with col2:
                # Download as Excel
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    renamed_df.to_excel(writer, sheet_name='Renamed Data', index=False)
                excel_data = excel_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name="rename_columns.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Download renamed data as Excel file"
                )
            
            with col3:
                # Download column mapping
                mapping_df = pd.DataFrame([
                    {"Original_Column": old, "New_Column": new}
                    for old, new in st.session_state.renamed_columns.items()
                ])
                
                mapping_csv = mapping_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Mapping",
                    data=mapping_csv,
                    file_name="column_mapping.csv",
                    mime="text/csv",
                    help="Download column name mapping file"
                )
            
            # Data preview section
            if st.checkbox("👀 Show Data Preview", help="Preview first 10 rows of renamed data"):
                st.markdown("---")
                st.subheader("📊 Data Preview (with renamed columns)")
                
                # Show preview with new column names
                st.dataframe(
                    renamed_df.head(10),
                    use_container_width=True,
                    height=400
                )
                
                # Statistics
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                with stat_col1:
                    st.metric("Total Rows", f"{len(renamed_df):,}")
                with stat_col2:
                    st.metric("Total Columns", f"{len(renamed_df.columns):,}")
                with stat_col3:
                    st.metric("Renamed Columns", f"{sum(1 for old, new in st.session_state.renamed_columns.items() if old != new):,}")
                with stat_col4:
                    memory_usage = renamed_df.memory_usage(deep=True).sum() / 1024 / 1024
                    st.metric("Memory Usage", f"{memory_usage:.1f} MB")
        else:
            st.info("ℹ️ No column names were changed.")
    
    # Show original data preview if no changes applied yet
    elif not st.session_state.changes_applied:
        if st.checkbox("👀 Show Original Data Preview", help="Preview first 10 rows of original data"):
            st.markdown("---")
            st.subheader("📊 Original Data Preview")
            
            st.dataframe(
                df.head(10),
                use_container_width=True,
                height=400
            )
            
            st.info("💡 Make your column name changes above and click 'APPLY COLUMN RENAMING' to see the renamed data.")

else:
    # Show instructions when no file is uploaded
    st.markdown("""
    <div class="upload-box">
        <h3>📁 No file uploaded yet</h3>
        <p>Please upload a CSV or Excel file using the sidebar to get started.</p>
        <p><strong>Supported formats:</strong> .csv, .xlsx, .xls</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show features
    st.subheader("✨ Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - **📂 Multiple file formats** - CSV, Excel (.xlsx, .xls)
        - **🔍 Search functionality** - Find columns quickly
        - **👀 Live preview** - See changes in real-time
        - **📊 Data statistics** - View column types and counts
        """)
    
    with col2:
        st.markdown("""
        - **💾 Multiple download options** - CSV, Excel, mapping file
        - **🔄 Easy reset** - Undo all changes with one click
        - **📝 Change tracking** - See what you've modified
        - **💡 Smart interface** - Intuitive and user-friendly
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>📧 Built with Streamlit | 🔄 Column Renamer Tool v1.0</p>
</div>
""", unsafe_allow_html=True)
