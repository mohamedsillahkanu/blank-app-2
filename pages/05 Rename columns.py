import streamlit as st
import pandas as pd

def rename_columns(df):
    try:
        orgunit_rename = {
            'orgunitlevel1': 'adm0',
            'orgunitlevel2': 'adm1',
            'orgunitlevel3': 'adm2',
            'orgunitlevel4': 'adm3',
            'organisationunitname': 'hf'
        }

        column_rename = {
            "OPD (New and follow-up curative) 0-59m_X": "allout_u5",
            "OPD (New and follow-up curative) 5+y_X": "allout_ov5",
            "Admission - Child with malaria 0-59 months_X": "maladm_u5",
            "Admission - Child with malaria 5-14 years_X": "maladm_5_14",
            "Admission - Malaria 15+ years_X": "maladm_ov15",
            "Child death - Malaria 1-59m_X": "maldth_1_59m",
            "Child death - Malaria 10-14y_X": "maldth_10_14",
            "Child death - Malaria 5-9y_X": "maldth_5_9",
            "Death malaria 15+ years Female": "maldth_fem_ov15",
            "Death malaria 15+ years Male": "maldth_mal_ov15",
            "Separation - Child with malaria 0-59 months_X Death": "maldth_u5",
            "Separation - Child with malaria 5-14 years_X Death": "maldth_5_14",
            "Separation - Malaria 15+ years_X Death": "maldth_ov15",
            "Fever case - suspected Malaria 0-59m_X": "susp_u5_hf",
            "Fever case - suspected Malaria 5-14y_X": "susp_5_14_hf",
            "Fever case - suspected Malaria 15+y_X": "susp_ov15_hf",
            "Fever case in community (Suspected Malaria) 0-59m_X": "susp_u5_com",
            "Fever case in community (Suspected Malaria) 5-14y_X": "susp_5_14_com",
            "Fever case in community (Suspected Malaria) 15+y_X": "susp_ov15_com",
            "Fever case in community tested for Malaria (RDT) - Negative 0-59m_X": "tes_neg_rdt_u5_com",
            "Fever case in community tested for Malaria (RDT) - Positive 0-59m_X": "tes_pos_rdt_u5_com",
            "Fever case in community tested for Malaria (RDT) - Negative 5-14y_X": "tes_neg_rdt_5_14_com",
            "Fever case in community tested for Malaria (RDT) - Positive 5-14y_X": "tes_pos_rdt_5_14_com",
            "Fever case in community tested for Malaria (RDT) - Negative 15+y_X": "tes_neg_rdt_ov15_com",
            "Fever case in community tested for Malaria (RDT) - Positive 15+y_X": "tes_pos_rdt_ov15_com",
            "Fever case tested for Malaria (Microscopy) - Negative 0-59m_X": "test_neg_mic_u5_hf",
            "Fever case tested for Malaria (Microscopy) - Positive 0-59m_X": "test_pos_mic_u5_hf",
            "Fever case tested for Malaria (Microscopy) - Negative 5-14y_X": "test_neg_mic_5_14_hf",
            "Fever case tested for Malaria (Microscopy) - Positive 5-14y_X": "test_pos_mic_5_14_hf",
            "Fever case tested for Malaria (Microscopy) - Negative 15+y_X": "test_neg_mic_ov15_hf",
            "Fever case tested for Malaria (Microscopy) - Positive 15+y_X": "test_pos_mic_ov15_hf",
            "Fever case tested for Malaria (RDT) - Negative 0-59m_X": "tes_neg_rdt_u5_hf",
            "Fever case tested for Malaria (RDT) - Positive 0-59m_X": "tes_pos_rdt_u5_hf",
            "Fever case tested for Malaria (RDT) - Negative 5-14y_X": "tes_neg_rdt_5_14_hf",
            "Fever case tested for Malaria (RDT) - Positive 5-14y_X": "tes_pos_rdt_5_14_hf",
            "Fever case tested for Malaria (RDT) - Negative 15+y_X": "tes_neg_rdt_ov15_hf",
            "Fever case tested for Malaria (RDT) - Positive 15+y_X": "tes_pos_rdt_ov15_hf",
            "Malaria treated in community with ACT <24 hours 0-59m_X": "maltreat_u24_u5_com",
            "Malaria treated in community with ACT >24 hours 0-59m_X": "maltreat_ov24_u5_com",
            "Malaria treated in community with ACT <24 hours 5-14y_X": "maltreat_u24_5_14_com",
            "Malaria treated in community with ACT >24 hours 5-14y_X": "maltreat_ov24_5_14_com",
            "Malaria treated in community with ACT <24 hours 15+y_X": "maltreat_u24_ov15_com",
            "Malaria treated in community with ACT >24 hours 15+y_X": "maltreat_ov24_ov15_com",
            "Malaria treated with ACT <24 hours 0-59m_X": "maltreat_u24_u5_hf",
            "Malaria treated with ACT >24 hours 0-59m_X": "maltreat_ov24_u5_hf",
            "Malaria treated with ACT <24 hours 5-14y_X": "maltreat_u24_5_14_hf",
            "Malaria treated with ACT >24 hours 5-14y_X": "maltreat_ov24_5_14_hf",
            "Malaria treated with ACT <24 hours 15+y_X": "maltreat_u24_ov15_hf",
            "Malaria treated with ACT >24 hours 15+y_X": "maltreat_ov24_ov15_hf"
        }

        rename_dict = {**orgunit_rename, **column_rename}
        return df.rename(columns=rename_dict)

    except Exception as e:
        st.error(f"Error renaming columns: {str(e)}")
        return None

def create_hfid(df):
    try:
        df['hf_uid'] = df.groupby(['adm1', 'adm2', 'adm3', 'hf']).ngroup().apply(
            lambda x: f'hf_{x:04d}'
        )
        return df
    except Exception as e:
        st.error(f"Error creating facility IDs: {str(e)}")
        return None

def read_file(file):
    file_type = file.name.split('.')[-1].lower()
    try:
        if file_type == 'csv':
            return pd.read_csv(file)
        elif file_type in ['xlsx', 'xls']:
            return pd.read_excel(file, engine='openpyxl' if file_type == 'xlsx' else 'xlrd')
        else:
            st.error(f"Unsupported file type: {file_type}")
            return None
    except Exception as e:
        st.error(f"Error reading file {file.name}: {str(e)}")
        return None

def process_files(file):
    if file is None:
        return None
    
    df = read_file(file)
    if df is None:
        return None
    
    df = rename_columns(df)
    if df is None:
        return None
        
    df = create_hfid(df)    
    return df

if 'processed_df' not in st.session_state:
    st.session_state.processed_df = None

st.title("Routine Data Uploader")
st.write("Upload the merged routine data downloaded from the merge malaria routine data")

uploaded_file = st.file_uploader("Upload merged data file", type=['xlsx', 'xls', 'csv'])

if uploaded_file:
    processed_df = process_files(uploaded_file)
    
    if processed_df is not None:
        st.session_state.processed_df = processed_df.copy()
        st.success("File processed successfully!")
        with st.expander("View Processed Data"):
            st.dataframe(processed_df)
        
        csv = processed_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Processed Data",
            csv,
            "rename_malaria_routine_data.csv",
            "text/csv"
        )
