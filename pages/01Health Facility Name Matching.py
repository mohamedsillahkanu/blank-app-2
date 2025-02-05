import streamlit as st
import pandas as pd
import numpy as np
from jellyfish import jaro_winkler_similarity
import time

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

def find_facility_column(df):
    """Find the health facility name column"""
    for col in df.columns:
        if 'hf' in col.lower() or 'facility' in col.lower() or 'name' in col.lower():
            return col
    return df.columns[0]

def find_adm3_column(df):
    """Find the ADM3 column"""
    for col in df.columns:
        if 'adm3' in col.lower() or 'district' in col.lower():
            return col
    return None

def handle_duplicate_facilities(df):
    """
    Handle duplicate facilities by identifying and marking duplicates
    """
    # Create a copy of the dataframe
    df_new = df.copy()
    
    # Find facility and ADM3 columns
    facility_col = find_facility_column(df_new)
    adm3_col = find_adm3_column(df_new)
    
    # Log initial unique facility count
    original_unique_count = len(df_new[facility_col].unique())
    st.write(f"Original Unique Facilities: {original_unique_count}")
    
    # Identify duplicates
    duplicate_mask = df_new[facility_col].duplicated(keep=False)
    
    # If duplicates exist
    if duplicate_mask.any():
        # Find which facilities are duplicated
        duplicated_facilities = df_new[facility_col][duplicate_mask]
        
        # If ADM3 column exists, use it for disambiguation
        if adm3_col:
            # Group duplicate facilities
            grouped = df_new[duplicate_mask].groupby(facility_col)
            
            for name, group in grouped:
                # If multiple facilities with same name have different ADM3
                if len(group[adm3_col].unique()) > 1:
                    # Mark these duplicates with ADM3 suffix
                    dup_indices = group.index
                    for idx in dup_indices:
                        adm3_suffix = str(df_new.loc[idx, adm3_col]) if pd.notna(df_new.loc[idx, adm3_col]) else 'Unknown'
                        df_new.loc[idx, facility_col] = f"{name}*_{adm3_suffix}"
        else:
            # If no ADM3, add incremental suffix to duplicates
            for name in df_new[facility_col][duplicate_mask].unique():
                mask = df_new[facility_col] == name
                df_new.loc[mask, facility_col] = [
                    f"{name}*_{i+1}" for i in range(sum(mask))
                ]
    
    # Log final unique facility count
    final_unique_count = len(df_new[facility_col].unique())
    st.write(f"Unique Facilities after processing: {final_unique_count}")
    
    # Display first few rows
    st.dataframe(df_new.head())
    
    # Visual effects
    st.snow()
    st.balloons()
    
    return df_new

def find_hf_not_in_mfl(dhis2_df, mfl_df):
    """
    Find health facilities in DHIS2 that are not in MFL
    """
    # Find facility columns
    dhis2_facility_col = find_facility_column(dhis2_df)
    mfl_facility_col = find_facility_column(mfl_df)
    
    # Get unique facility names (removing * and suffixes for comparison)
    dhis2_facilities = set(name.split('*')[0] for name in dhis2_df[dhis2_facility_col])
    mfl_facilities = set(name.split('*')[0] for name in mfl_df[mfl_facility_col])
    
    # Find facilities in DHIS2 not in MFL
    hf_not_in_mfl = dhis2_facilities - mfl_facilities
    
    # Create a dataframe of DHIS2 facilities not in MFL
    hf_not_in_mfl_df = dhis2_df[dhis2_df[dhis2_facility_col].apply(lambda x: x.split('*')[0] in hf_not_in_mfl)].copy()
    
    # Add a column to mark these facilities
    hf_not_in_mfl_df['HF_Status'] = 'Not in MFL'
    
    # Display findings
    st.write("### Health Facilities in DHIS2 Not in MFL")
    st.write(f"Number of facilities in DHIS2 not in MFL: {len(hf_not_in_mfl_df)}")
    
    # Display column lengths
    st.write("### Column Lengths for DHIS2 Facilities Not in MFL")
    column_lengths = pd.DataFrame({
        'Column': hf_not_in_mfl_df.columns,
        'Non-Null Count': hf_not_in_mfl_df.count(),
        'Null Count': hf_not_in_mfl_df.isnull().sum(),
        'Percentage Filled': round(hf_not_in_mfl_df.count() / len(hf_not_in_mfl_df) * 100, 2)
    })
    st.dataframe(column_lengths)
    
    # Display the dataframe
    st.dataframe(hf_not_in_mfl_df)
    
    return hf_not_in_mfl_df

