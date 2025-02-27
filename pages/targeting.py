import streamlit as st
import pandas as pd
import numpy as np
import base64
from io import BytesIO

st.set_page_config(page_title="Multi-Dataset Merger", layout="wide")

def read_file(file):
    """Read uploaded file into a dataframe."""
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file)
    else:
        st.error(f"Unsupported file format: {file.name}")
        return None

# Initialize session state
if 'datasets' not in st.session_state:
    st.session_state.datasets = {}
if 'merged_df' not in st.session_state:
    st.session_state.merged_df = None
if 'conditions' not in st.session_state:
    st.session_state.conditions = []

# App header
st.title("Multi-Dataset Merger with Conditional Logic")

# Sidebar for uploading files
with st.sidebar:
    st.header("Upload Datasets")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload dataset (CSV or Excel)", type=['csv', 'xlsx', 'xls'], key="file_upload")
    
    if uploaded_file is not None:
        dataset_name = st.text_input("Enter a name for this dataset:", 
                                     value=uploaded_file.name.split('.')[0])
        
        if st.button("Add Dataset"):
            df = read_file(uploaded_file)
            if df is not None:
                st.session_state.datasets[dataset_name] = df
                st.success(f"Added dataset: {dataset_name}")
    
    # Show currently loaded datasets
    if st.session_state.datasets:
        st.subheader("Loaded Datasets")
        for name in st.session_state.datasets.keys():
            st.write(f"- {name} ({len(st.session_state.datasets[name])} rows)")
        
        if st.button("Clear All Datasets"):
            st.session_state.datasets = {}
            st.session_state.merged_df = None
            st.session_state.conditions = []
            st.experimental_rerun()

# Main workspace
tab1, tab2, tab3 = st.tabs(["Merge Datasets", "Apply Conditions", "Download Results"])

# Tab 1: Merge Datasets
with tab1:
    st.header("Merge Datasets")
    
    if len(st.session_state.datasets) < 2:
        st.info("Please upload at least 2 datasets in the sidebar to perform a merge.")
    else:
        # Select datasets to merge
        st.subheader("Select Datasets to Merge")
        
        dataset_names = list(st.session_state.datasets.keys())
        base_dataset = st.selectbox("Select base dataset:", dataset_names)
        
        merge_list = []
        
        # Start with base dataset
        if base_dataset:
            base_df = st.session_state.datasets[base_dataset]
            result_df = base_df.copy()
            
            # Setup for merging additional datasets
            for i, name in enumerate([n for n in dataset_names if n != base_dataset]):
                if st.checkbox(f"Merge with {name}", key=f"merge_{i}"):
                    merge_list.append(name)
                    
                    if merge_list:
                        st.subheader(f"Merge Settings for {name}")
                        
                        # Find common columns
                        second_df = st.session_state.datasets[name]
                        common_cols = list(set(result_df.columns).intersection(set(second_df.columns)))
                        
                        # Select merge columns
                        merge_cols = st.multiselect(
                            f"Select columns to join on for {name}:",
                            common_cols,
                            default=common_cols[0] if common_cols else None,
                            key=f"cols_{i}"
                        )
                        
                        # Select merge type
                        merge_type = st.selectbox(
                            f"Join type for {name}:",
                            ["Left join", "Inner join", "Right join", "Outer join"],
                            key=f"type_{i}"
                        )
                        
                        merge_how = {
                            "Left join": "left",
                            "Inner join": "inner", 
                            "Right join": "right",
                            "Outer join": "outer"
                        }[merge_type]
                        
            # Perform merge button
            if merge_list and st.button("Perform Merge"):
                # Sequentially merge datasets
                for i, name in enumerate(merge_list):
                    second_df = st.session_state.datasets[name]
                    merge_cols = st.session_state[f"cols_{i}"]
                    merge_how = {
                        "Left join": "left",
                        "Inner join": "inner", 
                        "Right join": "right",
                        "Outer join": "outer"
                    }[st.session_state[f"type_{i}"]]
                    
                    # Perform the merge
                    result_df = pd.merge(
                        result_df, 
                        second_df,
                        on=merge_cols,
                        how=merge_how,
                        suffixes=(f'', f'_{name}')
                    )
                
                st.session_state.merged_df = result_df
                st.success(f"Successfully merged {len(merge_list)+1} datasets! Result has {len(result_df)} rows.")
        
        # Display merged result preview
        if st.session_state.merged_df is not None:
            st.subheader("Merged Dataset Preview")
            st.dataframe(st.session_state.merged_df.head())
            st.info(f"Total columns: {len(st.session_state.merged_df.columns)}")

