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
                # Find facility columns
                mfl_col = find_facility_column(mfl_data)
                dhis2_col = find_facility_column(dhis2_data)
                
                # Handle duplicates
                mfl_data = handle_duplicates(mfl_data, mfl_col)
                dhis2_data = handle_duplicates(dhis2_data, dhis2_col)
                
                # Prepare data with suffixes
                mfl_data_processed = prepare_facility_data(mfl_data, "MFL")
                dhis2_data_processed = prepare_facility_data(dhis2_data, "DHIS2")
                
                # Display previews
                st.success("Files uploaded successfully!")
                st.balloons()
                st.snow()
                
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
                                'New_MFL': mfl_name  # Same name for exact matches
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
                            'New_MFL': best_match if best_score >= 70 else mfl_name  # Use DHIS2 name if good match, else keep MFL name
                        })
                    
                    # Create final results
                    matches_df = pd.DataFrame(matches)
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
                    
                    # Sort columns to put matching columns first
                    column_order = [
                        'MFL_Name',
                        'DHIS2_Name',
                        'New_MFL',
                        'Match_Score',
                        'Match_Status'
                    ]
                    # Add remaining columns
                    remaining_cols = [col for col in final_results.columns if col not in column_order]
                    column_order.extend(remaining_cols)
                    
                    # Reorder columns
                    final_results = final_results[column_order]
                    
                    # Display results
                    st.write("### Matching Results")
                    st.dataframe(final_results)
                    
                    # Download button
                    csv = final_results.to_csv(index=False)
                    st.download_button(
                        label="Download Results",
                        data=csv,
                        file_name="facility_matching_results.csv",
                        mime="text/csv"
                    )

        except Exception as e:
            st.error(f"Error reading files: {e}")

if __name__ == "__main__":
    main()