def main():
    st.title("Health Facility Name Matching with Duplicate Handling")

    # File Upload
    st.write("Upload Files:")
    mfl_file = st.file_uploader("Upload Master HF List:", type=['csv', 'xlsx', 'xls'])
    dhis2_file = st.file_uploader("Upload DHIS2 HF List:", type=['csv', 'xlsx', 'xls'])

    if mfl_file and dhis2_file:
        try:
            # Read data files
            dhis2_df = read_data_file(dhis2_file)
            
            # First, process DHIS2 dataframe
            dhis2_df_processed = handle_duplicate_facilities(dhis2_df)
            
            # Then, read and process MFL dataframe
            mfl_df = read_data_file(mfl_file)
            mfl_df_processed = handle_duplicate_facilities(mfl_df)
            
            # Find health facilities in DHIS2 not in MFL
            hf_not_in_mfl_df = find_hf_not_in_mfl(dhis2_df_processed, mfl_df_processed)
            
            # Option to download DHIS2 facilities not in MFL
            if not hf_not_in_mfl_df.empty:
                csv = hf_not_in_mfl_df.to_csv(index=False)
                st.download_button(
                    label="Download DHIS2 Facilities Not in MFL",
                    data=csv,
                    file_name="dhis2_facilities_not_in_mfl.csv",
                    mime="text/csv"
                )
            
            # Perform matching
            st.write("### Matching Process")
            matches = []
            
            # Find facility columns
            dhis2_facility_col = find_facility_column(dhis2_df_processed)
            mfl_facility_col = find_facility_column(mfl_df_processed)
            
            # Matching logic
            for mfl_name in mfl_df_processed[mfl_facility_col]:
                best_match = None
                best_score = 0
                
                for dhis2_name in dhis2_df_processed[dhis2_facility_col]:
                    # Calculate similarity score
                    # Compare base names (without suffixes)
                    mfl_base = mfl_name.split('*')[0]
                    dhis2_base = dhis2_name.split('*')[0]
                    
                    score = jaro_winkler_similarity(str(mfl_base), str(dhis2_base)) * 100
                    
                    if score > best_score:
                        best_score = score
                        best_match = dhis2_name
                
                # Create match record
                match_record = {
                    'MFL_Name': mfl_name,
                    'DHIS2_Name': best_match,
                    'Match_Score': round(best_score, 2),
                    'Match_Status': 'Exact Match' if best_score == 100 else 
                                    'High Match' if best_score >= 70 else 
                                    'Low Match'
                }
                matches.append(match_record)
            
            # Convert matches to DataFrame
            matches_df = pd.DataFrame(matches)
            
            # Display matching results
            st.write("### Matching Results")
            st.dataframe(matches_df)
            
            st.snow()
            st.balloons()
            
            # Matching statistics
            st.write("### Matching Statistics")
            stats = {
                'Total MFL Facilities': len(mfl_df_processed),
                'Total DHIS2 Facilities': len(dhis2_df_processed),
                'DHIS2 Facilities Not in MFL': len(hf_not_in_mfl_df),
                'Exact Matches': len(matches_df[matches_df['Match_Status'] == 'Exact Match']),
                'High Matches (≥70%)': len(matches_df[matches_df['Match_Status'] == 'High Match']),
                'Low Matches (<70%)': len(matches_df[matches_df['Match_Status'] == 'Low Match'])
            }
            
            stats_df = pd.DataFrame(list(stats.items()), columns=['Metric', 'Value'])
            st.dataframe(stats_df)
            
            # Download results
            csv = matches_df.to_csv(index=False)
            st.download_button(
                label="Download Matching Results",
                data=csv,
                file_name="facility_matching_results.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
