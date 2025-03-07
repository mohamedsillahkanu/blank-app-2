import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap, to_hex
import io

# Title instead of image
st.title("MAP GENERATOR")
st.subheader("Create customized maps with your data")

# Load the shapefile
gdf = gpd.read_file("https://raw.githubusercontent.com/mohamedsillahkanu/si/2b7f982174b609f9647933147dec2a59a33e736a/Chiefdom%202021.shp")

# Define a nice set of colors that go well with white, including gray colors
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

# Display colors in a more compact horizontal layout
st.subheader("Available Colors")
cols = st.columns(5)  # Create 5 columns for a more compact horizontal display
for i, (color_name, hex_code) in enumerate(nice_colors.items()):
    with cols[i % 5]:
        st.markdown(
            f'<div style="background-color:{hex_code}; padding:5px; margin:2px; color:{"#000000" if color_name in ["White", "Light Gray", "Silver"] else "#FFFFFF"}; border:1px solid #CCCCCC; text-align:center;">{color_name}</div>',
            unsafe_allow_html=True
        )

# File upload (Excel or CSV)
uploaded_file = st.file_uploader("Upload Excel or CSV file", type=["xlsx", "csv"])
if uploaded_file is not None:
    # Read the uploaded file (Excel or CSV)
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    # Exclude certain columns from being selectable for the map
    excluded_columns = ['FIRST_DNAM', 'FIRST_CHIE', 'adm3']
    available_columns = [col for col in df.columns if col not in excluded_columns]

    # UI elements for selecting map settings
    map_column = st.selectbox("Select Map Column:", available_columns)
    map_title = st.text_input("Map Title:")
    legend_title = st.text_input("Legend Title:")
    image_name = st.text_input("Image Name:", value="Generated_Map")
    font_size = st.slider("Font Size (for Map Title):", min_value=8, max_value=24, value=15)

    # Line settings with more color options
    line_colors = ["White", "Black", "Red", "Gray", "Dark Gray", "Light Gray", "Blue", "Green"]
    # Create a mapping for valid matplotlib color names
    line_color_map = {
        "White": "white",
        "Black": "black", 
        "Red": "red",
        "Gray": "gray",
        "Dark Gray": "darkgray",  # No space
        "Light Gray": "lightgray",  # No space
        "Blue": "blue",
        "Green": "green"
    }
    line_color = st.selectbox("Select Default Line Color:", options=line_colors, index=1)
    line_width = st.slider("Select Default Line Width:", min_value=0.5, max_value=5.0, value=2.5)

    # Missing value settings with corrected color mapping
    missing_value_color = st.selectbox("Select Color for Missing Values:", options=["White", "Gray", "Red", "Light Gray"], index=1)
    missing_value_label = st.text_input("Label for Missing Values:", value="No Data")

    # Legend position settings
    legend_positions = {
        "Top Right": ('upper right', (1, 1)),
        "Top Left": ('upper left', (0, 1)),
        "Bottom Right": ('lower right', (1, 0)),
        "Bottom Left": ('lower left', (0, 0)),
        "Center Right": ('center right', (1, 0.5)),
        "Center Left": ('center left', (0, 0.5)),
        "Top Center": ('upper center', (0.5, 1)),
        "Bottom Center": ('lower center', (0.5, 0)),
        "Center": ('center', (0.5, 0.5)),
        "Outside Right": ('center left', (1.05, 0.5)),
        "Outside Bottom": ('upper center', (0.5, -0.15))
    }
    legend_position = st.selectbox("Select Legend Position:", 
                                  options=list(legend_positions.keys()), 
                                  index=0)  # Default to Top Right

    # Initialize category_counts dictionary for managing category counts
    category_counts = {}
    selected_categories = []  # Initialize selected_categories

    # Only categorical variable selection (removed numeric option)
    unique_values = sorted(df[map_column].dropna().unique().tolist())
    selected_categories = st.multiselect(f"Select Categories for the Legend of {map_column}:", unique_values, default=unique_values)
    category_counts = df[map_column].value_counts().to_dict()

    # Reorder the categories
    df[map_column] = pd.Categorical(df[map_column], categories=selected_categories, ordered=True)

    # Proceed with map generation if categories are selected
    if selected_categories:
        # Manual color mapping
        color_mapping = {}
        
        # Color customization for categories
        st.subheader("Select Colors for Categories")
        for i, category in enumerate(selected_categories):
            # Default to a color from our nice colors (cycling through the list)
            default_color = list(nice_colors.keys())[i % len(nice_colors)]
            selected_color_name = st.selectbox(f"Select Color for '{category}':", 
                                              options=list(nice_colors.keys()), 
                                              index=list(nice_colors.keys()).index(default_color))
            color_mapping[category] = nice_colors[selected_color_name]

        # Column1 and Column2 are selected automatically in the background
        shapefile_columns = ['FIRST_DNAM', 'FIRST_CHIE']
        excel_columns = ['FIRST_DNAM', 'FIRST_CHIE']

        # Check if two columns are selected for merging
        if len(shapefile_columns) == 2 and len(excel_columns) == 2:
            column1_line_color = st.selectbox(f"Select Line Color for '{shapefile_columns[0]}' boundaries:", options=line_colors, index=1)
            column1_line_width = st.slider(f"Select Line Width for '{shapefile_columns[0]}' boundaries:", min_value=0.5, max_value=10.0, value=2.5)
            column2_line_color = st.selectbox(f"Select Line Color for '{shapefile_columns[1]}' boundaries:", options=line_colors, index=1)
            column2_line_width = st.slider(f"Select Line Width for '{shapefile_columns[1]}' boundaries:", min_value=0.5, max_value=10.0, value=2.5)

        # Generate the map upon button click
        if st.button("Generate Map"):
            try:
                # Merge the shapefile and Excel data
                merged_gdf = gdf.merge(df, left_on=shapefile_columns, right_on=excel_columns, how='left')

                if map_column not in merged_gdf.columns:
                    st.error(f"The column '{map_column}' does not exist in the merged dataset.")
                else:
                    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

                    # Create a custom colormap from the selected colors
                    colors_list = [color_mapping[cat] for cat in selected_categories]
                    custom_cmap = ListedColormap(colors_list)

                    # Plot the map - use hex colors directly to avoid matplotlib color name issues
                    missing_color_hex = nice_colors.get(missing_value_color, "#D3D3D3")  # Default to light gray hex if not found
                    edge_color_hex = nice_colors.get(line_color, "#000000")  # Default to black hex if not found
                    
                    merged_gdf.plot(
                        column=map_column, 
                        ax=ax, 
                        linewidth=line_width, 
                        edgecolor=line_color_map.get(line_color, "black"),  # Use fallback if not in map
                        cmap=custom_cmap,
                        legend=False, 
                        missing_kwds={
                            'color': line_color_map.get(missing_value_color, "lightgray"),  # Use fallback if not in map
                            'edgecolor': line_color_map.get(line_color, "black"),  # Use fallback if not in map
                            'label': missing_value_label
                        }
                    )
                    
                    ax.set_title(map_title, fontsize=font_size, fontweight='bold')
                    ax.set_axis_off()

                    # Add boundaries for 'FIRST_DNAM' and 'FIRST_CHIE'
                    dissolved_gdf1 = merged_gdf.dissolve(by=shapefile_columns[0])
                    dissolved_gdf1.boundary.plot(
                        ax=ax, 
                        edgecolor=line_color_map.get(column1_line_color, "black"),  # Use fallback if not in map
                        linewidth=column1_line_width
                    )

                    dissolved_gdf2 = merged_gdf.dissolve(by=shapefile_columns[1])
                    dissolved_gdf2.boundary.plot(
                        ax=ax, 
                        edgecolor=line_color_map.get(column2_line_color, "black"),  # Use fallback if not in map
                        linewidth=column2_line_width
                    )

                    # Get legend position settings
                    legend_loc, legend_bbox = legend_positions[legend_position]

                    # Check for missing data in the map column
                    if merged_gdf[map_column].isnull().sum() > 0:
                        # Add missing data to the legend
                        handles = [Patch(color=color_mapping[cat], label=f"{cat} ({category_counts.get(cat, 0)})") for cat in selected_categories]
                        handles.append(Patch(
                            color=line_color_map.get(missing_value_color, "lightgray"),  # Use fallback if not in map
                            label=f"{missing_value_label} ({merged_gdf[map_column].isnull().sum()})"
                        ))
                    else:
                        # Normal legend without missing data
                        handles = [Patch(color=color_mapping[cat], label=f"{cat} ({category_counts.get(cat, 0)})") for cat in selected_categories]

                    # Create legend with bold text and border for white color patches
                    legend = ax.legend(handles=handles, title=legend_title, fontsize=10, 
                                      loc=legend_loc, bbox_to_anchor=legend_bbox, 
                                      frameon=True, fancybox=True, shadow=True)
                    plt.setp(legend.get_title(), fontsize=10, fontweight='bold')
                    plt.setp(legend.get_texts(), fontweight='bold')
                    
                    # Fix: Use legend_handles instead of legendHandles
                    for handle in legend.legend_handles:
                        handle.set_edgecolor('black')
                        handle.set_linewidth(0.5)

                    # Save the map to a BytesIO object for downloading
                    img_bytes = io.BytesIO()
                    plt.savefig(img_bytes, format='png', bbox_inches='tight', pad_inches=0.1)
                    img_bytes.seek(0)

                    # Display the map
                    st.pyplot(fig)

                    # Download button for the generated image
                    st.download_button("Download Map", img_bytes, file_name=f"{image_name}.png", mime="image/png")

            except Exception as e:
                st.error(f"An error occurred while generating the map: {e}")
