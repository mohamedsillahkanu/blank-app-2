import streamlit as st
import pandas as pd
import numpy as np
from jellyfish import jaro_winkler_similarity
from io import BytesIO
from PIL import Image
import time
import random
import math

# Set page config first
st.set_page_config(page_title="Health Facility Matching Tool", page_icon="🏥", layout="wide")

# Define themes
themes = {
    "Black Modern": {
        "bg": "#000000",
        "accent": "#3498db",
        "text": "#FFFFFF",
        "sidebar_bg": "#1E1E1E",
        "gradient": "linear-gradient(135deg, #3498db, #2ecc71)"
    },
    "Light Silver": {
        "bg": "#F5F5F5",
        "accent": "#1E88E5",
        "text": "#212121",
        "sidebar_bg": "#FFFFFF",
        "gradient": "linear-gradient(135deg, #1E88E5, #64B5F6)"
    },
    "Light Modern": {
        "bg": "#FFFFFF",
        "accent": "#3498db",
        "text": "#333333",
        "sidebar_bg": "#F8F9FA",
        "gradient": "linear-gradient(135deg, #3498db, #2ecc71)"
    },
    "Dark Modern": {
        "bg": "#0E1117",
        "accent": "#3498db",
        "text": "#E0E0E0",
        "sidebar_bg": "#1E1E1E",
        "gradient": "linear-gradient(135deg, #3498db, #2ecc71)"
    }
}

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'master_hf_list' not in st.session_state:
    st.session_state.master_hf_list = None
if 'health_facilities_dhis2_list' not in st.session_state:
    st.session_state.health_facilities_dhis2_list = None
if 'last_animation' not in st.session_state:
    st.session_state.last_animation = time.time()
    st.session_state.theme_index = list(themes.keys()).index("Light Modern")  # Default to Light Modern
    st.session_state.first_load = True

def create_snow_animation():
    st.markdown("""
        <style>
            @keyframes snow {
                0% {
                    transform: translateY(-10vh) translateX(0) rotate(0deg);
                    opacity: 1;
                }
                100% {
                    transform: translateY(100vh) translateX(20px) rotate(360deg);
                    opacity: 0;
                }
            }
            .snowflake {
                position: fixed;
                color: #3498db;
                font-size: 1.5em;
                font-family: Arial, sans-serif;
                text-shadow: 0 0 5px rgba(52, 152, 219, 0.8);
                z-index: 999;
                pointer-events: none;
            }
        </style>
    """, unsafe_allow_html=True)
    
    snowflakes = ['❄', '❅', '❆', '✧', '✦']
    for i in range(20):
        left = random.uniform(0, 100)
        animation_duration = random.uniform(10, 20)
        delay = random.uniform(0, 10)
        
        st.markdown(f"""
            <div class="snowflake" style="left: {left}vw; animation: snow {animation_duration}s linear {delay}s infinite;">
                {random.choice(snowflakes)}
            </div>
        """, unsafe_allow_html=True)

def create_stars_animation():
    st.markdown("""
        <style>
            @keyframes twinkle {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.3; }
            }
            .star {
                position: fixed;
                z-index: 999;
                pointer-events: none;
            }
            .star-content {
                color: #3498db;
                text-shadow: 0 0 5px rgba(52, 152, 219, 0.8),
                             0 0 10px rgba(52, 152, 219, 0.5),
                             0 0 15px rgba(52, 152, 219, 0.3);
            }
        </style>
    """, unsafe_allow_html=True)
    
    star_chars = ['✦', '✧', '⋆', '✫', '✬', '✭', '✮', '✯', '✰']
    for i in range(30):
        left = random.uniform(0, 100)
        top = random.uniform(0, 100)
        animation_duration = random.uniform(1, 3)
        delay = random.uniform(0, 2)
        size = random.uniform(0.8, 1.5)
        
        st.markdown(f"""
            <div class="star" style="left: {left}vw; top: {top}vh;">
                <div class="star-content" style="font-size: {size}em; animation: twinkle {animation_duration}s ease-in-out {delay}s infinite;">
                    {random.choice(star_chars)}
                </div>
            </div>
        """, unsafe_allow_html=True)


