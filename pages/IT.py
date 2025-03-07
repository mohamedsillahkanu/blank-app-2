import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import io

# Title
st.title("MAP GENERATOR")
st.subheader("Create customized maps with your data")

# Load the shapefile
gdf = gpd.read_file("https://raw.githubusercontent.com/mohamedsillahkanu/si/2b7f982174b609f9647933147dec2a59a33e736a/Chiefdom%202021.shp")

# Define color options
nice_colors = {
    "Light Blue": "#4CA3DD",
    "Soft Green": "#5DBE7E",
    "Coral": "#FF7F50",
    "Lavender": "#9A7CB7",
    "Gold": "#FFBE4D",
    "Teal": "#35B0AB",
    "Salmon": "#FF9E80",
    "Sky Blue": "#89CFF0",
    "Mint": "#98FB98",
    "Peach": "#FFDAB9",
    "White": "#FFFFFF",
    "Gray": "#808080",
    "Black": "#000000"
}

# File upload
uploaded_file = st.file_uploader("Upload Excel or CSV file", type=["xlsx", "csv"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    available_columns = [col for col in df.columns if col not in ['FIRST_DNAM', 'FIRST_CHIE', 'adm3']]
    
    # User Inputs
    map_column = st.selectbox("Select Map Column:", available_columns)
    map_title = st.text_input("Map Title:")
    legend_title = st.text_input("Legend Title:")
    image_name = st.text_input("Image Name:", value="Generated_Map")
    font_size = st.slider("Font Size (for Map Title):", 8, 24, 15)

    # Missing values settings
    missing_value_color = st.selectbox("Select Color for Missing Values:", list(nice_colors.keys()), index=1)
    missing_value_label = st.text_input("Label for Missing Values:", value="No Data")

    # Select categories
    unique_values = sorted(df[map_column].dropna().unique().tolist())
    selected_categories = st.multiselect(f"Select Categories for {map_column}:", unique_values, default=unique_values)

    if selected_categories:
        df[map_column] = pd.Categorical(df[map_column], categories=selected_categories, ordered=True)
        category_counts = df[map_column].value_counts().to_dict()

        # Assign colors to categories
        st.subheader("Select Colors for Categories")
        color_mapping = {}
        for i, category in enumerate(selected_categories):
            default_color = list(nice_colors.keys())[i % len(nice_colors)]
            selected_color = st.selectbox(f"Select Color for '{category}':", list(nice_colors.keys()), index=list(nice_colors.keys()).index(default_color))
            color_mapping[category] = nice_colors[selected_color]

        # Generate Map Button
        if st.button("Generate Map"):
            try:
                # Merge Data
                merged_gdf = gdf.merge(df, left_on='FIRST_CHIE', right_on='adm3', how='left')

                # Create figure
                fig, ax = plt.subplots(figsize=(10, 8))

                # Plot each category
                legend_handles = []
                for category in selected_categories:
                    sub_gdf = merged_gdf[merged_gdf[map_column] == category]
                    if not sub_gdf.empty:
                        sub_gdf.plot(ax=ax, color=color_mapping[category], edgecolor="white", linewidth=0.5)
                        count = category_counts.get(category, 0)
                        legend_handles.append(Patch(color=color_mapping[category], label=f"{category} ({count})"))

                # Handle missing values
                missing_data = merged_gdf[merged_gdf[map_column].isna()]
                if not missing_data.empty:
                    missing_data.plot(ax=ax, color=nice_colors[missing_value_color], edgecolor="white", linewidth=0.5)
                    legend_handles.append(Patch(color=nice_colors[missing_value_color], label=missing_value_label))

                # Plot boundaries for FIRST_DNAM (black) and FIRST_CHIE (gray)
                merged_gdf.dissolve(by='FIRST_DNAM').boundary.plot(ax=ax, edgecolor="black", linewidth=2.5)
                merged_gdf.dissolve(by='FIRST_CHIE').boundary.plot(ax=ax, edgecolor="gray", linewidth=1.5)

                # Set title and hide axes
                ax.set_title(map_title, fontsize=font_size, fontweight='bold')
                ax.set_axis_off()
                ax.legend(handles=legend_handles, title=legend_title, loc='lower left')

                # Show the map in Streamlit
                st.pyplot(fig)

                # Save map to buffer for download
                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight", dpi=300)
                buf.seek(0)

                # Download button
                st.download_button(
                    label="Download Map",
                    data=buf,
                    file_name=f"{image_name}.png",
                    mime="image/png"
                )

            except Exception as e:
                st.error(f"Error: {e}")
