import streamlit as st
import pandas as pd

def rename_columns(df):
    try:
        # Get a list of actual columns in the dataframe
        actual_columns = set(df.columns.str.lower())
        
        # Define the renaming dictionary
        orgunit_rename = {
            'orgunitlevel1': 'adm0',
            'orgunitlevel2': 'adm1',
            'orgunitlevel3': 'adm2',
            'orgunitlevel4': 'adm3',
            'organisationunitname': 'hf'
        }
        
        # Only include mappings for columns that actually exist
        rename_dict = {col: new_name for col, new_name in orgunit_rename.items() 
                      if col.lower() in actual_columns}
        
        if not rename_dict:
            st.warning("None of the expected columns found for renaming. Check your data format.")
            return df  # Return original dataframe instead of None
        
        return df.rename(columns=rename_dict)
    except Exception as e:
        st.error(f"Error renaming columns: {str(e)}")
        return df  # Return original dataframe instead of None

def create_hfid(df):
    try:
        # Check if all required columns exist
        required_cols = ['adm1', 'adm2', 'adm3', 'hf']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.warning(f"Missing columns for facility ID creation: {', '.join(missing_cols)}. Using available columns.")
            # Use only available columns for grouping
            group_cols = [col for col in required_cols if col in df.columns]
            if not group_cols:
                st.error("No location columns available for facility ID creation.")
                df['hf_uid'] = [f'hf_{i:04d}' for i in range(len(df))]
                return df
                
            df['hf_uid'] = df.groupby(group_cols).ngroup().apply(
                lambda x: f'hf_{x:04d}'
            )
        else:
            # All columns exist, proceed as planned
            df['hf_uid'] = df.groupby(['adm1', 'adm2', 'adm3', 'hf']).ngroup().apply(
                lambda x: f'hf_{x:04d}'
            )
        
        return df
    except Exception as e:
        st.error(f"Error creating facility IDs: {str(e)}")
        # Add a simple sequential ID as fallback
        df['hf_uid'] = [f'hf_{i:04d}' for i in range(len(df))]
        return df

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
            
        # Basic validation
        if df.empty:
            st.error("The uploaded file contains no data.")
            return None
            
        return df
    except Exception as e:
        st.error(f"Error reading file {file.name}: {str(e)}")
        return None

def process_files(file):
    if file is None:
        return None
    
    df = read_file(file)
    if df is None:
        return None
    
    # Display original column names for debugging
    st.write("Original columns:", df.columns.tolist())
    
    # Make column names lowercase for case-insensitive matching
    df.columns = df.columns.str.lower()
    
    df = rename_columns(df)
    if df is None:
        return None
        
    df = create_hfid(df)    
    return df

# Initialize session state
if 'processed_df' not in st.session_state:
    st.session_state.processed_df = None

st.title("Routine Data Uploader")
st.write("Upload the merged routine data downloaded from the merge malaria routine data")

# Create file uploader
uploaded_file = st.file_uploader("Upload merged data file", type=['xlsx', 'xls', 'csv'])

# Process the file when uploaded
if uploaded_file:
    with st.spinner("Processing file..."):
        processed_df = process_files(uploaded_file)
    
    if processed_df is not None:
        st.session_state.processed_df = processed_df.copy()
        st.success("File processed successfully!")
        
        # Show health facility count statistics
        unique_hf_count = processed_df['hf_uid'].nunique()
        total_rows = len(processed_df)
        
        st.metric("Unique Health Facilities", unique_hf_count)
        st.metric("Total Records", total_rows)
        st.metric("Average Records per Facility", round(total_rows/unique_hf_count, 2) if unique_hf_count > 0 else 0)
        
        # Show distribution of facilities
        if 'adm1' in processed_df.columns:
            with st.expander("Health Facility Distribution by Region"):
                hf_by_region = processed_df.groupby('adm1')['hf_uid'].nunique().reset_index()
                hf_by_region.columns = ['District', 'Number of Health Facilities']
                st.dataframe(hf_by_region.sort_values('Number of Health Facilities'))
        
        with st.expander("View Processed Data"):
            st.dataframe(processed_df)
        
        csv = processed_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Processed Data",
            csv,
            "renamed_malaria_routine_data.csv",
            "text/csv"
        )