# Welcome animation on first load
if st.session_state.first_load:
    create_snow_animation()
    create_stars_animation()
    st.balloons()
    welcome_placeholder = st.empty()
    welcome_placeholder.success("✨ Welcome to the Health Facility Matching Tool! 🏥 ✨")
    time.sleep(3)
    welcome_placeholder.empty()
    st.session_state.first_load = False

# Theme selection in sidebar
selected_theme = st.sidebar.selectbox(
    "🎨 Select Theme",
    list(themes.keys()),
    index=st.session_state.theme_index,
    key='theme_selector'
)

# Theme animation
if 'previous_theme' not in st.session_state:
    st.session_state.previous_theme = selected_theme
if st.session_state.previous_theme != selected_theme:
    create_snow_animation()
    create_stars_animation()
    st.balloons()
    st.session_state.previous_theme = selected_theme

theme = themes[selected_theme]
is_light_theme = "Light" in selected_theme

# Apply CSS styling
st.markdown(f"""
    <style>
        /* Main app styling */
        .stApp {{
            background-color: {theme['bg']};
        }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: {theme['sidebar_bg']} !important;
            padding: 1rem;
        }}
        
        [data-testid="stSidebar"] .stMarkdown {{
            color: {theme['text']} !important;
        }}
        
        [data-testid="stSidebar"] [data-testid="stSelectbox"] label {{
            color: {theme['text']} !important;
        }}
        
        /* Text and general elements */
        .stMarkdown, p, h1, h2, h3, label {{
            color: {theme['text']} !important;
        }}
        
        /* Custom title styling */
        .custom-title {{
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            padding: 1rem 0;
            margin-bottom: 2rem;
            color: {theme['text']};
            background: {theme['gradient']};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: glow 2s ease-in-out infinite alternate;
        }}
        
        /* Section card styling */
        .section-card {{
            background: {theme['sidebar_bg']};
            color: {theme['text']};
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            border-left: 5px solid {theme['accent']};
            transition: transform 0.3s ease;
            animation: float 6s ease-in-out infinite;
        }}
        
        .section-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
        }}

        .section-header {{
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: {theme['accent']};
        }}
        
        /* Button styling */
        .stButton button {{
            background: {theme['accent']};
            color: #FFFFFF;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .stButton button:hover {{
            opacity: 0.9;
            transform: translateY(-2px);
        }}
        
        /* Input field styling */
        .stTextInput input, .stSelectbox select, .stNumberInput input {{
            background-color: {theme['bg'] if is_light_theme else theme['sidebar_bg']};
            color: {theme['text']};
            border-radius: 5px;
            border: 1px solid {theme['accent'] + '40'};
        }}
        
        /* File uploader styling */
        [data-testid="stFileUploader"] {{
            background-color: {theme['bg'] if is_light_theme else theme['sidebar_bg']};
            padding: 1rem;
            border-radius: 10px;
            border: 2px dashed {theme['accent'] + '40'};
        }}
        
        /* Animation keyframes */
        @keyframes float {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
            100% {{ transform: translateY(0px); }}
        }}
        
        @keyframes glow {{
            from {{
                text-shadow: 0 0 5px {theme['accent'] + '40'},
                           0 0 10px {theme['accent'] + '30'},
                           0 0 15px {theme['accent'] + '20'};
            }}
            to {{
                text-shadow: 0 0 10px {theme['accent'] + '50'},
                           0 0 20px {theme['accent'] + '40'},
                           0 0 30px {theme['accent'] + '30'};
            }}
        }}
    </style>
""", unsafe_allow_html=True)




