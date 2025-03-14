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

        # Display summary
        total_unique_hfs = df_unique['hf'].nunique()
        st.subheader(f"Total Unique Health Facilities: {total_unique_hfs}")

        # Count occurrences of each HF type
        hf_types = ["CHC", "MCHP", "Clinic", "Hospital", "CHP"]
        type_counts = {hf_type: df_unique['hf'].str.contains(hf_type, na=False).sum() for hf_type in hf_types}
        type_counts_df = pd.DataFrame(list(type_counts.items()), columns=["HF Type", "Count"])

        # Display HF Type Summary
        st.subheader("Unique HF Count by Type")
        st.dataframe(type_counts_df)

        # Bar Chart
        st.subheader("Distribution of Unique Health Facility Types")
        fig, ax = plt.subplots()
        ax.bar(type_counts_df["HF Type"], type_counts_df["Count"], color=["blue", "green", "red", "orange", "purple"])
        ax.set_ylabel("Count")
        ax.set_xlabel("Health Facility Type")
        ax.set_title("Unique HF Count by Type")
        st.pyplot(fig)

        # Display grouped data
        st.subheader("Unique Health Facilities by Region")
        st.dataframe(grouped_df)

        # Download grouped data
        st.download_button(
            label="Download Grouped Unique HF Data",
            data=grouped_df.to_csv(index=False),
            file_name="grouped_unique_hf_data.csv",
            mime="text/csv"
        )
