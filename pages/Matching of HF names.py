import streamlit as st
import pandas as pd
import numpy as np
from jellyfish import jaro_winkler_similarity
from io import BytesIO
import time
import threading

st.set_page_config(page_title="Health Facility Matching Tool", page_icon="🏥", layout="wide")

st.markdown("""
   <style>
       * { font-weight: bold !important; font-size: 1.1rem !important; }
       .stApp { background-color: var(--bg-color, #0E1117) !important; }
       [data-testid="stSidebar"] {
           background-color: var(--sidebar-bg, #1E1E1E) !important;
           border-right: 1px solid var(--border-color, #2E2E2E);
       }
       .stMarkdown, p, h1, h2, h3 { color: var(--text-color, #E0E0E0) !important; }
       .custom-title {
           font-size: 2.7rem !important;
           font-weight: 700;
           text-align: center;
           padding: 1rem 0;
           margin-bottom: 2rem;
           color: var(--text-color, #E0E0E0) !important;
           background: var(--gradient);
           -webkit-background-clip: text;
           -webkit-text-fill-color: transparent;
       }
       .stSelectbox > div > div {
           background-color: var(--input-bg, #1E1E1E) !important;
           color: var(--text-color, #E0E0E0) !important;
       }
       .stCheckbox > div > div > label { color: var(--text-color, #E0E0E0) !important; }
       .section-card {
           background: var(--card-bg, #1E1E1E) !important;
           color: var(--text-color, #E0E0E0) !important;
           box-shadow: 0 4px 6px var(--shadow-color, rgba(0, 0, 0, 0.3)) !important;
           border-radius: 15px;
           padding: 25px;
           margin: 20px 0;
           border-left: 5px solid var(--accent-color, #3498db);
           transition: transform 0.3s ease;
       }
       .section-card:hover {
           transform: translateY(-5px);
           background: var(--card-hover-bg, #2E2E2E) !important;
       }
       .section-header {
           font-size: 1.7rem !important;
           font-weight: bold;
           margin-bottom: 1rem;
           color: var(--accent-color, #3498db) !important;
       }
       .dataframe {
           background-color: var(--card-bg, #1E1E1E) !important;
           color: var(--text-color, #E0E0E0) !important;
       }
       .stFileUploader {
           background-color: var(--input-bg, #1E1E1E) !important;
           border: 1px solid var(--accent-color, #3498db) !important;
       }
       .stButton button {
           background-color: var(--accent-color, #3498db) !important;
           color: var(--text-color, #E0E0E0) !important;
       }
       .stTextInput input {
           color: var(--text-color, #000000) !important;
           background-color: var(--input-bg, #FFFFFF) !important;
       }
   </style>
""", unsafe_allow_html=True)

themes = {
   "Black Modern": {
       "bg": "#000000", "accent": "#3498db", "text": "#FFFFFF",
       "gradient": "linear-gradient(135deg, #3498db, #2ecc71)"
   },
   "Light Silver": {
       "bg": "#F5F5F5", "accent": "#1E88E5", "text": "#212121",
       "gradient": "linear-gradient(135deg, #1E88E5, #64B5F6)"
   },
   "Light Sand": {
       "bg": "#FAFAFA", "accent": "#FF7043", "text": "#424242",
       "gradient": "linear-gradient(135deg, #FF7043, #FFB74D)"
   },
   "Light Modern": {
       "bg": "#FFFFFF", "accent": "#3498db", "text": "#333333",
       "gradient": "linear-gradient(135deg, #3498db, #2ecc71)"
   },
   "Dark Modern": {
       "bg": "#0E1117", "accent": "#3498db", "text": "#E0E0E0",
       "gradient": "linear-gradient(135deg, #3498db, #2ecc71)"
   },
   "Dark Elegance": {
       "bg": "#1a1a1a", "accent": "#e74c3c", "text": "#E0E0E0",
       "gradient": "linear-gradient(135deg, #e74c3c, #c0392b)"
   },
   "Dark Nature": {
       "bg": "#1E1E1E", "accent": "#27ae60", "text": "#E0E0E0",
       "gradient": "linear-gradient(135deg, #27ae60, #2ecc71)"
   },
   "Dark Ocean": {
       "bg": "#1A2632", "accent": "#00a8cc", "text": "#E0E0E0",
       "gradient": "linear-gradient(135deg, #00a8cc, #0089a7)"
   }
}

if 'step' not in st.session_state:
   st.session_state.step = 1
if 'master_hf_list' not in st.session_state:
   st.session_state.master_hf_list = None