def calculate_match(df1, df2, col1, col2, threshold):
    """Calculate matching scores between two columns using Jaro-Winkler similarity."""
    results = []
    
    # Create prefix lists for columns to avoid conflicts
    mfl_columns = [f'MFL_{col}' for col in df1.columns]
    dhis2_columns = [f'DHIS2_{col}' for col in df2.columns]
    
    for idx1, row1 in df1.iterrows():
        value1 = str(row1[col1])
        
        # Initialize a result row with all MFL columns
        result_row = {
            f'MFL_{col}': row1[col] for col in df1.columns
        }
        
        # Add placeholder None values for all DHIS2 columns
        result_row.update({
            f'DHIS2_{col}': None for col in df2.columns
        })
        
        # Add match metadata columns
        result_row.update({
            'Match_Score': 0,
            'Match_Status': 'Unmatch',
            'New_HF_name_in_MFL': value1
        })
        
        if value1 in df2[col2].values:
            # Exact match
            matched_row = df2[df2[col2] == value1].iloc[0]
            # Update DHIS2 columns
            for c in df2.columns:
                result_row[f'DHIS2_{c}'] = matched_row[c]
            result_row.update({
                'Match_Score': 100,
                'Match_Status': 'Match',
                'New_HF_name_in_MFL': value1
            })
        else:
            # Find best match
            best_score = 0
            best_match_row = None
            for idx2, row2 in df2.iterrows():
                value2 = str(row2[col2])
                similarity = jaro_winkler_similarity(value1, value2) * 100
                if similarity > best_score:
                    best_score = similarity
                    best_match_row = row2
            
            if best_match_row is not None:
                # Update DHIS2 columns
                for c in df2.columns:
                    result_row[f'DHIS2_{c}'] = best_match_row[c]
                result_row.update({
                    'Match_Score': round(best_score, 2),
                    'Match_Status': 'Unmatch' if best_score < threshold else 'Match',
                    'New_HF_name_in_MFL': best_match_row[col2] if best_score >= threshold else value1
                })
        
        results.append(result_row)
    
    # Add unmatched facilities from DHIS2
    for idx2, row2 in df2.iterrows():
        value2 = str(row2[col2])
        if value2 not in [str(r[f'DHIS2_{col2}']) for r in results]:
            result_row = {
                f'MFL_{col}': None for col in df1.columns
            }
            result_row.update({
                f'DHIS2_{col}': row2[col] for col in df2.columns
            })
            result_row.update({
                'Match_Score': 0,
                'Match_Status': 'Unmatch',
                'New_HF_name_in_MFL': None
            })
            results.append(result_row)
    
    # Create DataFrame and organize columns
    result_df = pd.DataFrame(results)
    
    # Organize columns in a logical order
    column_order = (
        mfl_columns +  # All MFL columns first
        dhis2_columns +  # Then all DHIS2 columns
        ['Match_Score', 'Match_Status', 'New_HF_name_in_MFL']  # Metadata columns last
    )
    
    return result_df[column_order]

