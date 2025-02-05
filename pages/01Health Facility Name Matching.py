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

# Light Sand theme styling
st.markdown("""
    <style>
    .stApp {
        background-color: #FAFAFA;
    }
    .main {
        padding: 2rem;
        color: #424242;
    }
    .stButton > button {
        background-color: #FF7043 !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #FFB74D !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

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
        if 'hf' in col.lower() or 'facility' in col.lower():
            return col
    return df.columns[0]

def handle_duplicates(df, facility_col):
    """Handle duplicates in facility names by appending adm3 names"""
    duplicated = df[facility_col].duplicated(keep=False)
    
    if duplicated.any():
        df_new = df.copy()
        adm3_cols = [col for col in df.columns if 'adm3' in col.lower()]
        
        if adm3_cols:
            adm3_col = adm3_cols[0]
            mask = duplicated
            df_new.loc[mask, facility_col] = (
                df_new.loc[mask, facility_col] + '_' + 
                df_new.loc[mask, adm3_col].fillna('unknown').astype(str)
            )
        else:
            for name in df[facility_col][duplicated].unique():
                mask = df[facility_col] == name
                df_new.loc[mask, facility_col] = [
                    f"{name}_{i+1}" for i in range(sum(mask))
                ]
        return df_new
    return df

def prepare_facility_data(df, source):
    """Prepare facility data with appropriate suffixes"""
    renamed_df = df.copy()
    suffix = f"_{source}"
    renamed_df.columns = [f"{col}{suffix}" for col in renamed_df.columns]
    return renamed_df

def display_initial_counts(mfl_data, dhis2_data):
    """Display initial facility counts for both datasets"""
    st.write("### Initial Facility Counts")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="MFL Facilities Count",
            value=len(mfl_data),
            help="Total number of facilities in Master Facility List"
        )
        st.write("MFL Data Counts:")
        mfl_counts = mfl_data.count()
        st.dataframe(pd.DataFrame({
            'Column': mfl_counts.index,
            'Count': mfl_counts.values
        }))
        
    with col2:
        st.metric(
            label="DHIS2 Facilities Count",
            value=len(dhis2_data),
            help="Total number of facilities in DHIS2 List"
        )
        st.write("DHIS2 Data Counts:")
        dhis2_counts = dhis2_data.count()
        st.dataframe(pd.DataFrame({
            'Column': dhis2_counts.index,
            'Count': dhis2_counts.values
        }))

def process_all_facilities(mfl_data_processed, dhis2_data_processed, matches_df, mfl_col_with_suffix, dhis2_col_with_suffix):
    """Process all facilities including unmatched facilities from both MFL and DHIS2"""
    # Get all DHIS2 facilities that weren't matched
    matched_dhis2 = matches_df['DHIS2_Name'].unique()
    all_dhis2 = dhis2_data_processed[dhis2_col_with_suffix].unique()
    unmatched_dhis2 = [f for f in all_dhis2 if f not in matched_dhis2]
    
    # Get all MFL facilities that weren't matched
    low_match_mfl = matches_df[matches_df['Match_Score'] < 70]['MFL_Name'].unique()
    
    # Create entries for unmatched DHIS2 facilities
    unmatched_entries = []
    for dhis2_name in unmatched_dhis2:
        unmatched_entries.append({
            'MFL_Name': None,
            'DHIS2_Name': dhis2_name,
            'New_MFL': dhis2_name,
            'Match_Score': 0,
            'Match_Status': 'HF in DHIS2 not in MFL'
        })
    
    # Mark low matching MFL facilities
    for mfl_name in low_match_mfl:
        if not matches_df[matches_df['MFL_Name'] == mfl_name]['Match_Score'].max() >= 70:
            matches_df.loc[matches_df['MFL_Name'] == mfl_name, 'Match_Status'] = 'HF in MFL not in DHIS2'
    
    # Add unmatched entries to matches DataFrame
    if unmatched_entries:
        unmatched_df = pd.DataFrame(unmatched_entries)
        matches_df = pd.concat([matches_df, unmatched_df], ignore_index=True)
    
    # Calculate statistics
    stats = {
        'Total MFL Facilities': len(mfl_data_processed),
        'Total DHIS2 Facilities': len(dhis2_data_processed),
        'Matched Facilities': len(matches_df[matches_df['Match_Status'] == 'Exact Match']),
        'Similar Facilities (≥70%)': len(matches_df[matches_df['Match_Score'] >= 70]) - len(matches_df[matches_df['Match_Status'] == 'Exact Match']),
        'HF in MFL not in DHIS2': len(matches_df[matches_df['Match_Status'] == 'HF in MFL not in DHIS2']),
        'HF in DHIS2 not in MFL': len(matches_df[matches_df['Match_Status'] == 'HF in DHIS2 not in MFL']),
        'Total Unique Facilities': len(matches_df)
    }
    
    return matches_df, stats

def display_column_lengths(df, title="Dataset Column Lengths"):
    """Display lengths of all columns in a DataFrame"""
    st.write(f"### {title}")
    
    # Calculate lengths for all columns
    lengths = pd.DataFrame({
        'Column': df.columns,
        'Non-Null Count': df.count(),
        'Null Count': df.isnull().sum(),
        'Total Length': len(df)
    })
    
    # Add percentage of non-null values
    lengths['Percentage Filled'] = round((lengths['Non-Null Count'] / lengths['Total Length']) * 100, 2)
    
    # Display the lengths
    st.dataframe(lengths)

def main():
    st.title("Health Facility Name Matching")

    # File Upload
    st.write("Upload Files:")
    mfl_file = st.file_uploader("Upload Master HF List:", type=['csv', 'xlsx', 'xls'])
    dhis2_file = st.file_uploader("Upload DHIS2 HF List:", type=['csv', 'xlsx', 'xls'])

    if mfl_file and dhis2_file:
        try:
            # Read data files
            mfl_data = read_data_file(mfl_file)
            dhis2_data = read_data_file(dhis2_file)
            
            if mfl_data is not None and dhis2_data is not None:
                # Display initial counts
                display_initial_counts(mfl_data, dhis2_data)
                
                # Find facility columns
                mfl_col = find_facility_column(mfl_data)
                dhis2_col = find_facility_column(dhis2_data)
                
                # Handle duplicates
                mfl_data = handle_duplicates(mfl_data, mfl_col)
                dhis2_data = handle_duplicates(dhis2_data, dhis2_col)
                
                # Prepare data with suffixes
                mfl_data_processed = prepare_facility_data(mfl_data, "MFL")
                dhis2_data_processed = prepare_facility_data(dhis2_data, "DHIS2")
                
                # Display success and animations
                st.success("Files uploaded successfully!")
                st.balloons()
                st.snow()
                
                # Display previews
                st.subheader("Preview of Data")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("Master Facility List Preview")
                    st.dataframe(mfl_data_processed.head())
                with col2:
                    st.write("DHIS2 List Preview")
                    st.dataframe(dhis2_data_processed.head())

                # Perform matching
                with st.spinner("Performing matching..."):
                    matches = []
                    mfl_col_with_suffix = f"{mfl_col}_MFL"
                    dhis2_col_with_suffix = f"{dhis2_col}_DHIS2"
                    
                    # Calculate matches
                    for mfl_name in mfl_data_processed[mfl_col_with_suffix]:
                        if mfl_name in dhis2_data_processed[dhis2_col_with_suffix].values:
                            matches.append({
                                'MFL_Name': mfl_name,
                                'DHIS2_Name': mfl_name,
                                'Match_Score': 100,
                                'Match_Status': 'Exact Match',
                                'New_MFL': mfl_name
                            })
                            continue
                        
                        best_match = None
                        best_score = 0
                        for dhis2_name in dhis2_data_processed[dhis2_col_with_suffix]:
                            score = jaro_winkler_similarity(str(mfl_name), str(dhis2_name)) * 100
                            if score > best_score:
                                best_score = score
                                best_match = dhis2_name
                        
                        matches.append({
                            'MFL_Name': mfl_name,
                            'DHIS2_Name': best_match,
                            'Match_Score': round(best_score, 2),
                            'Match_Status': 'Match' if best_score >= 70 else 'No Match',
                            'New_MFL': best_match if best_score >= 70 else mfl_name
                        })
                    
                    # Process all facilities including unmatched ones
                    matches_df = pd.DataFrame(matches)
                    matches_df, statistics = process_all_facilities(
                        mfl_data_processed, 
                        dhis2_data_processed, 
                        matches_df,
                        mfl_col_with_suffix,
                        dhis2_col_with_suffix
                    )
                    
                    # Display statistics
                    st.write("### Facility Matching Statistics")
                    stats_df = pd.DataFrame({
                        'Metric': statistics.keys(),
                        'Count': statistics.values()
                    })
                    st.dataframe(stats_df)
                    
                    # Create final results
                    final_results = matches_df.merge(
                        mfl_data_processed, 
                        left_on='MFL_Name',
                        right_on=mfl_col_with_suffix,
                        how='left'
                    ).merge(
                        dhis2_data_processed,
                        left_on='DHIS2_Name',
                        right_on=dhis2_col_with_suffix,
                        how='left'
                    )
                    
                    # Sort columns
                    column_order = [
                        'MFL_Name',
                        'DHIS2_Name',
                        'New_MFL',
                        'Match_Score',
                        'Match_Status'
                    ]
                    remaining_cols = [col for col in final_results.columns if col not in column_order]
                    column_order.extend(remaining_cols)
                    final_results = final_results[column_order]
                    
                    # Display results
                    st.write("### Matching Results")
                    st.dataframe(final_results)
                    
                    # Download button
                    csv = final_results.to_csv(index=False)
                    st.download_button(
                        label="Download Results",
                        data=csv,
                        file_name="Facility_matching_results.csv",
                        mime="text/csv"
                    )

        except Exception as e:
            st.error(f"Error reading files: {e}")

if __name__ == "__main__":
    main()
