import streamlit as st
import pandas as pd
import numpy as np
from jellyfish import jaro_winkler_similarity
from io import BytesIO
import time

# Page configuration
st.set_page_config(
    page_title="Health Facility Name Matching",
    page_icon="🏥",
    layout="wide"
)

# Light Silver theme styling
st.markdown("""
    <style>
    .stApp {
        background-color: #F5F5F5;
    }
    .main {
        padding: 2rem;
        color: #212121;
    }
    .stButton>button {
        background-color: #1E88E5 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        width: 100%;
        margin-top: 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1565C0 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .uploadedFile {
        margin-bottom: 1rem;
        background: gray;
        padding: 1rem;
        border-radius: 4px;
        border: 1px solid #1E88E5;
    }
    .stDataFrame {
        margin-top: 1rem;
        margin-bottom: 1rem;
        background: #FFFFFF;
        padding: 1rem;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stSelectbox > div > div {
        background-color: #FFFFFF;
        border: 1px solid #1E88E5;
    }
    .stTextInput > div > div > input {
        border: 1px solid #1E88E5;
    }
    [data-testid="stHeader"] {
        background: linear-gradient(135deg, #1E88E5, #64B5F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
""", unsafe_allow_html=True)

def show_welcome():
    """Show welcome message with animations"""
    welcome_container = st.empty()
    welcome_container.info("🏥 Welcome to the Health Facility Name Matching Tool")
    st.snow()
    st.balloons()
    # Clear welcome message after a few seconds
    time.sleep(3)
    welcome_container.empty()

def find_facility_column(df):
    """Automatically find the health facility name column"""
    for col in df.columns:
        if 'hf' in col.lower() or 'facility' in col.lower():
            return col
    return df.columns[0]  # Default to first column if no match found

def prepare_facility_data(df, source):
    """Prepare facility data with appropriate suffixes"""
    renamed_df = df.copy()
    suffix = f"_{source}"
    # Rename all columns with suffix
    renamed_df.columns = [f"{col}{suffix}" for col in renamed_df.columns]
    return renamed_df
    results = []
    
    for value1 in column1:
        if value1 in column2.values:
            results.append({
                'Col1': value1,
                'Col2': value1,
                'Match_Score': 100,
                'Match_Status': 'Match'
            })
        else:
            best_score = 0
            best_match = None
            for value2 in column2:
                similarity = jaro_winkler_similarity(str(value1), str(value2)) * 100
                if similarity > best_score:
                    best_score = similarity
                    best_match = value2
            results.append({
                'Col1': value1,
                'Col2': best_match,
                'Match_Score': round(best_score, 2),
                'Match_Status': 'Unmatch' if best_score < threshold else 'Match'
            })
    
    for value2 in column2:
        if value2 not in [r['Col2'] for r in results]:
            results.append({
                'Col1': None,
                'Col2': value2,
                'Match_Score': 0,
                'Match_Status': 'Unmatch'
            })
    
    return pd.DataFrame(results)

def read_data_file(file):
    """Read different types of data files"""
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith(('.xlsx', '.xls')):
            return pd.read_excel(file)
        else:
            raise ValueError(f"Unsupported file format: {file.name}")
    except Exception as e:
        st.error(f"Error reading file {file.name}: {str(e)}")
        return None

