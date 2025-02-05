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

def make_facility_names_unique(df):
    """
    Make facility names unique by adding incremental suffixes
    """
    # Create a copy of the dataframe
    df_new = df.copy()
    
    # Find facility column
    facility_col = find_facility_column(df_new)
    
    # Create a counter to track duplicate names
    name_counts = {}
    
    # Function to generate unique name
    def get_unique_name(name):
        if name not in name_counts:
            name_counts[name] = 0
            return name
        
        name_counts[name] += 1
        return f"{name}*_{name_counts[name]}"
    
    # Make facility names unique
    df_new[facility_col] = df_new[facility_col].apply(get_unique_name)
    
    # Display unique count after processing
    st.write(f"Unique Facilities after processing: {len(df_new[facility_col].unique())}")
    
    # Display first few rows
    st.dataframe(df_new.head())
    
    # Visual effects
    st.snow()
    st.balloons()
    
    return df_new

def main():
    st.title("Health Facility Name Matching")

    # File Upload
    st.write("Upload Files:")
    mfl_file = st.file_uploader("Upload Master HF List:", type=['csv', 'xlsx', 'xls'])
    dhis2_file = st.file_uploader("Upload DHIS2 HF List:", type=['csv', 'xlsx', 'xls'])

    if mfl_file and dhis2_file:
        try:
            # Read data files
            dhis2_df = read_data_file(dhis2_file)
            
            # First, process DHIS2 dataframe
            dhis2_facility_col = find_facility_column(dhis2_df)
            st.write(f"Original DHIS2 Unique Facilities: {len(dhis2_df[dhis2_facility_col].unique())}")
            dhis2_df_processed = make_facility_names_unique(dhis2_df)
            
            # Then, read and process MFL dataframe
            mfl_df = read_data_file(mfl_file)
            mfl_facility_col = find_facility_column(mfl_df)
            st.write(f"Original MFL Unique Facilities: {len(mfl_df[mfl_facility_col].unique())}")
            mfl_df_processed = make_facility_names_unique(mfl_df)
            
            # Perform matching
            st.write("### Matching Process")
            matches = []
            
            # Matching logic
            for mfl_name in mfl_df_processed[mfl_facility_col]:
                best_match = None
                best_score = 0
                
                for dhis2_name in dhis2_df_processed[dhis2_facility_col]:
                    # Remove suffixes for comparison
                    mfl_base = mfl_name.split('*_')[0]
                    dhis2_base = dhis2_name.split('*_')[0]
                    
                    # Calculate similarity score
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
