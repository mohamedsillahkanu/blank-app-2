import streamlit as st
import pandas as pd

def read_file(file):
    file_type = file.name.split('.')[-1].lower()
    try:
        if file_type == 'csv':
            df = pd.read_csv(file)
        elif file_type in ['xlsx', 'xls']:
            df = pd.read_excel(file, engine='openpyxl' if file_type == 'xlsx' else 'xlrd')
        else:
            st.error(f"Unsupported file type: {file_type}")
            return None
        
        # Remove unnamed columns
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
        if unnamed_cols:
            st.info(f"Removing {len(unnamed_cols)} unnamed columns from {file.name}")
            df = df.drop(columns=unnamed_cols)
        
        # Reset the column index if the first row should be the header
        if df.columns.str.contains('Unnamed').any():
            st.info(f"First row in {file.name} appears to be headers. Setting first row as header.")
            # Make first row the header
            df.columns = df.iloc[0]
            df = df.drop(0).reset_index(drop=True)
        
        # Display columns for debugging
        st.write(f"Columns in {file.name} after cleaning:", list(df.columns))
        return df
    except Exception as e:
        st.error(f"Error reading file {file.name}: {str(e)}")
        return None

def clean_dataframe(df):
    """Remove blank rows and columns from dataframe"""
    if df is None:
        return None
    
    initial_rows = len(df)
    
    # Drop rows where all values are NaN or empty strings
    df = df.dropna(how='all').reset_index(drop=True)
    
    # Also drop rows where any key column is empty
    # Adjust this list based on your data's essential columns
    key_columns = ['periodname'] if 'periodname' in df.columns else []
    if key_columns:
        df = df.dropna(subset=key_columns).reset_index(drop=True)
    
    rows_removed = initial_rows - len(df)
    if rows_removed > 0:
        st.info(f"Removed {rows_removed} blank or incomplete rows")
    
    # Remove all-blank columns too
    df = df.dropna(axis=1, how='all')
    
    # Convert any blank strings to NaN for consistency
    df = df.replace('', pd.NA)
    
    return df

def validate_and_combine_files(files):
    if not files:
        return None
    
    dfs = []
    reference_df = read_file(files[0])
    
    if reference_df is None:
        return None
    
    # Remove blank rows from reference dataframe
    reference_df = clean_dataframe(reference_df)
    if reference_df.empty:
        st.error(f"First file {files[0].name} has no valid data after removing blank rows")
        return None
        
    reference_columns = list(reference_df.columns)
    dfs.append(reference_df)
    
    for file in files[1:]:
        df = read_file(file)
        if df is None:
            continue
        
        # Remove blank rows from current dataframe
        df = clean_dataframe(df)
        if df.empty:
            st.warning(f"File {file.name} has no valid data after removing blank rows")
            continue
            
        if list(df.columns) != reference_columns:
            st.error(f"Column mismatch in {file.name}")
            col_diff = set(df.columns).symmetric_difference(set(reference_columns))
            st.write("Mismatched columns:", col_diff)
            return None
            
        dfs.append(df)
    
    if not dfs:
        st.error("No valid data found in any of the files")
        return None
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Process date immediately after combining
    try:
        month_map = {
            'January': '01', 'February': '02', 'March': '03', 'April': '04',
            'May': '05', 'June': '06', 'July': '07', 'August': '08',
            'September': '09', 'October': '10', 'November': '11', 'December': '12'
        }
        
        # Check if the required columns exist
        if 'periodname' not in combined_df.columns:
            st.error("Missing required column: 'periodname'")
            st.write("Available columns:", list(combined_df.columns))
            return None
            
        combined_df[['month', 'year']] = combined_df['periodname'].str.split(' ', expand=True)
        combined_df['month'] = combined_df['month'].map(month_map)
        combined_df['year'] = pd.to_numeric(combined_df['year'])
        combined_df['Date'] = combined_df['year'].astype(str) + '-' + combined_df['month']
        
        # Only drop columns if they exist
        columns_to_drop = []
        if 'periodname' in combined_df.columns:
            columns_to_drop.append('periodname')
        if 'orgunitlevel5' in combined_df.columns:
            columns_to_drop.append('orgunitlevel5')
            
        if columns_to_drop:
            combined_df = combined_df.drop(columns=columns_to_drop)
    except Exception as e:
        st.error(f"Error processing date information: {str(e)}")
        st.write("Please check if your data has the expected 'periodname' column with values like 'January 2023'")
        return None
    
    return combined_df

if 'combined_df' not in st.session_state:
    st.session_state.combined_df = None

st.title("Malaria Data Processor")

uploaded_files = st.file_uploader("Upload Excel or CSV files", type=['xlsx', 'xls', 'csv'], accept_multiple_files=True)

if uploaded_files:
    combined_df = validate_and_combine_files(uploaded_files)
    
    if combined_df is not None:
        st.session_state.combined_df = combined_df.copy()
        
        # Display stats about cleaning
        st.success(f"Files processed successfully! Combined {len(uploaded_files)} files into {len(combined_df)} rows.")
        
        with st.expander("View Processed Data"):
            st.dataframe(st.session_state.combined_df)
        
        csv = combined_df.to_csv(index=False).encode('utf-8')
        st.snow()
        st.balloons()
        st.download_button(
            "Download Processed Data",
            csv,
            "merge_routine_data_processed.csv",
            "text/csv"
        )
