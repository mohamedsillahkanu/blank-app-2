import streamlit as st
import pandas as pd
import io
import os
from typing import List, Dict, Tuple, Set

st.set_page_config(page_title="Dataset Merger", layout="wide")

def safe_dataframe_display(df):
    """Safely display a dataframe, converting problematic types to strings if needed."""
    try:
        return st.dataframe(df)
    except Exception as e:
        # If we encounter an error, try converting the dataframe to more compatible types
        st.warning("Converting complex data types to string representation for display...")
        
        # Convert problematic columns to strings
        df_display = df.copy()
        for col in df_display.columns:
            # Check for object dtype columns that might cause issues
            if df_display[col].dtype == 'object':
                try:
                    # Try to convert to string
                    df_display[col] = df_display[col].astype(str)
                except:
                    # If that fails, use a more aggressive approach
                    df_display[col] = df_display[col].apply(lambda x: str(x) if x is not None else None)
        
        try:
            return st.dataframe(df_display)
        except Exception as e2:
            st.error(f"Could not display dataframe: {str(e2)}. Try downloading it instead.")
            # Show just the shape and columns as text
            st.write(f"DataFrame shape: {df.shape}")
            st.write("Columns:", list(df.columns))
            return None

def read_file(uploaded_file):
    """Read the uploaded file and return a pandas DataFrame."""
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    try:
        if file_extension in ['.xlsx', '.xls']:
            return pd.read_excel(uploaded_file)
        elif file_extension == '.csv':
            return pd.read_csv(uploaded_file)
        else:
            st.error(f"Unsupported file format: {file_extension}. Please upload .xlsx, .xls, or .csv files.")
            return None
    except Exception as e:
        st.error(f"Error reading file {uploaded_file.name}: {str(e)}")
        return None

def find_common_columns(dataframes: List[pd.DataFrame]) -> Set[str]:
    """Find columns that are common across all dataframes."""
    if not dataframes:
        return set()
    
    common_columns = set(dataframes[0].columns)
    for df in dataframes[1:]:
        common_columns &= set(df.columns)
    
    return common_columns

def merge_all_datasets(dataframes: List[pd.DataFrame], merge_columns: List[str]) -> pd.DataFrame:
    """
    Merge multiple dataframes based on specified columns using a full outer join.
    This preserves all rows and columns from all dataframes.
    """
    if not dataframes or len(dataframes) < 2:
        return None
    
    # Start with the first dataframe
    result = dataframes[0].copy()
    
    # Loop through the remaining dataframes and merge them in
    for i, df in enumerate(dataframes[1:], 1):
        # Create a suffix for duplicate columns
        suffix = f"_{i}"
        
        # Merge with the next dataframe using full outer join
        result = pd.merge(result, df, on=merge_columns, how='outer', suffixes=('', suffix))
    
    return result

# Main Streamlit App
st.title("Dataset Merger")
st.write("""
Upload multiple Excel (.xlsx, .xls) or CSV files and get a merged dataset that preserves all rows and columns from all datasets.
""")

uploaded_files = st.file_uploader("Upload datasets", accept_multiple_files=True, 
                                  type=["xlsx", "xls", "csv"])

if uploaded_files:
    st.write(f"Uploaded {len(uploaded_files)} files")
    
    # Read all files
    dataframes = []
    df_names = []
    
    for file in uploaded_files:
        df = read_file(file)
        if df is not None:
            dataframes.append(df)
            df_names.append(file.name)
    
    if len(dataframes) < 2:
        st.warning("Please upload at least two valid files to merge.")
    else:
        # Find common columns
        common_columns = find_common_columns(dataframes)
        
        if not common_columns:
            st.error("No common columns found across all datasets. Cannot perform merge.")
        else:
            st.subheader("Common Columns")
            st.write(f"Merging on common columns: {', '.join(sorted(common_columns))}")
            
            # Automatically use all common columns
            selected_columns = list(common_columns)
            
            if st.button("Merge Datasets"):
                st.info("Using full outer join to preserve all rows and columns from all datasets")
                
                # Use the full outer join function
                merged_df = merge_all_datasets(dataframes, selected_columns)
                
                if merged_df is not None:
                    st.subheader("Merged Dataset")
                    st.write(f"Successfully merged into {len(merged_df)} rows and {len(merged_df.columns)} columns")
                    
                    # Display all columns in the merged dataset
                    st.subheader("All Columns in Merged Dataset")
                    
                    # Create a DataFrame of all column names for better display
                    column_df = pd.DataFrame({
                        'Column Name': merged_df.columns,
                        'Data Type': [str(merged_df[col].dtype) for col in merged_df.columns]
                    })
                    
                    # Display the column information
                    st.write("Columns in merged dataset:")
                    st.dataframe(column_df)
                    
                    # Use the safe display function for the merged data
                    st.subheader("Merged Data Preview")
                    safe_dataframe_display(merged_df)
                    
                    # Create CSV for download with a fixed filename
                    csv = merged_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Merged Dataset",
                        data=csv,
                        file_name="merged_dataset.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("Failed to merge the datasets.")
else:
    st.info("Please upload at least two files to merge (.xlsx, .xls, or .csv format).")

# Add some app information
st.sidebar.title("About")
st.sidebar.info("""
This app helps you merge multiple datasets based on common columns.

**Features:**
- Upload multiple Excel or CSV files
- Automatically identify common columns for merging
- Uses full outer join to preserve ALL rows from ALL datasets
- Preserves all columns from all datasets
- Displays a complete list of columns in the merged result
- Download the merged dataset
""")
