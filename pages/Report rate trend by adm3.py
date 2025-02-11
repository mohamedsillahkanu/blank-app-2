import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import zipfile
import tempfile
from pathlib import Path
import io

class DistrictTrendAnalyzer:
    def __init__(self):
        """Initialize analyzer"""
        self.df = None
        self.years = list(range(2015, 2024))  # 2015 to 2023
        self.year_cols = [f'conf_rr_{year}' for year in self.years]
        self.temp_dir = tempfile.mkdtemp()

    def load_data(self):
        """Load and prepare the data"""
        try:
            self.df = pd.read_excel("reporting_rate_by_adm3.xlsx")
            st.success("Data successfully loaded!")
            return True
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return False

    def plot_district(self, row):
        """Create individual plot for a single district"""
        district = row['adm3']
        region = row['adm1']
        rates = [row[col] for col in self.year_cols]

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))

        # Add title with extra space
        plt.title(f'Yearly Reporting Rate in {district}, {region}\n', 
                 fontsize=14, pad=20)

        # Plot line
        plt.plot(self.years, rates, marker='o', linewidth=2,
                markersize=8, color='#1f77b4')

        # Add value labels
        for x, y in zip(self.years, rates):
            plt.annotate(f'{y:.1f}%',
                        (x, y),
                        textcoords="offset points",
                        xytext=(0,10),
                        ha='center',
                        fontsize=10)

        # Customize axes
        plt.xlabel('Year', fontsize=12, labelpad=10)
        plt.ylabel('Reporting Rate (%)', fontsize=12, labelpad=10)
        plt.ylim(0, 100)

        # Add grid and reference lines
        plt.grid(True, linestyle='--', alpha=0.3)
        for y in [25, 50, 75]:
            plt.axhline(y=y, color='gray', linestyle='--', alpha=0.2)

        # Set x-axis ticks
        plt.xticks(self.years, rotation=0)

        # Adjust layout
        plt.tight_layout()

        # Save plot to temp directory
        output_file = os.path.join(self.temp_dir, f'{district}.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')

        return fig, output_file

    def create_zip_for_region(self, region_files, region_name):
        """Create a zip file for a specific region"""
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in region_files:
                zipf.write(file, os.path.basename(file))
        memory_file.seek(0)
        return memory_file

    def create_master_zip(self, all_files):
        """Create a zip file containing all plots"""
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in all_files:
                zipf.write(file, os.path.basename(file))
        memory_file.seek(0)
        return memory_file

def main():
    st.title("District Reporting Rate Trend Analysis")
    st.snow()
    st.balloons()

    analyzer = DistrictTrendAnalyzer()

    if analyzer.load_data():
        with st.spinner("Generating plots..."):
            try:
                # Group data by region
                grouped = analyzer.df.groupby('adm1')
                all_plot_files = []

                # Process each region
                for region in sorted(analyzer.df['adm1'].unique()):
                    st.header(f"Region: {region}")
                    group = analyzer.df[analyzer.df['adm1'] == region]
                    region_files = []

                    # Generate plots for this region
                    for idx, row in group.iterrows():
                        district = row['adm3']
                        st.subheader(f"District: {district}")
                        
                        fig, plot_file = analyzer.plot_district(row)
                        st.pyplot(fig)
                        plt.close(fig)
                        
                        region_files.append(plot_file)
                        all_plot_files.append(plot_file)
                        
                        # Add individual download button
                        with open(plot_file, "rb") as file:
                            st.download_button(
                                label=f"Download {district} Plot",
                                data=file,
                                file_name=f"{district}.png",
                                mime="image/png"
                            )
                    
                    # Add region ZIP download
                    region_zip = analyzer.create_zip_for_region(region_files, region)
                    st.download_button(
                        label=f"Download All {region} Plots (ZIP)",
                        data=region_zip,
                        file_name=f"{region}_plots.zip",
                        mime="application/zip"
                    )
                
                # Create and offer master ZIP download
                st.header("Download All Plots")
                master_zip = analyzer.create_master_zip(all_plot_files)
                st.download_button(
                    label="Download All Districts (ZIP)",
                    data=master_zip,
                    file_name="all_district_plots.zip",
                    mime="application/zip"
                )
                
                st.snow()
                st.balloons()
                
            except Exception as e:
                st.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()
