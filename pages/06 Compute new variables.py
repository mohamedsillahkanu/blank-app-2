import streamlit as st
import pandas as pd
import numpy as np

st.title("Routine Data Uploader")
st.write("Upload the rename_malaria_routine_data.csv downloaded")

def create_variables(df):
    try:
        # allout
        df['allout'] = df[['allout_u5', 'allout_ov5']].sum(axis=1, min_count=1)
        
        susp_cols = ['susp_u5_hf', 'susp_5_14_hf', 'susp_ov15_hf',
                     'susp_u5_com', 'susp_5_14_com', 'susp_ov15_com']
        df['susp'] = df[susp_cols].sum(axis=1, min_count=1)
        
        # test_hf
        test_hf_cols = ['test_neg_mic_u5_hf', 'test_pos_mic_u5_hf', 'test_neg_mic_5_14_hf',
                      'test_pos_mic_5_14_hf', 'test_neg_mic_ov15_hf', 'test_pos_mic_ov15_hf',
                      'tes_neg_rdt_u5_hf', 'tes_pos_rdt_u5_hf', 'tes_neg_rdt_5_14_hf',
                      'tes_pos_rdt_5_14_hf', 'tes_neg_rdt_ov15_hf', 'tes_pos_rdt_ov15_hf']
        df['test_hf'] = df[test_hf_cols].sum(axis=1, min_count=1)
        
        test_com_cols = ['tes_neg_rdt_u5_com', 'tes_pos_rdt_u5_com', 'tes_neg_rdt_5_14_com',
                      'tes_pos_rdt_5_14_com', 'tes_neg_rdt_ov15_com', 'tes_pos_rdt_ov15_com']
        df['test_com'] = df[test_com_cols].sum(axis=1, min_count=1)
        
        df['test'] = df[['test_hf', 'test_com']].sum(axis=1, min_count=1)
        
        conf_hf_cols = ['test_pos_mic_u5_hf', 'test_pos_mic_5_14_hf', 'test_pos_mic_ov15_hf',
                      'tes_pos_rdt_u5_hf', 'tes_pos_rdt_5_14_hf', 'tes_pos_rdt_ov15_hf']
        df['conf_hf'] = df[conf_hf_cols].sum(axis=1, min_count=1)
        
        conf_com_cols = ['tes_pos_rdt_u5_com', 'tes_pos_rdt_5_14_com', 'tes_pos_rdt_ov15_com']
        df['conf_com'] = df[conf_com_cols].sum(axis=1, min_count=1)
        
        df['conf'] = df[['conf_hf', 'conf_com']].sum(axis=1, min_count=1)
        
        maltreat_com_cols = ['maltreat_u24_u5_com', 'maltreat_ov24_u5_com', 'maltreat_u24_5_14_com',
                          'maltreat_ov24_5_14_com', 'maltreat_u24_ov15_com', 'maltreat_ov24_ov15_com']
        df['maltreat_com'] = df[maltreat_com_cols].sum(axis=1, min_count=1)
        
        maltreat_hf_cols = ['maltreat_u24_u5_hf', 'maltreat_ov24_u5_hf', 'maltreat_u24_5_14_hf',
                         'maltreat_ov24_5_14_hf', 'maltreat_u24_ov15_hf', 'maltreat_ov24_ov15_hf']
        df['maltreat_hf'] = df[maltreat_hf_cols].sum(axis=1, min_count=1)
        
        df['maltreat'] = df[['maltreat_hf', 'maltreat_com']].sum(axis=1, min_count=1)
        
        df['pres_com'] = np.maximum(df['maltreat_com'].fillna(0) - df['conf_com'].fillna(0), 0)
        df['pres_hf'] = np.maximum(df['maltreat_hf'].fillna(0) - df['conf_hf'].fillna(0), 0)
        df['pres'] = df[['pres_com', 'pres_hf']].sum(axis=1, min_count=1)
        
        df['maladm'] = df[['maladm_u5', 'maladm_5_14', 'maladm_ov15']].sum(axis=1, min_count=1)
        
        maldth_cols = ['maldth_u5', 'maldth_1_59m', 'maldth_10_14', 'maldth_5_9',
                     'maldth_5_14', 'maldth_ov15', 'maldth_fem_ov15', 'maldth_mal_ov15']
        df['maldth'] = df[maldth_cols].sum(axis=1, min_count=1)
        
        return df
        
    except Exception as e:
        st.error(f"Error processing variables: {str(e)}")
        return None

uploaded_file = st.file_uploader("Upload data file", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine='openpyxl' if uploaded_file.name.endswith('.xlsx') else 'xlrd')
            
        if df is not None:
            st.success("File loaded successfully")
            processed_df = create_variables(df)
            
            if processed_df is not None:
                st.success("Variables created successfully")
                with st.expander("View Processed Data"):
                    st.dataframe(processed_df)
                
                # Full data download
                csv = processed_df.to_csv(index=False).encode('utf-8')

                st.balloons()
                st.snow()
                st.download_button(
                    "Download Full Data",
                    csv,
                    "compute_variables_data.csv",
                    "text/csv"
                )
                
                # Selected columns download
                selected_cols = ['adm1', 'adm2', 'adm3', 'hf', 'hf_uid', 'year', 'month', 
                               'Date', 'allout', 'susp', 'test', 'conf', 'maltreat', 
                               'pres', 'maladm', 'maldth']
                selected_df = processed_df[selected_cols]
                csv_selected = selected_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download Selected Columns",
                    csv_selected,
                    "key_variables.csv",
                    "text/csv"
                )
                
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
