import streamlit as st
from io import BytesIO
import pandas as pd
import numpy as np

# Function to detect outliers using Scatterplot with Q1 and Q3 lines
def detect_outliers_scatterplot(df, col):
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return lower_bound, upper_bound

# Function to apply winsorization to a column
def winsorize_series(series, lower_bound, upper_bound):
    return series.clip(lower=lower_bound, upper=upper_bound)

# Function to process and export the results for a single column using Winsorization
def process_column_winsorization(df, column):
    grouped = df.groupby(['hf_uid', 'year'])
    results = []

    for (hf_uid, year), group in grouped:
        lower_bound, upper_bound = detect_outliers_scatterplot(group, column)
        group[f'{column}_lower_bound'] = lower_bound
        group[f'{column}_upper_bound'] = upper_bound
        group[f'{column}_category'] = np.where(
            (group[column] < lower_bound) | (group[column] > upper_bound), 'Outlier', 'Non-Outlier'
        )
        group[f'{column}_winsorized'] = winsorize_series(group[column], lower_bound, upper_bound)
        results.append(group)

    final_df = pd.concat(results)
    export_columns = [
        'adm1', 'adm2', 'adm3', 'hf', 'hf_uid', 'year', 'month', 'date', column,
        f'{column}_category', f'{column}_lower_bound', f'{column}_upper_bound',
        f'{column}_winsorized'
    ]
    export_columns = [col for col in export_columns if col in final_df.columns]
    return final_df[export_columns]

# Streamlit app setup
st.title("Outlier Detection and Winsorization")

uploaded_file = st.file_uploader("Upload key_variables.csv:", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()

    st.write("### Preview of the uploaded dataset:")
    st.write(df.head())
  
    st.snow()
    st.balloons()

    columns_to_process = ['allout', 'susp', 'test', 'conf', 'maltreat', 'pres', 'maladm', 'maldth']
    processed_dfs = []

    for column in columns_to_process:
        if column not in df.columns:
            st.warning(f"Skipping column {column} as it does not exist in the dataset.")
            continue
        if df[column].isnull().all():
            st.warning(f"Skipping column {column} as it contains only missing values.")
            continue

        st.write(f"Processing column: {column}")
        processed_df = process_column_winsorization(df, column)
        processed_dfs.append(processed_df)

        st.write(f"### Processed Data for {column}:")
        st.write(processed_df.head())

    if processed_dfs:
        merge_keys = ['adm1', 'adm2', 'adm3', 'hf', 'hf_uid', 'year', 'month']
        final_combined_df = processed_dfs[0]
        for df_to_merge in processed_dfs[1:]:
            final_combined_df = final_combined_df.merge(df_to_merge, on=merge_keys, how='outer')

        st.write("### Final Combined Data:")
        st.write(final_combined_df.head())

        # Export combined DataFrame
        combined_buffer = BytesIO()
        final_combined_df.to_csv(combined_buffer, index=False)
        st.download_button(
            label="Download Winsorized Data",
            data=combined_buffer.getvalue(),
            file_name="outlier_corrected_data.csv",
            mime="text/csv"
        )
