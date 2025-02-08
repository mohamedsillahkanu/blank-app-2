try:
    # Read files directly
    shapefile = gpd.read_file("Chiefdom 2021.shp")
    facility_data = pd.read_excel("master_hf_list.xlsx")

    # Ensure proper CRS for shapefile (assuming it should be in WGS 84)
    if shapefile.crs is None or shapefile.crs != "EPSG:4326":
        shapefile = shapefile.to_crs("EPSG:4326")

    # Create GeoDataFrame from facility data with explicit CRS
    geometry = [Point(xy) for xy in zip(facility_data['w_long'], facility_data['w_lat'])]
    facilities_gdf = gpd.GeoDataFrame(
        facility_data, 
        geometry=geometry,
        crs="EPSG:4326"  # Setting WGS 84 as CRS
    )

    # Verify coordinate ranges
    st.write("Longitude range:", facilities_gdf['w_long'].min(), facilities_gdf['w_long'].max())
    st.write("Latitude range:", facilities_gdf['w_lat'].min(), facilities_gdf['w_lat'].max())
    st.write("Shapefile bounds:", shapefile.total_bounds)
