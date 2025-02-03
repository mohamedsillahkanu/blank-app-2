import streamlit as st
import time
import random
import threading

# Set page config first
st.set_page_config(page_title="Geospatial Analysis Tool", page_icon="🗺️", layout="wide")

# Force dark theme across the entire app
st.markdown("""
    <style>
        /* Override Streamlit's default theme to force dark mode */
        .stApp {
            background-color: #0E1117 !important;
        }
        
        /* Dark theme for sidebar */
        [data-testid="stSidebar"] {
            background-color: #1E1E1E !important;
            border-right: 1px solid #2E2E2E;
        }
        
        /* Dark theme for all text */
        .stMarkdown, p, h1, h2, h3 {
            color: #E0E0E0 !important;
        }
        
        /* Dark theme for selectbox */
        .stSelectbox > div > div {
            background-color: #1E1E1E !important;
            color: #E0E0E0 !important;
        }
        
        /* Dark theme for checkbox */
        .stCheckbox > div > div > label {
            color: #E0E0E0 !important;
        }
        
        /* Update section cards for dark theme */
        .section-card {
            background: #1E1E1E !important;
            color: #E0E0E0 !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
        }
        
        .section-card:hover {
            background: #2E2E2E !important;
        }
        
        /* Dark theme for content text */
        .content-text {
            color: #E0E0E0 !important;
        }

        /* Bullet points */
        .custom-bullet {
            margin-left: 20px;
            position: relative;
        }
        .custom-bullet::before {
            content: "•";
            color: #E0E0E0;
            position: absolute;
            left: -15px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session states
if 'last_animation' not in st.session_state:
    st.session_state.last_animation = time.time()
    st.session_state.theme_index = 0
    st.session_state.first_load = True

# Define dark themes
themes = {
    "Dark Modern": {
        "bg": "#0E1117",
        "accent": "#3498db",
        "text": "#E0E0E0",
        "gradient": "linear-gradient(135deg, #3498db, #2ecc71)"
    },
    "Dark Elegance": {
        "bg": "#1a1a1a",
        "accent": "#e74c3c",
        "text": "#E0E0E0",
        "gradient": "linear-gradient(135deg, #e74c3c, #c0392b)"
    },
    "Dark Nature": {
        "bg": "#1E1E1E",
        "accent": "#27ae60",
        "text": "#E0E0E0",
        "gradient": "linear-gradient(135deg, #27ae60, #2ecc71)"
    },
    "Dark Cosmic": {
        "bg": "#2c0337",
        "accent": "#9b59b6",
        "text": "#E0E0E0",
        "gradient": "linear-gradient(135deg, #9b59b6, #8e44ad)"
    },
    "Dark Ocean": {
        "bg": "#1A2632",
        "accent": "#00a8cc",
        "text": "#E0E0E0",
        "gradient": "linear-gradient(135deg, #00a8cc, #0089a7)"
    }
}

# Welcome animation on first load
if st.session_state.first_load:
    st.balloons()
    st.snow()
    welcome_placeholder = st.empty()
    welcome_placeholder.success("Welcome to the Geospatial Analysis Tool! 🌍")
    time.sleep(3)
    welcome_placeholder.empty()
    st.session_state.first_load = False

# Auto theme changer and animation
current_time = time.time()
if current_time - st.session_state.last_animation >= 30:
    st.session_state.last_animation = current_time
    theme_keys = list(themes.keys())
    st.session_state.theme_index = (st.session_state.theme_index + 1) % len(theme_keys)
    selected_theme = theme_keys[st.session_state.theme_index]
    st.balloons()
else:
    selected_theme = list(themes.keys())[st.session_state.theme_index]

# Get current theme
theme = themes[selected_theme]

# Apply dark styling
st.markdown(f"""
    <style>
        /* Global Styles */
        .main {{
            background-color: {theme["bg"]};
            color: {theme["text"]};
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        /* Header Styles */
        h1 {{
            background: {theme["gradient"]};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 2rem;
            text-align: center;
            animation: fadeIn 1.5s ease-in;
        }}
        
        /* Section Cards */
        .section-card {{
            background: {theme["bg"]};
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            border-left: 5px solid {theme["accent"]};
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            animation: slideIn 0.5s ease-out;
            color: {theme["text"]};
        }}
        
        .section-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.5);
            background: #2E2E2E;
        }}
        
        /* Section Headers */
        .section-header {{
            color: {theme["accent"]};
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }}
        
        /* Content Text */
        .content-text {{
            line-height: 1.6;
            color: {theme["text"]};
        }}
        
        /* Image Container */
        .img-container {{
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            animation: scaleIn 1s ease;
            background: {theme["bg"]};
        }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        @keyframes slideIn {{
            from {{ transform: translateX(-20px); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        
        @keyframes scaleIn {{
            from {{ transform: scale(0.95); opacity: 0; }}
            to {{ transform: scale(1); opacity: 1; }}
        }}
    </style>
""", unsafe_allow_html=True)

# Title and Image

st.markdown("""
    <h1 class="title">
        Automated Geospatial Analysis for Sub-National Tailoring of Malaria Interventions
    </h1>
""", unsafe_allow_html=True)

# Adding the title again with custom styling
st.markdown("""
    <h1 class="custom-title">
        Automated Geospatial Analysis for Sub-National Tailoring of Malaria Interventions
    </h1>
""", unsafe_allow_html=True)


# Center the image using markdown with HTML attributes
st.markdown("""
    <p align="center">
        <img src="https://github.com/mohamedsillahkanu/si/raw/b0706926bf09ba23d8e90c394fdbb17e864121d8/Sierra%20Leone%20Map.png" 
             width="30%"
             style="display: block; margin-left: auto; margin-right: auto;">
    </p>
""", unsafe_allow_html=True)


# Content Sections
import streamlit as st
import pandas as pd
import numpy as np
from jellyfish import jaro_winkler_similarity
from io import BytesIO
from PIL import Image

st.image("https://raw.githubusercontent.com/mohamedsillahkanu/si/4a7954a650c20056f19da5a77fe5d09ed4e49526/welcome-animation.svg", caption="Welcome Animation")


def calculate_match(column1, column2, threshold):
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
    st.title("Health Facility Name Matching")

    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'master_hf_list' not in st.session_state:
        st.session_state.master_hf_list = None
    if 'health_facilities_dhis2_list' not in st.session_state:
        st.session_state.health_facilities_dhis2_list = None

    # Step 1: File Upload
    if st.session_state.step == 1:
        st.header("Step 1: Upload Files")
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
                st.subheader("Preview of Master HF List")
                st.dataframe(st.session_state.master_hf_list.head())
                st.subheader("Preview of DHIS2 HF List")
                st.dataframe(st.session_state.health_facilities_dhis2_list.head())

                if st.button("Proceed to Column Renaming"):
                    st.session_state.step = 2
                    st.experimental_rerun()

            except Exception as e:
                st.error(f"Error reading files: {e}")

    # Step 2: Column Renaming
    elif st.session_state.step == 2:
        st.header("Step 2: Rename Columns (Optional)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Master HF List Columns")
            mfl_renamed_columns = {}
            for col in st.session_state.master_hf_list.columns:
                new_col = st.text_input(f"Rename '{col}' to:", key=f"mfl_{col}", value=col)
                mfl_renamed_columns[col] = new_col

        with col2:
            st.subheader("DHIS2 HF List Columns")
            dhis2_renamed_columns = {}
            for col in st.session_state.health_facilities_dhis2_list.columns:
                new_col = st.text_input(f"Rename '{col}' to:", key=f"dhis2_{col}", value=col)
                dhis2_renamed_columns[col] = new_col

        if st.button("Apply Changes and Continue"):
            st.session_state.master_hf_list = st.session_state.master_hf_list.rename(columns=mfl_renamed_columns)
            st.session_state.health_facilities_dhis2_list = st.session_state.health_facilities_dhis2_list.rename(
                columns=dhis2_renamed_columns)
            st.session_state.step = 3
            st.experimental_rerun()

        if st.button("Skip Renaming"):
            st.session_state.step = 3
            st.experimental_rerun()

    # Step 3: Column Selection and Matching
    elif st.session_state.step == 3:
        st.header("Step 3: Select Columns for Matching")
        
        mfl_col = st.selectbox("Select HF Name column in Master HF List:", 
                              st.session_state.master_hf_list.columns)
        dhis2_col = st.selectbox("Select HF Name column in DHIS2 HF List:", 
                                st.session_state.health_facilities_dhis2_list.columns)
        
        threshold = st.slider("Set Match Threshold (0-100):", 
                            min_value=0, max_value=100, value=70)

        if st.button("Perform Matching"):
            # Process data
            master_hf_list_clean = st.session_state.master_hf_list.copy()
            dhis2_list_clean = st.session_state.health_facilities_dhis2_list.copy()
            
            master_hf_list_clean[mfl_col] = master_hf_list_clean[mfl_col].astype(str)
            master_hf_list_clean = master_hf_list_clean.drop_duplicates(subset=[mfl_col])
            dhis2_list_clean[dhis2_col] = dhis2_list_clean[dhis2_col].astype(str)

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

                # Rename columns and add new column for replacements
                hf_name_match_results = hf_name_match_results.rename(
                    columns={'Col1': 'HF_Name_in_MFL', 'Col2': 'HF_Name_in_DHIS2'}
                )
                hf_name_match_results['New_HF_Name_in_MFL'] = np.where(
                    hf_name_match_results['Match_Score'] >= threshold,
                    hf_name_match_results['HF_Name_in_DHIS2'],
                    hf_name_match_results['HF_Name_in_MFL']
                )

                # Display results
                st.write("### Matching Results")
                st.dataframe(hf_name_match_results)

                # Download results
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    hf_name_match_results.to_excel(writer, index=False)
                output.seek(0)

                st.download_button(
                    label="Download Matching Results as Excel",
                    data=output,
                    file_name="hf_name_matching_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        if st.button("Start Over"):
            st.session_state.step = 1
            st.session_state.master_hf_list = None
            st.session_state.health_facilities_dhis2_list = None
            st.experimental_rerun()

if __name__ == "__main__":
    main()

# Sidebar theme selector
st.sidebar.selectbox(
    "🎨 Select Theme",
    list(themes.keys()),
    index=st.session_state.theme_index,
    key='theme_selector'
)

# Enable/Disable animations toggle
if st.sidebar.checkbox("Enable Auto Animations", value=True):
    def show_periodic_animations():
        while True:
            time.sleep(60)
            st.balloons()
            time.sleep(10)
            st.snow()

    # Start animation thread if not already running
    if not hasattr(st.session_state, 'animation_thread'):
        st.session_state.animation_thread = threading.Thread(target=show_periodic_animations)
        st.session_state.animation_thread.daemon = True
        st.session_state.animation_thread.start()
