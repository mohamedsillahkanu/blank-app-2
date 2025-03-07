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
    "Light Gray": "#D3D3D3",
    "Gray": "#808080",
    "Dark Gray": "#404040",
    "Silver": "#C0C0C0",
    "Slate Gray": "#708090"
}

# File upload
uploaded_file = st.file_uploader("Upload Excel or CSV file", type=["xlsx", "csv"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)

    available_columns = [col for col in df.columns if col not in ['FIRST_DNAM', 'FIRST_CHIE', 'adm3']]
    map_column = st.selectbox("Select Map Column:", available_columns)
    map_title = st.text_input("Map Title:")
    legend_title = st.text_input("Legend Title:")
    font_size = st.slider("Font Size (for Map Title):", 8, 24, 15)

    # Line settings
    line_color = st.selectbox("Select Default Line Color:", list(nice_colors.keys()), index=1)
    line_width = st.slider("Select Default Line Width:", 0.5, 5.0, 2.5)

    # Missing values settings
    missing_value_color = st.selectbox("Select Color for Missing Values:", list(nice_colors.keys()), index=1)
    missing_value_label = st.text_input("Label for Missing Values:", value="No Data")

    # Select categories
    unique_values = sorted(df[map_column].dropna().unique().tolist())
    selected_categories = st.multiselect(f"Select Categories for {map_column}:", unique_values, default=unique_values)

    if selected_categories:
        df[map_column] = pd.Categorical(df[map_column], categories=selected_categories, ordered=True)

        # Assign colors to categories
        st.subheader("Select Colors for Categories")
        color_mapping = {category: nice_colors[st.selectbox(f"Select Color for '{category}':", list(nice_colors.keys()))] for category in selected_categories}

        # Generate map
        fig, ax = plt.subplots(figsize=(10, 8))
        gdf.boundary.plot(ax=ax, linewidth=line_width, edgecolor=nice_colors[line_color])

        # Plot each category
        for category, color in color_mapping.items():
            sub_gdf = gdf[gdf["FIRST_CHIE"].isin(df[df[map_column] == category]["FIRST_CHIE"])]
            if not sub_gdf.empty:
                sub_gdf.plot(ax=ax, color=color, edgecolor=nice_colors[line_color], linewidth=line_width)

        # Handle missing values
        missing_gdf = gdf[~gdf["FIRST_CHIE"].isin(df[df[map_column].notna()]["FIRST_CHIE"])]
        if not missing_gdf.empty:
            missing_gdf.plot(ax=ax, color=nice_colors[missing_value_color], edgecolor=nice_colors[line_color], linewidth=line_width)

        # Add default legend at the center right
        ax.legend(title=legend_title, loc='center right', fontsize=font_size)

        # Add title
        ax.set_title(map_title, fontsize=font_size)

        # Remove axis
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)

        # Display map in Streamlit
        st.pyplot(fig)

        # Save map as a PNG file
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format="png", dpi=300, bbox_inches="tight")
        img_buffer.seek(0)

        # Add download button
        st.download_button(
            label="Download Map as PNG",
            data=img_buffer,
            file_name="generated_map.png",
            mime="image/png"
        )
