import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit App Title
st.title("Health Facility (HF) Filter & Summary")

# File uploader
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xls", "xlsx"])

if uploaded_file:
    # Read file based on extension
    file_extension = uploaded_file.name.split(".")[-1]
    if file_extension in ["xls", "xlsx"]:
        df = pd.read_excel(uploaded_file)
    elif file_extension == "csv":
        df = pd.read_csv(uploaded_file)

    # Ensure 'hf' column exists
    if 'hf' not in df.columns:
        st.error("The uploaded file must contain a column named 'hf'.")
    else:
        # Drop duplicate 'hf' values to ensure unique facilities
        df_unique = df.drop_duplicates(subset=['hf'])

        # Filter rows with specific HF types
        hf_types = ["CHC", "MCHP", "Clinic", "Hospital", "CHP"]
        pattern = r'\b(' + '|'.join(hf_types) + r')\b'
        filtered_df = df_unique[df_unique['hf'].str.contains(pattern, regex=True, na=False)]

        # Display total count of unique HFs
        total_hfs = filtered_df.shape[0]
        st.subheader(f"Total Unique Health Facilities: {total_hfs}")

        # Count occurrences of each HF type
        type_counts = {hf_type: filtered_df['hf'].str.contains(hf_type).sum() for hf_type in hf_types}
        type_counts_df = pd.DataFrame(list(type_counts.items()), columns=["HF Type", "Count"])

        # Display DataFrame
        st.dataframe(type_counts_df)

        # Bar Chart
        st.subheader("Unique HF Count by Type")
        fig, ax = plt.subplots()
        ax.bar(type_counts_df["HF Type"], type_counts_df["Count"], color=["blue", "green", "red", "orange", "purple"])
        ax.set_ylabel("Count")
        ax.set_xlabel("Health Facility Type")
        ax.set_title("Distribution of Unique Health Facility Types")
        st.pyplot(fig)

        # Download filtered unique data
        st.download_button(
            label="Download Filtered Unique HF Data",
            data=filtered_df.to_csv(index=False),
            file_name="filtered_unique_hf_data.csv",
            mime="text/csv"
        )