def main():
    st.markdown('<h1 class="custom-title">Health Facility Name Matching</h1>', unsafe_allow_html=True)

    # Step 1: File Upload
    if st.session_state.step == 1:
        st.markdown('<div class="section-card"><div class="section-header">Step 1: Upload Files</div>', unsafe_allow_html=True)
        mfl_file = st.file_uploader("Upload Master HF List (CSV, Excel):", type=['csv', 'xlsx', 'xls'])
        dhis2_file = st.file_uploader("Upload DHIS2 HF List (CSV, Excel):", type=['csv', 'xlsx', 'xls'])

        if mfl_file and dhis2_file:
            try:
                # Read files
                if mfl_file.name.endswith('.csv'):
                    st.session_state.master_hf_list = pd.read_csv(mfl_file)
                else:
                    st.session_state.master_hf_list = pd.read_excel(mfl_file)

                if dhis2_file.name.endswith('.csv'):
                    st.session_state.health_facilities_dhis2_list = pd.read_csv(dhis2_file)
                else:
                    st.session_state.health_facilities_dhis2_list = pd.read_excel(dhis2_file)

                st.success("Files uploaded successfully!")
                
                # Display previews
                st.markdown('<div class="section-header">Preview of Master HF List</div>', unsafe_allow_html=True)
                st.dataframe(st.session_state.master_hf_list.head())
                st.markdown('<div class="section-header">Preview of DHIS2 HF List</div>', unsafe_allow_html=True)
                st.dataframe(st.session_state.health_facilities_dhis2_list.head())

                if st.button("Proceed to Column Renaming"):
                    st.session_state.step = 2
                    st.experimental_rerun()

            except Exception as e:
                st.error(f"Error reading files: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
        # Step 2: Column Renaming
    elif st.session_state.step == 2:
        st.markdown('<div class="section-card"><div class="section-header">Step 2: Rename Columns (Optional)</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-header">Master HF List Columns</div>', unsafe_allow_html=True)
            mfl_renamed_columns = {}
            for col in st.session_state.master_hf_list.columns:
                new_col = st.text_input(f"Rename '{col}' to:", key=f"mfl_{col}", value=col)
                mfl_renamed_columns[col] = new_col

        with col2:
            st.markdown('<div class="section-header">DHIS2 HF List Columns</div>', unsafe_allow_html=True)
            dhis2_renamed_columns = {}
            for col in st.session_state.health_facilities_dhis2_list.columns:
                new_col = st.text_input(f"Rename '{col}' to:", key=f"dhis2_{col}", value=col)
                dhis2_renamed_columns[col] = new_col

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Apply Changes and Continue"):
                st.session_state.master_hf_list = st.session_state.master_hf_list.rename(columns=mfl_renamed_columns)
                st.session_state.health_facilities_dhis2_list = st.session_state.health_facilities_dhis2_list.rename(
                    columns=dhis2_renamed_columns)
                st.session_state.step = 3
                st.experimental_rerun()
        
        with col2:
            if st.button("Skip Renaming"):
                st.session_state.step = 3
                st.experimental_rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 3: Column Selection and Matching
    elif st.session_state.step == 3:
        st.markdown('<div class="section-card"><div class="section-header">Step 3: Select Columns for Matching</div>', unsafe_allow_html=True)
        
        mfl_col = st.selectbox("Select HF Name column in Master HF List:", 
                              st.session_state.master_hf_list.columns)
        dhis2_col = st.selectbox("Select HF Name column in DHIS2 HF List:", 
                                st.session_state.health_facilities_dhis2_list.columns)
        
        threshold = st.slider("Set Match Threshold (0-100):", 
                            min_value=0, max_value=100, value=70)

        if st.button("Perform Matching"):
            with st.spinner("Processing data..."):
                # Process data
                master_hf_list_clean = st.session_state.master_hf_list.copy()
                dhis2_list_clean = st.session_state.health_facilities_dhis2_list.copy()
                
                master_hf_list_clean[mfl_col] = master_hf_list_clean[mfl_col].astype(str)
                master_hf_list_clean = master_hf_list_clean.drop_duplicates(subset=[mfl_col])
                dhis2_list_clean[dhis2_col] = dhis2_list_clean[dhis2_col].astype(str)

                st.markdown('<div class="section-header">Health Facilities Count</div>', unsafe_allow_html=True)
                st.write(f"Count of HFs in DHIS2 list: {len(dhis2_list_clean)}")
                st.write(f"Count of HFs in MFL list: {len(master_hf_list_clean)}")

                # Perform matching
                with st.spinner("Matching facilities..."):
                    hf_name_match_results = calculate_match(
                        master_hf_list_clean,
                        dhis2_list_clean,
                        mfl_col,
                        dhis2_col,
                        threshold
                    )

                    # Display results
                    st.markdown('<div class="section-header">Matching Results</div>', unsafe_allow_html=True)
                    
                    # Display interactive dataframe with column sorting
                    st.dataframe(
                        hf_name_match_results,
                        use_container_width=True,
                        hide_index=True
                    )

                    # Calculate and display statistics
                    total_records = len(hf_name_match_results)
                    matched = len(hf_name_match_results[hf_name_match_results['Match_Status'] == 'Match'])
                    unmatched = total_records - matched

                    st.markdown(f"""
                        <div style='padding: 20px; border-radius: 10px; background-color: {theme['sidebar_bg']}; margin: 20px 0;'>
                            <h3 style='color: {theme['accent']};'>Matching Statistics</h3>
                            <p style='color: {theme['text']};'>Total Records: {total_records}</p>
                            <p style='color: {theme['text']};'>Matched: {matched} ({(matched/total_records*100):.1f}%)</p>
                            <p style='color: {theme['text']};'>Unmatched: {unmatched} ({(unmatched/total_records*100):.1f}%)</p>
                        </div>
                    """, unsafe_allow_html=True)

                    # Prepare download
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        hf_name_match_results.to_excel(writer, index=False)
                    output.seek(0)

                    # Download button
                    st.download_button(
                        label="📥 Download Matching Results",
                        data=output,
                        file_name="health_facility_matching_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        if st.button("Start Over"):
            st.session_state.step = 1
            st.session_state.master_hf_list = None
            st.session_state.health_facilities_dhis2_list = None
            st.experimental_rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