def main():
    st.title("Health Facility Name Matching")

    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 1
        st.balloons()  # Show balloons on first load
        st.snow()  # Show snow effect on first load
    if 'master_hf_list' not in st.session_state:
        st.session_state.master_hf_list = None
    if 'health_facilities_dhis2_list' not in st.session_state:
        st.session_state.health_facilities_dhis2_list = None

    # Step 1: File Upload
    if st.session_state.step == 1:
        st.header("Upload Files")
        mfl_file = st.file_uploader("Upload Master HF List:", type=['csv', 'xlsx', 'xls'])
        dhis2_file = st.file_uploader("Upload DHIS2 HF List:", type=['csv', 'xlsx', 'xls'])

        if mfl_file and dhis2_file:
            try:
                # Read data files
                mfl_data = read_data_file(mfl_file)
                dhis2_data = read_data_file(dhis2_file)
                
                if mfl_data is not None and dhis2_data is not None:
                    # Prepare data with suffixes
                    mfl_data_processed = prepare_facility_data(mfl_data, "MFL")
                    dhis2_data_processed = prepare_facility_data(dhis2_data, "DHIS2")
                    
                    # Find facility name columns
                    mfl_col = find_facility_column(mfl_data)
                    dhis2_col = find_facility_column(dhis2_data)
                    
                    # Display previews
                    st.success("Files uploaded successfully!")
                    st.balloons()
                    st.snow()
                    
                    st.subheader("Preview of Data")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("Master Facility List Preview")
                        st.dataframe(mfl_data.head())
                        st.write(f"Using column: {mfl_col}")
                    with col2:
                        st.write("DHIS2 List Preview")
                        st.dataframe(dhis2_data.head())
                        st.write(f"Using column: {dhis2_col}")
                    
                    if st.button("Proceed with Matching"):
                        st.session_state.mfl_data = mfl_data
                        st.session_state.dhis2_data = dhis2_data
                        st.session_state.mfl_col = mfl_col
                        st.session_state.dhis2_col = dhis2_col
                        st.session_state.step = 2
                        st.experimental_rerun()

            except Exception as e:
                st.error(f"Error reading files: {e}")

    # Step 2: Matching Process
    elif st.session_state.step == 2:
        st.header("Matching Process")
        
        with st.spinner("Performing matching..."):
            # Process the data
            mfl_data = st.session_state.mfl_data
            dhis2_data = st.session_state.dhis2_data
            mfl_col = st.session_state.mfl_col
            dhis2_col = st.session_state.dhis2_col
            
            # Convert name columns to string and handle duplicates
            mfl_data[mfl_col] = mfl_data[mfl_col].astype(str)
            dhis2_data[dhis2_col] = dhis2_data[dhis2_col].astype(str)
            
            # Display facility counts
            st.write("### Facility Counts")
            st.write(f"DHIS2 facilities: {len(dhis2_data)}")
            st.write(f"MFL facilities: {len(mfl_data)}")
            
            # Calculate matches with fixed threshold of 70
            matches = []
            for mfl_name in mfl_data[mfl_col]:
                best_match = None
                best_score = 0
                
                # Check for exact matches first
                if mfl_name in dhis2_data[dhis2_col].values:
                    matches.append({
                        'MFL_Name': mfl_name,
                        'DHIS2_Name': mfl_name,
                        'Match_Score': 100,
                        'Match_Status': 'Exact Match'
                    })
                    continue
                
                # If no exact match, find best match
                for dhis2_name in dhis2_data[dhis2_col]:
                    score = jaro_winkler_similarity(str(mfl_name), str(dhis2_name)) * 100
                    if score > best_score:
                        best_score = score
                        best_match = dhis2_name
                
                matches.append({
                    'MFL_Name': mfl_name,
                    'DHIS2_Name': best_match,
                    'Match_Score': round(best_score, 2),
                    'Match_Status': 'Match' if best_score >= 70 else 'No Match'
                })
            
            # Create matches DataFrame
            matches_df = pd.DataFrame(matches)
            
            # Prepare both datasets with suffixes
            mfl_data_suffix = mfl_data.copy()
            dhis2_data_suffix = dhis2_data.copy()
            
            # Add suffixes to all columns
            mfl_data_suffix.columns = [f"{col}_MFL" for col in mfl_data_suffix.columns]
            dhis2_data_suffix.columns = [f"{col}_DHIS2" for col in dhis2_data_suffix.columns]
            
            # Merge matches with original data
            final_results = matches_df.merge(
                mfl_data_suffix, 
                left_on='MFL_Name',
                right_on=f"{mfl_col}_MFL",
                how='left'
            ).merge(
                dhis2_data_suffix,
                left_on='DHIS2_Name',
                right_on=f"{dhis2_col}_DHIS2",
                how='left'
            )
            
            # Drop duplicate columns
            cols_to_drop = [f"{mfl_col}_MFL", f"{dhis2_col}_DHIS2"]
            final_results = final_results.drop(columns=cols_to_drop, errors='ignore')
            
            # Display results
            st.write("### Matching Results")
            st.dataframe(final_results)
            
            # Download button
            csv = final_results.to_csv(index=False)
            if st.download_button(
                label="Download Results",
                data=csv,
                file_name="facility_matching_results.csv",
                mime="text/csv"
            ):
                st.balloons()
                st.snow()
        
        if st.button("Perform Matching"):
            # Process data
            master_hf_list_clean = st.session_state.master_hf_list.copy()
            dhis2_list_clean = st.session_state.health_facilities_dhis2_list.copy()
            
            # Display facility counts
            st.write("### Counts of Health Facilities")
            st.write(f"Count of HFs in DHIS2 list: {len(dhis2_list_clean)}")
            st.write(f"Count of HFs in MFL list: {len(master_hf_list_clean)}")
            
            # Perform matching
            with st.spinner("Performing matching..."):
                hf_name_match_results = calculate_match(
                    master_hf_list_clean[mfl_col],
                    dhis2_list_clean[dhis2_col],
                    threshold
                )
                
                # Rename columns and process results
                hf_name_match_results = hf_name_match_results.rename(
                    columns={
                        'Col1': 'HF_Name_in_MFL',
                        'Col2': 'HF_Name_in_DHIS2'
                    }
                )
                
                # Add suffixes to all columns
                master_hf_cols = {col: f"{col}_MFL" for col in master_hf_list_clean.columns}
                dhis2_cols = {col: f"{col}_DHIS2" for col in dhis2_list_clean.columns}
                
                master_hf_list_clean = master_hf_list_clean.rename(columns=master_hf_cols)
                dhis2_list_clean = dhis2_list_clean.rename(columns=dhis2_cols)
                
                # Merge and create final results
                merged_results = pd.concat([
                    hf_name_match_results,
                    master_hf_list_clean,
                    dhis2_list_clean
                ], axis=1)
                
                st.write("### Matching Results")
                st.dataframe(merged_results)
                
                # Add download button
                csv = merged_results.to_csv(index=False)
                if st.download_button(
                    label="Download Matching Results",
                    data=csv,
                    file_name="facility_matching_results.csv",
                    mime="text/csv"
                ):
                    show_animations()  # Show animations on download

        if st.button("Start Over"):
            st.session_state.step = 1
            st.session_state.master_hf_list = None
            st.session_state.health_facilities_dhis2_list = None
            st.experimental_rerun()

if __name__ == "__main__":
    main()
