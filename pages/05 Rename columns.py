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
            "OPD (New and follow-up curative) 0-59m": "allout_u5",
            "OPD (New and follow-up curative) 05+y": "allout_ov5",
            "Admission - Child with malaria 0-59 months": "maladm_u5",
            "Admission - Child with malaria 5-14 years": "maladm_5_14",
            "Admission - Malaria 15+ years": "maladm_ov15",
            
            "Child death - Malaria 01-59m": "maldth_1_59m",
            "Child death - Malaria 05-09y": "maldth_5_9",
            "Child death - Malaria 10-14y": "maldth_10_14",

            "Death malaria 15+ years Female": "maldth_fem_ov15",
            "Death malaria 15+ years Male": "maldth_mal_ov15",
            
            "Separation - Child with malaria 0-59 months Death": "maldth_u5",
            "Separation - Child with malaria 5-14 years Death": "maldth_5_14",
            "Separation - Malaria 15+ years Death": "maldth_ov15",
            "Fever case - suspected Malaria 0-59m": "susp_u5_hf",
            "Fever case - suspected Malaria 05-14y": "susp_5_14_hf",
            "Fever case - suspected Malaria 15+y": "susp_ov15_hf",
            "Fever case (suspected malaria) in HTR and ETR 02-59m": "susp_u5_com",
            "Fever case (suspected malaria) in HTR and ETR 05-14y": "susp_5_14_com",
            "Fever case (suspected malaria) in HTR and ETR 15+y": "susp_ov15_com",
            "Fever case tested for Malaria (RDT) in HTR - Negative 02-59m": "tes_neg_rdt_u5_com",
            "Fever case tested for Malaria (RDT) in HTR - Positive 02-59m": "tes_pos_rdt_u5_com",
            "Fever case tested for Malaria (RDT) in HTR - Negative 05-14y": "tes_neg_rdt_5_14_com",
            "Fever case tested for Malaria (RDT) in HTR - Positive 05-14y": "tes_pos_rdt_5_14_com",
            "Fever case tested for Malaria (RDT) in HTR - Negative 15+y": "tes_neg_rdt_ov15_com",
            "Fever case tested for Malaria (RDT) in HTR - Positive 15+y": "tes_pos_rdt_ov15_com",
            "Fever case tested for Malaria (Microscopy) - Negative 0-59m": "test_neg_mic_u5_hf",
            "Fever case tested for Malaria (Microscopy) - Positive 0-59m": "test_pos_mic_u5_hf",
            "Fever case tested for Malaria (Microscopy) - Negative 05-14y": "test_neg_mic_5_14_hf",
            "Fever case tested for Malaria (Microscopy) - Positive 05-14y": "test_pos_mic_5_14_hf",
            "Fever case tested for Malaria (Microscopy) - Negative 15+y": "test_neg_mic_ov15_hf",
            "Fever case tested for Malaria (Microscopy) - Positive 15+y": "test_pos_mic_ov15_hf",
            "Fever case tested for Malaria (RDT) - Negative 0-59m": "tes_neg_rdt_u5_hf",
            "Fever case tested for Malaria (RDT) - Positive 0-59m": "tes_pos_rdt_u5_hf",
            "Fever case tested for Malaria (RDT) - Negative 05-14y": "tes_neg_rdt_5_14_hf",
            "Fever case tested for Malaria (RDT) - Positive 05-14y": "tes_pos_rdt_5_14_hf",
            "Fever case tested for Malaria (RDT) - Negative 15+y": "tes_neg_rdt_ov15_hf",
            "Fever case tested for Malaria (RDT) - Positive 15+y": "tes_pos_rdt_ov15_hf",
            "Malaria treated with ACT in HTR <24 hours 02-59m": "maltreat_u24_u5_com",
            "Malaria treated with ACT in HTR >24 hours 02-59m": "maltreat_ov24_u5_com",
            "Malaria treated with ACT in HTR <24 hours 05-14y": "maltreat_u24_5_14_com",
            "Malaria treated with ACT in HTR >24 hours 05-14y": "maltreat_ov24_5_14_com",
            "Malaria treated with ACT in HTR <24 hours 15+y": "maltreat_u24_ov15_com",
            "Malaria treated with ACT in HTR >24 hours 15+y": "maltreat_ov24_ov15_com",
            "Malaria treated with ACT <24 hours 0-59m": "maltreat_u24_u5_hf",
            "Malaria treated with ACT >24 hours 0-59m": "maltreat_ov24_u5_hf",
            "Malaria treated with ACT <24 hours 05-14y": "maltreat_u24_5_14_hf",
            "Malaria treated with ACT >24 hours 05-14y": "maltreat_ov24_5_14_hf",
            "Malaria treated with ACT <24 hours 15+y": "maltreat_u24_ov15_hf",
            "Malaria treated with ACT >24 hours 15+y": "maltreat_ov24_ov15_hf"
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
