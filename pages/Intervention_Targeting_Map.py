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

# Define color options with hex codes
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

# Display colors in a horizontal layout
st.subheader("Available Colors")
cols = st.columns(5)
for i, (color_name, hex_code) in enumerate(nice_colors.items()):
    with cols[i % 5]:
        st.markdown(
            f'<div style="background-color:{hex_code}; padding:5px; margin:2px; color:{"#000000" if color_name in ["White", "Light Gray", "Silver"] else "#FFFFFF"}; border:1px solid #CCCCCC; text-align:center;">{color_name}</div>',
            unsafe_allow_html=True
        )

# File upload
uploaded_file = st.file_uploader("Upload Excel or CSV file", type=["xlsx", "csv"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)

    excluded_columns = ['FIRST_DNAM', 'FIRST_CHIE', 'adm3']
    available_columns = [col for col in df.columns if col not in excluded_columns]

    map_column = st.selectbox("Select Map Column:", available_columns)
    map_title = st.text_input("Map Title:")
    legend_title = st.text_input("Legend Title:")
    image_name = st.text_input("Image Name:", value="Generated_Map")
    font_size = st.slider("Font Size (for Map Title):", 8, 24, 15)

    # Line settings
    line_color_map = {
        "White": "#FFFFFF",
        "Black": "#000000", 
        "Red": "#FF0000",
        "Gray": "#808080",
        "Dark Gray": "#404040",
        "Light Gray": "#D3D3D3",  # ✅ Fixed invalid name
        "Blue": "#0000FF",
        "Green": "#008000"
    }
    line_color = st.selectbox("Select Default Line Color:", options=list(line_color_map.keys()), index=1)
    line_width = st.slider("Select Default Line Width:", 0.5, 5.0, 2.5)

    # Missing value settings
    missing_value_color = st.selectbox("Select Color for Missing Values:", ["White", "Gray", "Red", "Light Gray"], index=1)
    missing_value_label = st.text_input("Label for Missing Values:", value="No Data")

    # Legend position
    legend_positions = {
        "Top Right": 'upper right',
        "Top Left": 'upper left',
        "Bottom Right": 'lower right',
        "Bottom Left": 'lower left',
        "Center Right": 'center right',
        "Center Left": 'center left',
        "Top Center": 'upper center',
        "Bottom Center": 'lower center',
        "Center": 'center'
    }
    legend_position = st.selectbox("Select Legend Position:", list(legend_positions.keys()), index=0)

    # Select categories
    unique_values = sorted(df[map_column].dropna().unique().tolist())
    selected_categories = st.multiselect(f"Select Categories for the Legend of {map_column}:", unique_values, default=unique_values)

    # If categories are selected, proceed
    if selected_categories:
        df[map_column] = pd.Categorical(df[map_column], categories=selected_categories, ordered=True)

        # Assign colors to categories
        st.subheader("Select Colors for Categories")
        color_mapping = {}
        for i, category in enumerate(selected_categories):
            default_color = list(nice_colors.keys())[i % len(nice_colors)]
            selected_color_name = st.selectbox(f"Select Color for '{category}':", list(nice_colors.keys()), index=i % len(nice_colors))
            color_mapping[category] = nice_colors[selected_color_name]

        # Generate map
        fig, ax = plt.subplots(figsize=(10, 8))
        gdf.boundary.plot(ax=ax, linewidth=line_width, edgecolor=line_color_map[line_color])

        # Plot each category with its assigned color
        legend_handles = []
        for category, color in color_mapping.items():
            sub_gdf = gdf[gdf["FIRST_CHIE"].isin(df[df[map_column] == category]["FIRST_CHIE"])]
            if not sub_gdf.empty:
                sub_gdf.plot(ax=ax, color=color, edgecolor=line_color_map[line_color], linewidth=line_width)
                legend_handles.append(Patch(facecolor=color, edgecolor="black", label=category))

        # Handle missing values
        missing_gdf = gdf[~gdf["FIRST_CHIE"].isin(df["FIRST_CHIE"])]
        if not missing_gdf.empty:
            missing_gdf.plot(ax=ax, color=line_color_map[missing_value_color], edgecolor=line_color_map[line_color], linewidth=line_width)
            legend_handles.append(Patch(facecolor=line_color_map[missing_value_color], edgecolor="black", label=missing_value_label))

        # Add legend
        legend = ax.legend(handles=legend_handles, title=legend_title, loc=legend_positions[legend_position])

        # Add title
        ax.set_title(map_title, fontsize=font_size)

        # Remove axes
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)

        # Save image
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=300)
        buf.seek(0)

        st.image(buf, caption="Generated Map", use_column_width=True)
        st.download_button("Download Map", buf, file_name=f"{image_name}.png", mime="image/png")
