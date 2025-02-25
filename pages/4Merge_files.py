import streamlit as st
import pandas as pd
import io
import os
from typing import List, Dict, Tuple, Set

st.set_page_config(page_title="Dataset Merger", layout="wide")

def read_file(uploaded_file):
    """Read the uploaded file and return a pandas DataFrame."""
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    if file_extension in ['.xlsx', '.xls']:
        return pd.read_excel(uploaded_file)
    elif file_extension == '.csv':
        return pd.read_csv(uploaded_file)
    else:
        st.error(f"Unsupported file format: {file_extension}. Please upload .xlsx, .xls, or .csv files.")
        return None

def find_common_columns(dataframes: List[pd.DataFrame]) -> Set[str]:
    """Find columns that are common across all dataframes."""
    if not dataframes:
        return set()
    
    common_columns = set(dataframes[0].columns)
    for df in dataframes[1:]:
        common_columns &= set(df.columns)
    
    return common_columns

def identify_merge_problems(left_df: pd.DataFrame, right_df: pd.DataFrame, 
                           merge_keys: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Identify problematic rows that don't have a 1:1 merge relationship.
    Returns three dataframes:
    1. Rows that merged successfully (1:1)
    2. Rows from left_df that have no match or multiple matches
    3. Rows from right_df that have no match or multiple matches
    """
    # Create keys for identification
    left_df['_merge_key'] = left_df[merge_keys].apply(lambda x: tuple(x), axis=1)
    right_df['_merge_key'] = right_df[merge_keys].apply(lambda x: tuple(x), axis=1)
    
    # Count occurrences of each key
    left_counts = left_df['_merge_key'].value_counts().to_dict()
    right_counts = right_df['_merge_key'].value_counts().to_dict()
    
    # Find problematic keys
    left_problem_keys = {k for k, v in left_counts.items() if v > 1 or k not in right_counts}
    right_problem_keys = {k for k, v in right_counts.items() if v > 1 or k not in left_counts}
    
    # Create masks for filtering
    left_problem_mask = left_df['_merge_key'].isin(left_problem_keys)
    right_problem_mask = right_df['_merge_key'].isin(right_problem_keys)
    
    # Extract problematic rows
    left_problems = left_df[left_problem_mask].copy()
    right_problems = right_df[right_problem_mask].copy()
    
    # Perform the merge for successful rows
    successful_left = left_df[~left_problem_mask].copy()
    successful_right = right_df[~right_problem_mask].copy()
    
    # Remove temporary merge key column
    successful_left = successful_left.drop(columns=['_merge_key'])
    successful_right = successful_right.drop(columns=['_merge_key'])
    left_problems = left_problems.drop(columns=['_merge_key'])
    right_problems = right_problems.drop(columns=['_merge_key'])
    
    # Merge the successful rows
    merged = pd.merge(successful_left, successful_right, on=merge_keys, how='inner')
    
    return merged, left_problems, right_problems

def merge_datasets(dataframes: List[pd.DataFrame], merge_columns: List[str]) -> Tuple[pd.DataFrame, Dict]:
    """
    Merge multiple dataframes based on specified columns.
    Returns the merged dataframe and a dictionary of problematic rows.
    """
    if not dataframes or len(dataframes) < 2:
        return None, {}
    
    problems = {}
    result = dataframes[0].copy()
    
    for i, df in enumerate(dataframes[1:], 1):
        merged, left_problems, right_problems = identify_merge_problems(result, df, merge_columns)
        
        if not left_problems.empty:
            problems[f"Dataset {i-1} problems"] = left_problems
            
        if not right_problems.empty:
            problems[f"Dataset {i} problems"] = right_problems
            
        result = merged
    
    return result, problems

# Main Streamlit App
st.title("Dataset Merger")
st.write("""
Upload multiple Excel (.xlsx, .xls) or CSV files, select common columns to merge on, 
and get a merged dataset with error reporting for rows that don't have a 1:1 relationship.
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
            st.error("No common columns found across all datasets.")
        else:
            st.subheader("Common Columns")
            selected_columns = st.multiselect(
                "Select columns to merge on",
                options=list(common_columns),
                default=list(common_columns)
            )
            
            if selected_columns:
                if st.button("Merge Datasets"):
                    merged_df, problems = merge_datasets(dataframes, selected_columns)
                    
                    if merged_df is not None:
                        st.subheader("Merged Dataset")
                        st.write(f"Successfully merged {len(merged_df)} rows")
                        st.dataframe(merged_df)
                        
                        # Provide download option for merged dataset
                        csv = merged_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download merged dataset as CSV",
                            data=csv,
                            file_name="merged_dataset.csv",
                            mime="text/csv"
                        )
                        
                        # Display problematic rows
                        if problems:
                            st.subheader("Merge Problems")
                            st.warning(
                                "The following rows couldn't be merged with a 1:1 relationship. "
                                "They were excluded from the main merge but are shown below for reference."
                            )
                            
                            for problem_name, problem_df in problems.items():
                                with st.expander(f"{problem_name} ({len(problem_df)} rows)"):
                                    st.dataframe(problem_df)
                        else:
                            st.success("All rows merged successfully with a 1:1 relationship.")
                    else:
                        st.error("Failed to merge the datasets.")
            else:
                st.info("Please select at least one column to merge on.")

    # Display individual datasets
    with st.expander("View uploaded datasets"):
        for i, (df, name) in enumerate(zip(dataframes, df_names)):
            st.subheader(f"Dataset {i+1}: {name}")
            st.dataframe(df)
            st.write(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
else:
    st.info("Please upload at least two files to merge (.xlsx, .xls, or .csv format).")

# Add some app information
st.sidebar.title("About")
st.sidebar.info("""
This app helps you merge multiple datasets based on common columns. 
It identifies and reports on rows that don't have a perfect 1:1 relationship.

**Features:**
- Upload multiple Excel or CSV files
- Automatically identify common columns
- Perform 1:1 merge on selected columns
- Report problematic rows that don't merge cleanly
- Download the merged dataset
""")