# Tab 2: Apply Conditions
with tab2:
    st.header("Apply Conditional Logic")
    
    if st.session_state.merged_df is None:
        st.info("Please merge datasets in the 'Merge Datasets' tab first.")
    else:
        st.subheader("Create Conditional Columns")
        
        # Add a new condition
        with st.expander("Add New Condition", expanded=True):
            all_columns = st.session_state.merged_df.columns.tolist()
            
            col1, col2 = st.columns(2)
            with col1:
                source_col = st.selectbox("Select column for condition:", all_columns)
                
                # Show sample values
                if source_col:
                    unique_vals = st.session_state.merged_df[source_col].dropna().unique()
                    if len(unique_vals) > 5:
                        st.write(f"Sample values: {', '.join(map(str, unique_vals[:5]))}, ...")
                    else:
                        st.write(f"Unique values: {', '.join(map(str, unique_vals))}")
                
                operator = st.selectbox("Condition type:", 
                                      ["equals", "not equals", "greater than", "less than", "contains", "does not contain"])
                
                condition_value = st.text_input("Condition value:")
            
            with col2:
                new_col_name = st.text_input("New column name:", 
                                           value=f"{source_col}_flag" if source_col else "")
                true_value = st.text_input("Value when TRUE:", value="Yes")
                false_value = st.text_input("Value when FALSE:", value="No")
            
            if st.button("Add Condition"):
                if source_col and new_col_name:
                    new_condition = {
                        "source_column": source_col,
                        "operator": operator,
                        "value": condition_value,
                        "new_column": new_col_name,
                        "true_value": true_value,
                        "false_value": false_value
                    }
                    
                    if 'conditions' not in st.session_state:
                        st.session_state.conditions = []
                    
                    st.session_state.conditions.append(new_condition)
                    st.success(f"Added condition for column: {source_col}")
                else:
                    st.error("Please select a column and provide a name for the new column.")
        
        # Display existing conditions
        if st.session_state.conditions:
            st.subheader("Current Conditions")
            
            for i, condition in enumerate(st.session_state.conditions):
                with st.expander(f"Condition {i+1}: {condition['new_column']}"):
                    st.write(f"If {condition['source_column']} {condition['operator']} '{condition['value']}' then '{condition['true_value']}' else '{condition['false_value']}'")
                    
                    if st.button(f"Remove condition", key=f"remove_{i}"):
                        st.session_state.conditions.pop(i)
                        st.experimental_rerun()
            
            # Apply all conditions
            if st.button("Apply All Conditions"):
                result_df = st.session_state.merged_df.copy()
                
                for condition in st.session_state.conditions:
                    col = condition["source_column"]
                    op = condition["operator"]
                    val = condition["value"]
                    new_col = condition["new_column"]
                    true_val = condition["true_value"]
                    false_val = condition["false_value"]
                    
                    # Try to convert value to numeric if column is numeric
                    if pd.api.types.is_numeric_dtype(result_df[col]) and val.replace('.', '', 1).isdigit():
                        val = float(val)
                    
                    # Apply condition based on operator
                    if op == "equals":
                        result_df[new_col] = np.where(result_df[col] == val, true_val, false_val)
                    elif op == "not equals":
                        result_df[new_col] = np.where(result_df[col] != val, true_val, false_val)
                    elif op == "greater than":
                        result_df[new_col] = np.where(result_df[col] > val, true_val, false_val)
                    elif op == "less than":
                        result_df[new_col] = np.where(result_df[col] < val, true_val, false_val)
                    elif op == "contains":
                        result_df[new_col] = np.where(result_df[col].astype(str).str.contains(str(val), na=False), 
                                                   true_val, false_val)
                    elif op == "does not contain":
                        result_df[new_col] = np.where(~result_df[col].astype(str).str.contains(str(val), na=False), 
                                                    true_val, false_val)
                
                st.session_state.merged_df = result_df
                st.success("Successfully applied all conditions!")
                
                # Display preview of result
                st.subheader("Result Preview")
                st.dataframe(st.session_state.merged_df.head())

# Tab 3: Download Results
with tab3:
    st.header("Download Results")
    
    if st.session_state.merged_df is None:
        st.info("Please merge datasets and apply conditions before downloading.")
    else:
        st.subheader("Preview Final Dataset")
        st.dataframe(st.session_state.merged_df.head())
        
        st.subheader("Download Options")
        filename = st.text_input("Enter filename for download (without extension):", value="merged_result")
        
        file_format = st.radio("Select file format:", ["CSV", "Excel"])
        
        if st.button("Generate Download Link"):
            try:
                if file_format == "CSV":
                    csv = st.session_state.merged_df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Click here to download {filename}.csv</a>'
                else:
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        st.session_state.merged_df.to_excel(writer, index=False, sheet_name='Results')
                    b64 = base64.b64encode(buffer.getvalue()).decode()
                    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">Click here to download {filename}.xlsx</a>'
                
                st.markdown(href, unsafe_allow_html=True)
                st.success(f"Download link generated for {filename}!")
            except Exception as e:
                st.error(f"Error generating download: {e}")