if 'health_facilities_dhis2_list' not in st.session_state:
   st.session_state.health_facilities_dhis2_list = None

selected_theme = st.sidebar.selectbox("🎨 Theme:", list(themes.keys()))
theme = themes[selected_theme]
is_light = "Light" in selected_theme

st.markdown(f"""
   <style>
       :root {{
           --bg-color: {theme['bg']};
           --text-color: {theme['text']};
           --accent-color: {theme['accent']};
           --gradient: {theme['gradient']};
           --sidebar-bg: {theme['bg']};
           --card-bg: {'#F8F9FA' if is_light else '#1E1E1E'};
           --card-hover-bg: {'#E9ECEF' if is_light else '#2E2E2E'};
           --input-bg: {'#F8F9FA' if is_light else '#1E1E1E'};
           --shadow-color: {'rgba(0,0,0,0.1)' if is_light else 'rgba(0,0,0,0.3)'};
           --border-color: {'#DEE2E6' if is_light else '#2E2E2E'};
       }}
   </style>
""", unsafe_allow_html=True)

def calculate_match(df1, df2, col1, col2, threshold):
   results = []
   for idx1, row1 in df1.iterrows():
       value1 = str(row1[col1])
       if value1 in df2[col2].values:
           matched_row = df2[df2[col2] == value1].iloc[0]
           result_row = {
               f'MFL_{col1}': value1,
               f'DHIS2_{col2}': value1,
               'Match_Score': 100,
               'Match_Status': 'Match',
               'New_HF_name_in_MFL': value1
           }
       else:
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
       
       for c in df1.columns:
           if c != col1:
               result_row[f'MFL_{c}'] = row1[c]
       for c in df2.columns:
           if c != col2 and best_match_row is not None:
               result_row[f'DHIS2_{c}'] = best_match_row[c]
       
       results.append(result_row)
   
   return pd.DataFrame(results)

def main():
   st.markdown('<h1 class="custom-title">Health Facility Name Matching</h1>', unsafe_allow_html=True)

   if st.session_state.step == 1:
       st.markdown('<div class="section-card">', unsafe_allow_html=True)
       mfl_file = st.file_uploader("Upload Master HF List (CSV, Excel):", type=['csv', 'xlsx'])
       dhis2_file = st.file_uploader("Upload DHIS2 HF List (CSV, Excel):", type=['csv', 'xlsx'])

       if mfl_file and dhis2_file:
           try:
               st.session_state.master_hf_list = pd.read_excel(mfl_file) if mfl_file.name.endswith('xlsx') else pd.read_csv(mfl_file)
               st.session_state.health_facilities_dhis2_list = pd.read_excel(dhis2_file) if dhis2_file.name.endswith('xlsx') else pd.read_csv(dhis2_file)
               
               st.success("Files uploaded successfully!")
               st.markdown('<div class="section-header">Preview of Files</div>', unsafe_allow_html=True)
               st.dataframe(st.session_state.master_hf_list.head())
               st.dataframe(st.session_state.health_facilities_dhis2_list.head())

               if st.button("Proceed to Column Selection"):
                   st.session_state.step = 2
                   st.experimental_rerun()
           except Exception as e:
               st.error(f"Error: {e}")
       st.markdown('</div>', unsafe_allow_html=True)

   elif st.session_state.step == 2:
       st.markdown('<div class="section-card">', unsafe_allow_html=True)
       mfl_col = st.selectbox("Select HF Name column in Master List:", st.session_state.master_hf_list.columns)
       dhis2_col = st.selectbox("Select HF Name column in DHIS2 List:", st.session_state.health_facilities_dhis2_list.columns)
       threshold = st.slider("Match Threshold:", 0, 100, 70)

       if st.button("Perform Matching"):
           with st.spinner("Processing..."):
               results = calculate_match(
                   st.session_state.master_hf_list,
                   st.session_state.health_facilities_dhis2_list,
                   mfl_col, dhis2_col, threshold
               )
               
               st.markdown('<div class="section-header">Results</div>', unsafe_allow_html=True)
               st.dataframe(results, height=600)
               
               output = BytesIO()
               with pd.ExcelWriter(output, engine='openpyxl') as writer:
                   results.to_excel(writer, index=False)
               output.seek(0)
               
               st.download_button(
                   "Download Results",
                   output,
                   "matching_results.xlsx",
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
               )

       if st.button("Start Over"):
           st.session_state.step = 1
           st.session_state.master_hf_list = None
           st.session_state.health_facilities_dhis2_list = None
           st.experimental_rerun()
       st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
   main()
