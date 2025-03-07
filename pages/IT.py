import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

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
    "Slate Gray": "#708090",
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
        category_counts = df[map_column].value_counts().to_dict()

        # Assign colors to categories
        st.subheader("Select Colors for Categories")
        color_mapping = {}
        for i, category in enumerate(selected_categories):
            default_color = list(nice_colors.keys())[i % len(nice_colors)]
            selected_color = st.selectbox(f"Select Color for '{category}':", list(nice_colors.keys()), index=list(nice_colors.keys()).index(default_color))
            color_mapping[category] = nice_colors[selected_color]

        # Custom line settings for boundaries
        first_dnam_color = st.selectbox("Select Color for FIRST_DNAM:", list(nice_colors.keys()), index=0)
        first_dnam_width = st.slider("Select Line Width for FIRST_DNAM:", 0.5, 5.0, 2.5)
        first_chie_color = st.selectbox("Select Color for FIRST_CHIE:", list(nice_colors.keys()), index=1)
        first_chie_width = st.slider("Select Line Width for FIRST_CHIE:", 0.5, 5.0, 2.5)

        # Generate Map Button
        if st.button("Generate Map"):
            try:
                # Merge Data
                merged_gdf = gdf.merge(df, left_on='FIRST_CHIE', right_on='adm3', how='left')

                # Create figure
                fig, ax = plt.subplots(figsize=(10, 8))

                # Plot the default boundaries
                gdf.boundary.plot(ax=ax, linewidth=line_width, edgecolor=nice_colors[line_color])

                # Plot each category
                legend_handles = []
                for category in selected_categories:
                    sub_gdf = merged_gdf[merged_gdf[map_column] == category]
                    if not sub_gdf.empty:
                        sub_gdf.plot(ax=ax, color=color_mapping[category], edgecolor=nice_colors[line_color], linewidth=line_width)
                        count = category_counts.get(category, 0)
                        legend_handles.append(Patch(color=color_mapping[category], label=f"{category} ({count})"))

                # Handle missing values
                missing_data = merged_gdf[merged_gdf[map_column].isna()]
                if not missing_data.empty:
                    missing_data.plot(ax=ax, color=nice_colors[missing_value_color], edgecolor=nice_colors[line_color], linewidth=line_width)
                    legend_handles.append(Patch(color=nice_colors[missing_value_color], label=missing_value_label))

                # Plot boundaries for FIRST_DNAM and FIRST_CHIE
                dissolved_gdf1 = merged_gdf.dissolve(by='FIRST_DNAM')
                dissolved_gdf1.boundary.plot(ax=ax, edgecolor=nice_colors[first_dnam_color], linewidth=first_dnam_width)

                dissolved_gdf2 = merged_gdf.dissolve(by='FIRST_CHIE')
                dissolved_gdf2.boundary.plot(ax=ax, edgecolor=nice_colors[first_chie_color], linewidth=first_chie_width)

                # Set title and hide axes
                ax.set_title(map_title, fontsize=font_size, fontweight='bold')
                ax.set_axis_off()
                ax.legend(handles=legend_handles, title=legend_title, loc='lower left')

                # Show the map in Streamlit
                st.pyplot(fig)

            except Exception as e:
                st.error(f"Error generating map: {e}")
