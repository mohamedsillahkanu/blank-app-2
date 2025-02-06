import streamlit as st
import pandas as pd

def read_file(file):
    file_type = file.name.split('.')[-1].lower()
    try:
        if file_type == 'csv':
            return pd.read_csv(file)
        elif file_type in ['xlsx', 'xls']:
            return pd.read_excel(file, engine='openpyxl' if file_type == 'xlsx' else 'xlrd')
        else:
            st.error(f"Unsupported file type: {file_type}")
            return None
    except Exception as e:
        st.error(f"Error reading file {file.name}: {str(e)}")
        return None

def validate_and_combine_files(files):
    if not files:
        return None

    dfs = []
    reference_df = read_file(files[0])
    
    if reference_df is None:
        return None
        
    reference_columns = list(reference_df.columns)
    dfs.append(reference_df)
    
    for file in files[1:]:
        df = read_file(file)
        if df is None:
            continue
            
        if list(df.columns) != reference_columns:
            st.error(f"Column mismatch in {file.name}")
            col_diff = set(df.columns).symmetric_difference(set(reference_columns))
            st.write("Mismatched columns:", col_diff)
            return None
            
        dfs.append(df)
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Process date immediately after combining
    month_map = {
        'January': '01', 'February': '02', 'March': '03', 'April': '04',
        'May': '05', 'June': '06', 'July': '07', 'August': '08',
        'September': '09', 'October': '10', 'November': '11', 'December': '12'
    }

    combined_df[['month', 'year']] = combined_df['periodname'].str.split(' ', expand=True)
    combined_df['month'] = combined_df['month'].map(month_map)
    combined_df['year'] = pd.to_numeric(combined_df['year'])
    combined_df['Date'] = combined_df['year'].astype(str) + '-' + combined_df['month']
    combined_df = combined_df.drop(columns=['periodname', 'orgunitlevel5'])
    
    return combined_df

if 'combined_df' not in st.session_state:
    st.session_state.combined_df = None

st.title("Malaria Data Processor")
uploaded_files = st.file_uploader("Upload Excel or CSV files", type=['xlsx', 'xls', 'csv'], accept_multiple_files=True)

if uploaded_files:
    combined_df = validate_and_combine_files(uploaded_files)
    
    if combined_df is not None:
        st.session_state.combined_df = combined_df.copy()
        st.success("Files processed successfully!")
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
