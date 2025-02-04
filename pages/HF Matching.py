import streamlit as st
import pandas as pd
import numpy as np
from jellyfish import jaro_winkler_similarity
from io import BytesIO
from PIL import Image
import time
import random
import threading

# Set page config first
st.set_page_config(page_title="Health Facility Matching Tool", page_icon="🏥", layout="wide")



themes = {
    "Black Modern": {
        "bg": "#000000",
        "accent": "#3498db",
        "text": "#FFFFFF",
        "gradient": "linear-gradient(135deg, #3498db, #2ecc71)"
    },
    "Light Silver": {
        "bg": "#F5F5F5",
        "accent": "#1E88E5",
        "text": "#212121",
        "gradient": "linear-gradient(135deg, #1E88E5, #64B5F6)"
    },
    "Light Sand": {
        "bg": "#FAFAFA",
        "accent": "#FF7043",
        "text": "#424242",
        "gradient": "linear-gradient(135deg, #FF7043, #FFB74D)"
    },
    "Light Modern": {
        "bg": "#FFFFFF",
        "accent": "#3498db",
        "text": "#333333",
        "gradient": "linear-gradient(135deg, #3498db, #2ecc71)"
    },
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

st.markdown("""
    <style>
        .stApp {
            background-color: var(--bg-color, #0E1117) !important;
            color: var(--text-color, #E0E0E0) !important;
        }
        
        [data-testid="stSidebar"] {
            background-color: var(--sidebar-bg, #1E1E1E) !important;
            border-right: 1px solid var(--border-color, #2E2E2E);
        }
        
        .stMarkdown, p, h1, h2, h3 {
            color: var(--text-color, #E0E0E0) !important;
        }
        
        .custom-title {
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            padding: 1rem 0;
            margin-bottom: 2rem;
            color: var(--text-color, #E0E0E0) !important;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: block;
            width: 100%;
        }
        
        .stSelectbox > div > div {
            background-color: var(--input-bg, #1E1E1E) !important;
            color: var(--text-color, #E0E0E0) !important;
        }
        
        .stCheckbox > div > div > label {
            color: var(--text-color, #E0E0E0) !important;
        }
        
        .section-card {
            background: var(--card-bg, #1E1E1E) !important;
            color: var(--text-color, #E0E0E0) !important;
            box-shadow: 0 4px 6px var(--shadow-color, rgba(0, 0, 0, 0.3)) !important;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            border-left: 5px solid var(--accent-color, #3498db);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            animation: slideIn 0.5s ease-out;
        }
        
        .section-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px var(--shadow-color, rgba(0, 0, 0, 0.5));
            background: var(--card-hover-bg, #2E2E2E) !important;
        }

        .section-header {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: var(--accent-color, #3498db) !important;
        }
        
        .custom-bullet {
            margin-left: 20px;
            position: relative;
            color: var(--text-color, #E0E0E0) !important;
        }
        .custom-bullet::before {
            content: "•";
            color: var(--text-color, #E0E0E0);
            position: absolute;
            left: -15px;
        }
        
        .content-text {
            color: var(--text-color, #E0E0E0) !important;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideIn {
            from { transform: translateX(-20px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes scaleIn {
            from { transform: scale(0.95); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
    </style>
""", unsafe_allow_html=True)

if 'last_animation' not in st.session_state:
    st.session_state.last_animation = time.time()
    st.session_state.theme_index = list(themes.keys()).index("Black Modern")
    st.session_state.first_load = True

if st.session_state.first_load:
    st.balloons()
    st.snow()
    welcome_placeholder = st.empty()
    welcome_placeholder.success("Welcome to the Geospatial Analysis Tool! 🌍")
    time.sleep(3)
    welcome_placeholder.empty()
    st.session_state.first_load = False

current_time = time.time()
if current_time - st.session_state.last_animation >= 30:
    st.session_state.last_animation = current_time
    theme_keys = list(themes.keys())
    st.session_state.theme_index = (st.session_state.theme_index + 1) % len(theme_keys)
    st.balloons()
else:
    selected_theme = list(themes.keys())[st.session_state.theme_index]

selected_theme = st.sidebar.selectbox(
    "🎨 Select Theme",
    list(themes.keys()),
    index=st.session_state.theme_index,
    key='theme_selector'
)

# Trigger animations on theme change
if 'previous_theme' not in st.session_state:
    st.session_state.previous_theme = selected_theme
if st.session_state.previous_theme != selected_theme:
    st.balloons()
    st.snow()
    st.session_state.previous_theme = selected_theme

theme = themes[selected_theme]
is_light_theme = "Light" in selected_theme

st.markdown(f"""
    <style>
        :root {{
            --bg-color: {theme['bg']};
            --text-color: {theme['text']};
            --accent-color: {theme['accent']};
            --gradient: {theme['gradient']};
            --sidebar-bg: {theme['bg']};
            --card-bg: {'#F8F9FA' if is_light_theme else '#1E1E1E'};
            --card-hover-bg: {'#E9ECEF' if is_light_theme else '#2E2E2E'};
            --input-bg: {'#F8F9FA' if is_light_theme else '#1E1E1E'};
            --shadow-color: {f'rgba(0, 0, 0, 0.1)' if is_light_theme else 'rgba(0, 0, 0, 0.3)'};
            --border-color: {'#DEE2E6' if is_light_theme else '#2E2E2E'};
        }}
    </style>
""", unsafe_allow_html=True)

st.title("Automated Geospatial Analysis for Sub-National Tailoring of Malaria Interventions")

st.markdown("""
    <div class="img-container" style="text-align: center;">
        <img src="https://github.com/mohamedsillahkanu/si/raw/b0706926bf09ba23d8e90c394fdbb17e864121d8/Sierra%20Leone%20Map.png" 
             style="width: 50%; max-width: 500px; margin: 20px auto;">
    </div>
""", unsafe_allow_html=True)




def calculate_match(df1, df2, col1, col2, threshold):
    """Calculate matching scores between two columns using Jaro-Winkler similarity."""
    results = []
    
    for idx1, row1 in df1.iterrows():
        value1 = str(row1[col1])
        if value1 in df2[col2].values:
            # Exact match
            matched_row = df2[df2[col2] == value1].iloc[0]
            result_row = {
                f'MFL_{col1}': value1,
                f'DHIS2_{col2}': value1,
                'Match_Score': 100,
                'Match_Status': 'Match',
                'New_HF_name_in_MFL': value1
            }
            # Add all columns from both dataframes
            for c in df1.columns:
                if c != col1:
                    result_row[f'MFL_{c}'] = row1[c]
            for c in df2.columns:
                if c != col2:
                    result_row[f'DHIS2_{c}'] = matched_row[c]
            results.append(result_row)
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
            
            result_row = {
                f'MFL_{col1}': value1,
                f'DHIS2_{col2}': best_match_row[col2] if best_match_row is not None else None,
                'Match_Score': round(best_score, 2),
                'Match_Status': 'Unmatch' if best_score < threshold else 'Match',
                'New_HF_name_in_MFL': best_match_row[col2] if best_score >= threshold else value1
            }
            # Add all columns from both dataframes
            for c in df1.columns:
                if c != col1:
                    result_row[f'MFL_{c}'] = row1[c]
            for c in df2.columns:
                if c != col2:
                    result_row[f'DHIS2_{c}'] = best_match_row[c] if best_match_row is not None else None
            results.append(result_row)
    
    # Add unmatched facilities from DHIS2
    for idx2, row2 in df2.iterrows():
        value2 = str(row2[col2])
        if value2 not in [str(r[f'DHIS2_{col2}']) for r in results]:
            result_row = {
                f'MFL_{col1}': None,
                f'DHIS2_{col2}': value2,
                'Match_Score': 0,
                'Match_Status': 'Unmatch',
                'New_HF_name_in_MFL': None
            }
            # Add all columns from both dataframes
            for c in df1.columns:
                if c != col1:
                    result_row[f'MFL_{c}'] = None
            for c in df2.columns:
                if c != col2:
                    result_row[f'DHIS2_{c}'] = row2[c]
            results.append(result_row)
    
    return pd.DataFrame(results)

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
            with st.spinner("Performing matching..."):
                hf_name_match_results = calculate_match(
                    master_hf_list_clean,
                    dhis2_list_clean,
                    mfl_col,
                    dhis2_col,
                    threshold
                )

                # Display results
                st.markdown('<div class="section-header">Matching Results</div>', unsafe_allow_html=True)
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
        
        st.markdown('</div>', unsafe_allow_html=True)



for i, (title, content) in enumerate(sections.items()):
    time.sleep(0.2)
    st.markdown(f"""
        <div class="section-card">
            <div class="section-header">{title}</div>
            <div class="content-text">{content}</div>
        </div>
    """, unsafe_allow_html=True)

def show_confetti():
    st.markdown("""
        <style>
            @keyframes confetti {
                0% { transform: translateY(0) rotate(0deg); }
                100% { transform: translateY(100vh) rotate(360deg); }
            }
            .confetti {
                position: fixed;
                animation: confetti 4s linear;
                z-index: 9999;
            }
        </style>
    """, unsafe_allow_html=True)
    for i in range(50):
        color = f"hsl({random.randint(0, 360)}, 100%, 50%)"
        left = random.randint(0, 100)
        st.markdown(f"""
            <div class="confetti" style="left: {left}vw; background: {color}; 
            width: 10px; height: 10px; border-radius: 50%;"></div>
        """, unsafe_allow_html=True)

def show_sparkles():
    st.markdown("""
        <style>
            @keyframes sparkle {
                0% { transform: scale(0); opacity: 0; }
                50% { transform: scale(1); opacity: 1; }
                100% { transform: scale(0); opacity: 0; }
            }
            .sparkle {
                position: fixed;
                animation: sparkle 2s infinite;
            }
        </style>
    """, unsafe_allow_html=True)
    for i in range(20):
        left = random.randint(0, 100)
        top = random.randint(0, 100)
        st.markdown(f"""
            <div class="sparkle" style="left: {left}vw; top: {top}vh; 
            background: gold; width: 5px; height: 5px; border-radius: 50%;"></div>
        """, unsafe_allow_html=True)

def show_fireworks():
    animations = [st.balloons(), st.snow(), show_confetti(), show_sparkles()]
    random.choice(animations)

animations_list = [
    st.balloons,
    st.snow,
    show_confetti,
    show_sparkles,
    show_fireworks,
    lambda: [st.balloons(), st.snow()],
    lambda: [show_confetti(), show_sparkles()],
    lambda: [st.balloons(), show_confetti()],
    lambda: [st.snow(), show_sparkles()],
    lambda: [show_confetti(), st.snow()]
]

# Update theme change animation
if 'previous_theme' not in st.session_state:
    st.session_state.previous_theme = selected_theme
if st.session_state.previous_theme != selected_theme:
    random.choice(animations_list)()
    st.session_state.previous_theme = selected_theme

# Update periodic animations
if st.sidebar.checkbox("Enable Auto Animations", value=True):
    def show_periodic_animations():
        while True:
            time.sleep(60)
            random.choice(animations_list)()
            time.sleep(10)
            random.choice(animations_list)()

    if not hasattr(st.session_state, 'animation_thread'):
        st.session_state.animation_thread = threading.Thread(target=show_periodic_animations)
        st.session_state.animation_thread.daemon = True
        st.session_state.animation_thread.start()

if __name__ == "__main__":
    main()
