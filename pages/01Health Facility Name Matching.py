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

def add_suffix_to_dhis2_duplicates(df):
    """
    First, process DHIS2 dataframe to add ADM3 suffixes to duplicate facility names
    If no ADM3 column exists, use incremental numbering
    """
    st.write("### Processing DHIS2 Dataframe")
    
    # Create a copy of the dataframe
    df_new = df.copy()
    
    # Find facility and ADM3 columns
    facility_col = find_facility_column(df_new)
    adm3_col = find_adm3_column(df_new)
    
    # Log initial unique facility count
    st.write(f"Original DHIS2 Unique Facilities: {len(df_new[facility_col].unique())}")
    
    # Identify duplicates
    duplicate_mask = df_new[facility_col].duplicated(keep=False)
    
    if duplicate_mask.any():
        if adm3_col:
            # Create unique names by combining facility name and ADM3
            grouped = df_new[duplicate_mask].groupby(facility_col)
            
            for name, group in grouped:
                # Find indices of duplicates for this specific name
                dup_indices = group.index
                
                # Add unique suffixes using ADM3
                for idx in dup_indices:
                    # Use ADM3 or 'Unknown' if ADM3 is null
                    adm3_suffix = str(df_new.loc[idx, adm3_col]) if pd.notna(df_new.loc[idx, adm3_col]) else 'Unknown'
                    df_new.loc[idx, facility_col] = f"{name}*_{adm3_suffix}"
        else:
            # If no ADM3 column, use incremental numbering
            for name in df_new[facility_col][duplicate_mask].unique():
                mask = df_new[facility_col] == name
                df_new.loc[mask, facility_col] = [
                    f"{name}*_{i+1}" for i in range(sum(mask))
                ]
    
    # Log processed unique facility count
    st.write(f"DHIS2 Unique Facilities after processing: {len(df_new[facility_col].unique())}")
    
    # Display first few rows of processed DHIS2 dataframe
    st.dataframe(df_new.head())
    
    # Add snow and balloons for fun visual effect
    st.snow()
    st.balloons()
    
    return df_new

def add_suffix_to_mfl_duplicates(df):
    """
    Next, process MFL dataframe to add ADM3 suffixes to duplicate facility names
    If no ADM3 column exists, use incremental numbering
    """
    st.write("### Processing MFL Dataframe")
    
    # Create a copy of the dataframe
    df_new = df.copy()
    
    # Find facility and ADM3 columns
    facility_col = find_facility_column(df_new)
    adm3_col = find_adm3_column(df_new)
    
    # Log initial unique facility count
    st.write(f"Original MFL Unique Facilities: {len(df_new[facility_col].unique())}")
    
    # Identify duplicates
    duplicate_mask = df_new[facility_col].duplicated(keep=False)
    
    if duplicate_mask.any():
        if adm3_col:
            # Create unique names by combining facility name and ADM3
            grouped = df_new[duplicate_mask].groupby(facility_col)
            
            for name, group in grouped:
                # Find indices of duplicates for this specific name
                dup_indices = group.index
                
                # Add unique suffixes using ADM3
                for idx in dup_indices:
                    # Use ADM3 or 'Unknown' if ADM3 is null
                    adm3_suffix = str(df_new.loc[idx, adm3_col]) if pd.notna(df_new.loc[idx, adm3_col]) else 'Unknown'
                    df_new.loc[idx, facility_col] = f"{name}*_{adm3_suffix}"
        else:
            # If no ADM3 column, use incremental numbering
            for name in df_new[facility_col][duplicate_mask].unique():
                mask = df_new[facility_col] == name
                df_new.loc[mask, facility_col] = [
                    f"{name}*_{i+1}" for i in range(sum(mask))
                ]
    
    # Log processed unique facility count
    st.write(f"MFL Unique Facilities after processing: {len(df_new[facility_col].unique())}")
    
    # Display first few rows of processed MFL dataframe
    st.dataframe(df_new.head())
    
    # Add snow and balloons for fun visual effect
    st.snow()
    st.balloons()
    
    return df_new

def main():
    st.title("Health Facility Name Matching with ADM3 Suffixes")

    # File Upload
    st.write("Upload Files:")
    mfl_file = st.file_uploader("Upload Master HF List:", type=['csv', 'xlsx', 'xls'])
    dhis2_file = st.file_uploader("Upload DHIS2 HF List:", type=['csv', 'xlsx', 'xls'])

    if mfl_file and dhis2_file:
        try:
            # Read data files
            dhis2_df = read_data_file(dhis2_file)
            
            # First, process DHIS2 dataframe
            dhis2_df_processed = add_suffix_to_dhis2_duplicates(dhis2_df)
            
            # Then, read and process MFL dataframe
            mfl_df = read_data_file(mfl_file)
            mfl_df_processed = add_suffix_to_mfl_duplicates(mfl_df)
            
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
                    score = jaro_winkler_similarity(str(mfl_name), str(dhis2_name)) * 100
                    
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
            
            # Add snow and balloons after matching
            st.snow()
            st.balloons()
            
            # Matching statistics
            st.write("### Matching Statistics")
            stats = {
                'Total MFL Facilities': len(mfl_df_processed),
                'Total DHIS2 Facilities': len(dhis2_df_processed),
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
