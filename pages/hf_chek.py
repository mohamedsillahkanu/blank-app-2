import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit App Title
st.title("Health Facility (HF) Grouping & Summary")

# File uploader
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xls", "xlsx"])

if uploaded_file:
    # Read file based on extension
    file_extension = uploaded_file.name.split(".")[-1]
    if file_extension in ["xls", "xlsx"]:
        df = pd.read_excel(uploaded_file)
    elif file_extension == "csv":
        df = pd.read_csv(uploaded_file)

    # Ensure required columns exist
    required_columns = {'adm1', 'adm2', 'adm3', 'hf'}
    if not required_columns.issubset(df.columns):
        st.error(f"The uploaded file must contain the following columns: {required_columns}")
    else:
        # Drop duplicates to get unique HF per group
        df_unique = df.drop_duplicates(subset=['adm1', 'adm2', 'adm3', 'hf'])

        # Group by 'adm1', 'adm2', 'adm3' and count unique HFs
        grouped_df = df_unique.groupby(['adm1', 'adm2', 'adm3'])['hf'].nunique().reset_index()
        grouped_df.rename(columns={'hf': 'Unique HF Count'}, inplace=True)

        # Display the grouped DataFrame
        st.subheader("Unique Health Facilities by Region")
        st.dataframe(grouped_df)

        # Download grouped data
        st.download_button(
            label="Download Grouped Unique HF Data",
            data=grouped_df.to_csv(index=False),
            file_name="grouped_unique_hf_data.csv",
            mime="text/csv"
        )
