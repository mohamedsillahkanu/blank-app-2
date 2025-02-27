import streamlit as st
import pandas as pd
import numpy as np
import base64
from io import BytesIO

st.set_page_config(page_title="Dataset Merger with Conditional Logic", layout="wide")

def get_file_extension(file):
    """Get file extension from uploaded file."""
    return file.name.split('.')[-1].lower()

def read_file(file):
    """Read file based on its extension."""
    extension = get_file_extension(file)
    
    if extension == 'csv':
        return pd.read_csv(file)
    elif extension in ['xlsx', 'xls']:
        return pd.read_excel(file)
    else:
        st.error(f"Unsupported file format: {extension}")
        return None

def get_common_columns(df1, df2):
    """Get columns that exist in both dataframes."""
    return list(set(df1.columns).intersection(set(df2.columns)))

def main():
    st.title("Dataset Merger with Conditional Logic")
    
    # Initialize session state variables
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'df1' not in st.session_state:
        st.session_state.df1 = None
    if 'df2' not in st.session_state:
        st.session_state.df2 = None
    if 'merged_df' not in st.session_state:
        st.session_state.merged_df = None
    if 'selected_columns' not in st.session_state:
        st.session_state.selected_columns = []
    if 'conditions' not in st.session_state:
        st.session_state.conditions = {}
    if 'condition_names' not in st.session_state:
        st.session_state.condition_names = {}
    
    # Step 1: Upload datasets
    if st.session_state.step == 1:
        st.header("Step 1: Upload Datasets")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("First Dataset")
            file1 = st.file_uploader("Upload first dataset (CSV, Excel):", type=['csv', 'xlsx', 'xls'], key="file1")
            
            if file1 is not None:
                st.session_state.df1 = read_file(file1)
                if st.session_state.df1 is not None:
                    st.success(f"Successfully loaded: {file1.name}")
                    st.write("Preview:")
                    st.dataframe(st.session_state.df1.head())
        
        with col2:
            st.subheader("Second Dataset")
            file2 = st.file_uploader("Upload second dataset (CSV, Excel):", type=['csv', 'xlsx', 'xls'], key="file2")
            
            if file2 is not None:
                st.session_state.df2 = read_file(file2)
                if st.session_state.df2 is not None:
                    st.success(f"Successfully loaded: {file2.name}")
                    st.write("Preview:")
                    st.dataframe(st.session_state.df2.head())
        
        if st.session_state.df1 is not None and st.session_state.df2 is not None:
            common_columns = get_common_columns(st.session_state.df1, st.session_state.df2)
            
            if common_columns:
                st.subheader("Common Columns")
                st.write(f"Found {len(common_columns)} common columns: {', '.join(common_columns)}")
                
                # Select columns for merging
                merge_columns = st.multiselect(
                    "Select columns to merge datasets on:",
                    options=common_columns,
                    default=common_columns[0] if common_columns else None
                )
                
                merge_type = st.selectbox(
                    "Select merge type:",
                    options=["Inner join", "Left join", "Right join", "Outer join"],
                    help="Inner: keep only matching rows, Left: keep all rows from first dataset, Right: keep all rows from second dataset, Outer: keep all rows from both datasets"
                )
                
                if st.button("Merge Datasets") and merge_columns:
                    # Map merge type to pandas merge how parameter
                    merge_how = {
                        "Inner join": "inner",
                        "Left join": "left",
                        "Right join": "right",
                        "Outer join": "outer"
                    }[merge_type]
                    
                    # Perform merge
                    st.session_state.merged_df = pd.merge(
                        st.session_state.df1,
                        st.session_state.df2,
                        on=merge_columns,
                        how=merge_how,
                        suffixes=('_1', '_2')
                    )
                    
                    st.success(f"Successfully merged datasets! Result has {len(st.session_state.merged_df)} rows and {len(st.session_state.merged_df.columns)} columns.")
                    st.write("Preview of merged dataset:")
                    st.dataframe(st.session_state.merged_df.head())
                    
                    # Proceed to step 2
                    if st.button("Proceed to Conditional Logic"):
                        st.session_state.step = 2
                        st.experimental_rerun()
            else:
                st.error("No common columns found between the datasets. Cannot perform merge.")
    
    # Step 2: Select columns for conditional logic
    elif st.session_state.step == 2:
        st.header("Step 2: Select Columns for Conditional Logic")
        
        if st.session_state.merged_df is not None:
            # Show preview of merged dataset
            st.subheader("Preview of Merged Dataset")
            st.dataframe(st.session_state.merged_df.head())
            
            # Select columns for conditions
            st.subheader("Select Columns for Conditional Logic")
            st.write("Select columns you want to create conditions for:")
            
            all_columns = st.session_state.merged_df.columns.tolist()
            selected_columns = st.multiselect(
                "Select columns:",
                options=all_columns
            )
            
            if st.button("Proceed with Selected Columns") and selected_columns:
                st.session_state.selected_columns = selected_columns
                st.session_state.step = 3
                st.experimental_rerun()
            
            if st.button("Skip Conditional Logic"):
                st.session_state.step = 5  # Skip to download step
                st.experimental_rerun()
    
    # Step 3: Define conditions for each selected column
    elif st.session_state.step == 3:
        st.header("Step 3: Define Conditions")
        
        if not st.session_state.selected_columns:
            st.error("No columns selected for conditions.")
            if st.button("Go Back"):
                st.session_state.step = 2
                st.experimental_rerun()
        else:
            st.write("For each selected column, define the condition and values:")
            
            # Create a placeholder for conditions
            conditions = {}
            condition_names = {}
            
            for column in st.session_state.selected_columns:
                st.subheader(f"Condition for column: {column}")
                
                # Get unique values for the column
                unique_values = st.session_state.merged_df[column].dropna().unique()
                
                # Limit display if too many unique values
                if len(unique_values) > 20:
                    st.write(f"Column has {len(unique_values)} unique values. Showing first 20:")
                    st.write(unique_values[:20])
                else:
                    st.write(f"Unique values: {unique_values}")
                
                # Define condition operator
                operator = st.selectbox(
                    f"Select operator for {column}:",
                    options=["equals", "not equals", "greater than", "less than", "contains", "does not contain"],
                    key=f"operator_{column}"
                )
                
                # Define the conditional value
                if operator in ["equals", "not equals"] and len(unique_values) <= 20:
                    # Use selectbox for few unique values
                    condition_value = st.selectbox(
                        f"Select value for {column}:",
                        options=unique_values,
                        key=f"value_{column}"
                    )
                else:
                    # Use text input for many unique values or other operators
                    condition_value = st.text_input(
                        f"Enter value for {column}:",
                        key=f"value_{column}"
                    )
                    
                    # Try to convert to numeric if the column is numeric
                    if pd.api.types.is_numeric_dtype(st.session_state.merged_df[column]):
                        try:
                            condition_value = float(condition_value)
                        except ValueError:
                            st.warning(f"Entered value is not numeric. Column {column} appears to be numeric.")
                
                # Define new column name and values
                new_column_name = st.text_input(
                    f"Name for the new column based on {column} condition:",
                    value=f"{column}_flag",
                    key=f"new_col_{column}"
                )
                
                true_value = st.text_input(
                    f"Value when condition is TRUE:",
                    value="Yes",
                    key=f"true_{column}"
                )
                
                false_value = st.text_input(
                    f"Value when condition is FALSE:",
                    value="No",
                    key=f"false_{column}"
                )
                
                # Store the condition
                conditions[column] = {
                    "operator": operator,
                    "value": condition_value,
                    "true_value": true_value,
                    "false_value": false_value
                }
                
                condition_names[column] = new_column_name
            
            if st.button("Apply Conditions"):
                st.session_state.conditions = conditions
                st.session_state.condition_names = condition_names
                st.session_state.step = 4
                st.experimental_rerun()
    
    # Step 4: Apply conditions and create new columns
    elif st.session_state.step == 4:
        st.header("Step 4: Applying Conditions")
        
        if not st.session_state.conditions:
            st.error("No conditions defined.")
            if st.button("Go Back"):
                st.session_state.step = 3
                st.experimental_rerun()
        else:
            result_df = st.session_state.merged_df.copy()
            
            # Apply each condition and create new columns
            for column, condition in st.session_state.conditions.items():
                operator = condition["operator"]
                value = condition["value"]
                true_value = condition["true_value"]
                false_value = condition["false_value"]
                new_column_name = st.session_state.condition_names[column]
                
                # Apply the condition based on the operator
                if operator == "equals":
                    result_df[new_column_name] = np.where(result_df[column] == value, true_value, false_value)
                elif operator == "not equals":
                    result_df[new_column_name] = np.where(result_df[column] != value, true_value, false_value)
                elif operator == "greater than":
                    result_df[new_column_name] = np.where(result_df[column] > value, true_value, false_value)
                elif operator == "less than":
                    result_df[new_column_name] = np.where(result_df[column] < value, true_value, false_value)
                elif operator == "contains":
                    result_df[new_column_name] = np.where(result_df[column].astype(str).str.contains(str(value), na=False), true_value, false_value)
                elif operator == "does not contain":
                    result_df[new_column_name] = np.where(~result_df[column].astype(str).str.contains(str(value), na=False), true_value, false_value)
            
            # Update the merged dataframe with new columns
            st.session_state.merged_df = result_df
            
            st.success("Successfully applied all conditions!")
            st.write("Preview of dataset with conditional columns:")
            st.dataframe(st.session_state.merged_df.head())
            
            # Proceed to download step
            if st.button("Proceed to Download"):
                st.session_state.step = 5
                st.experimental_rerun()
    
    # Step 5: Download the final dataset
    elif st.session_state.step == 5:
        st.header("Step 5: Download Result")
        
        if st.session_state.merged_df is not None:
            st.write("Preview of final dataset:")
            st.dataframe(st.session_state.merged_df.head())
            
            # Get file name for download
            file_name = st.text_input("Enter file name for download (without extension):", value="merged_result")
            
            # Select file format
            file_format = st.selectbox(
                "Select file format:",
                options=["CSV", "Excel"]
            )
            
            if st.button("Download Result"):
                try:
                    if file_format == "CSV":
                        csv = st.session_state.merged_df.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}.csv">Download CSV File</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    else:  # Excel
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            st.session_state.merged_df.to_excel(writer, index=False, sheet_name='Result')
                        b64 = base64.b64encode(output.getvalue()).decode()
                        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{file_name}.xlsx">Download Excel File</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    
                    st.success(f"File '{file_name}' ready for download!")
                except Exception as e:
                    st.error(f"Error preparing download: {e}")
            
            if st.button("Start Over"):
                # Reset session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.experimental_rerun()
    
    # Add a sidebar with step navigation
    with st.sidebar:
        st.title("Navigation")
        st.write(f"Current step: {st.session_state.step}")
        
        if st.button("Go to Step 1: Upload"):
            st.session_state.step = 1
            st.experimental_rerun()
        
        if st.session_state.merged_df is not None:
            if st.button("Go to Step 2: Select Columns"):
                st.session_state.step = 2
                st.experimental_rerun()
        
        if st.session_state.selected_columns:
            if st.button("Go to Step 3: Define Conditions"):
                st.session_state.step = 3
                st.experimental_rerun()
        
        if st.session_state.conditions:
            if st.button("Go to Step 4: Apply Conditions"):
                st.session_state.step = 4
                st.experimental_rerun()
        
        if st.session_state.merged_df is not None:
            if st.button("Go to Step 5: Download"):
                st.session_state.step = 5
                st.experimental_rerun()

if __name__ == "__main__":
    main()
