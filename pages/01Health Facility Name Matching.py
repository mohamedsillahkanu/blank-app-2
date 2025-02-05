import streamlit as st
import pandas as pd
import numpy as np
from jellyfish import jaro_winkler_similarity
from io import BytesIO

def find_hf_column(df):
    """Find the health facility name column"""
    hf_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['hf', 'facility', 'name', 'clinic'])]
    return hf_columns[0] if hf_columns else df.columns[0]

def add_suffixes_to_duplicate_hf_names(df, hf_column):
    """
    Add suffixes to duplicate health facility names while preserving all columns
    """
    # Create a copy of the dataframe
    df_processed = df.copy()
    
    # Count occurrences of each facility name
    name_counts = df_processed[hf_column].value_counts()
    
    # Identify duplicate names
    duplicates = name_counts[name_counts > 1]
    
    # Track suffixes for each unique name
    suffix_trackers = {}
    
    # Process each row
    for index, row in df_processed.iterrows():
        current_name = row[hf_column]
        
        # If this name appears more than once
        if current_name in duplicates.index:
            # Initialize suffix tracker for this name if not exists
            if current_name not in suffix_trackers:
                suffix_trackers[current_name] = 1
            
            # Add suffix to the name
            df_processed.at[index, hf_column] = f"{current_name}*_{suffix_trackers[current_name]}"
            
            # Increment suffix tracker
            suffix_trackers[current_name] += 1
    
    return df_processed

def calculate_match(column1, column2, threshold=70):
    """Calculate matching scores between two columns using Jaro-Winkler similarity."""
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

def main():
    st.title("Automated Health Facility Name Matching")

    # File Upload
    mfl_file = st.file_uploader("Upload Master HF List (CSV, Excel):", type=['csv', 'xlsx', 'xls'])
    dhis2_file = st.file_uploader("Upload DHIS2 HF List (CSV, Excel):", type=['csv', 'xlsx', 'xls'])

    if mfl_file and dhis2_file:
        try:
            # Read files
            if mfl_file.name.endswith('.csv'):
                mfl_df = pd.read_csv(mfl_file)
            else:
                mfl_df = pd.read_excel(mfl_file)

            if dhis2_file.name.endswith('.csv'):
                dhis2_df = pd.read_csv(dhis2_file)
            else:
                dhis2_df = pd.read_excel(dhis2_file)

            # Find HF name columns
            dhis2_hf_column = find_hf_column(dhis2_df)
            mfl_hf_column = find_hf_column(mfl_df)

            # Process DHIS2 duplicates
            st.write("### Processing DHIS2 Facility Names")
            st.write(f"Original DHIS2 Unique Facilities: {len(dhis2_df[dhis2_hf_column].unique())}")
            dhis2_df_processed = add_suffixes_to_duplicate_hf_names(dhis2_df, dhis2_hf_column)
            st.write(f"DHIS2 Unique Facilities after processing: {len(dhis2_df_processed[dhis2_hf_column].unique())}")

            # Process MFL duplicates
            st.write("### Processing MFL Facility Names")
            st.write(f"Original MFL Unique Facilities: {len(mfl_df[mfl_hf_column].unique())}")
            mfl_df_processed = add_suffixes_to_duplicate_hf_names(mfl_df, mfl_hf_column)
            st.write(f"MFL Unique Facilities after processing: {len(mfl_df_processed[mfl_hf_column].unique())}")

            # Perform matching
            st.write("### Matching Process")
            
            # Convert name columns to string
            mfl_df_processed[mfl_hf_column] = mfl_df_processed[mfl_hf_column].astype(str)
            dhis2_df_processed[dhis2_hf_column] = dhis2_df_processed[dhis2_hf_column].astype(str)

            # Calculate matching results
            match_results = calculate_match(
                mfl_df_processed[mfl_hf_column],
                dhis2_df_processed[dhis2_hf_column]
            )

            # Rename matching columns
            match_results = match_results.rename(columns={
                'Col1': 'HF_Name_in_MFL',
                'Col2': 'HF_Name_in_DHIS2'
            })

            # Add replacement column
            match_results['New_HF_Name_in_MFL'] = np.where(
                match_results['Match_Score'] >= 70,
                match_results['HF_Name_in_DHIS2'],
                match_results['HF_Name_in_MFL']
            )

            # Prepare dataframes with suffixed columns
            mfl_cols = {col: f"{col}_MFL" for col in mfl_df_processed.columns if col != mfl_hf_column}
            dhis2_cols = {col: f"{col}_DHIS2" for col in dhis2_df_processed.columns if col != dhis2_hf_column}

            mfl_df_suffixed = mfl_df_processed.rename(columns=mfl_cols)
            dhis2_df_suffixed = dhis2_df_processed.rename(columns=dhis2_cols)

            # Merge results
            merged_results = (
                match_results
                .merge(
                    mfl_df_suffixed,
                    left_on='HF_Name_in_MFL',
                    right_on=f"{mfl_hf_column}_MFL",
                    how='left'
                )
                .merge(
                    dhis2_df_suffixed,
                    left_on='HF_Name_in_DHIS2',
                    right_on=f"{dhis2_hf_column}_DHIS2",
                    how='left'
                )
            )

            # Clean up columns
            if f"{mfl_hf_column}_MFL" in merged_results.columns:
                merged_results = merged_results.drop(columns=[f"{mfl_hf_column}_MFL"])
            if f"{dhis2_hf_column}_DHIS2" in merged_results.columns:
                merged_results = merged_results.drop(columns=[f"{dhis2_hf_column}_DHIS2"])

            # Reorder columns
            matching_cols = [
                'HF_Name_in_MFL',
                'HF_Name_in_DHIS2',
                'New_HF_Name_in_MFL',
                'Match_Score'
            ]
            other_cols = [col for col in merged_results.columns if col not in matching_cols]
            final_col_order = matching_cols + other_cols
            merged_results = merged_results[final_col_order]

            # Display statistics
            st.write("### Matching Statistics")
            stats = {
                'Total MFL Facilities': len(mfl_df_processed),
                'Total DHIS2 Facilities': len(dhis2_df_processed),
                'Exact Matches': len(merged_results[merged_results['Match_Score'] == 100]),
                'High Matches (≥70%)': len(merged_results[merged_results['Match_Score'] >= 70]),
                'Low Matches (<70%)': len(merged_results[merged_results['Match_Score'] < 70])
            }
            stats_df = pd.DataFrame(list(stats.items()), columns=['Metric', 'Value'])
            st.dataframe(stats_df)

            # Display results
            st.write("### Matching Results")
            st.dataframe(merged_results)

            # Download button
            csv = merged_results.to_csv(index=False)
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
