import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import zipfile
import io
import os
import tempfile

class HealthFacilityReportingProcessor:
    def __init__(self):
        self.df = None
        self.grouped = None
        self.temp_dir = tempfile.mkdtemp()

    def load_data(self):
        try:
            self.df = pd.read_excel("active_health_facilities.xlsx")
            st.success("Data successfully loaded!")
            return True
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return False

    def calculate_reporting_rate(self):
        self.grouped = (
            self.df.groupby(['adm1', 'adm3', 'date'])
            .agg(
                report_conf_sum=('report_conf', 'sum'),
                hf_expected_sum=('hf_expected_to_report_month', 'sum')
            )
            .reset_index()
        )

        self.grouped['reporting_rate'] = (
            self.grouped['report_conf_sum'].div(self.grouped['hf_expected_sum']) * 100
        ).round(2)

    def pivot_heatmap_data(self, data):
        heatmap_data = data.pivot(index='adm3', columns='date', values='reporting_rate')
        heatmap_data.columns = heatmap_data.columns.strftime('%Y-%m')
        heatmap_data['average_reporting_rate'] = heatmap_data.mean(axis=1, skipna=True)
        heatmap_data = heatmap_data.sort_values(by='average_reporting_rate', ascending=False)
        return heatmap_data.drop(columns=['average_reporting_rate'])

    def plot_overall_heatmap(self):
        overall_data = self.grouped.groupby(['adm3', 'date'])['reporting_rate'].mean().reset_index()
        heatmap_data = self.pivot_heatmap_data(overall_data)

        fig, ax = plt.subplots(figsize=(16, 10))
        sns.heatmap(
            data=heatmap_data,
            annot=False,
            fmt=".1f",
            cmap="viridis",
            linewidths=0,
            cbar_kws={'label': 'Reporting Rate (%)'},
            yticklabels=False
        )
        plt.title('Overall Monthly Reporting Rate by District', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('District', fontsize=12)
        plt.xticks(rotation=90, ha='right')
        plt.tight_layout()
        
        # Save to temp directory
        filepath = os.path.join(self.temp_dir, "overall_reporting_rate.png")
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        return fig

    def plot_subplots_by_adm1(self):
        adm1_groups = sorted(self.grouped['adm1'].unique())
        total_adm1 = len(adm1_groups)

        rows = (total_adm1 - 1) // 4 + 1
        fig, axes = plt.subplots(nrows=rows, ncols=4, figsize=(20, rows * 5), constrained_layout=True)
        axes = axes.flatten()

        for idx, adm1 in enumerate(adm1_groups):
            adm1_data = self.grouped[self.grouped['adm1'] == adm1]
            heatmap_data = self.pivot_heatmap_data(adm1_data)

            sns.heatmap(
                data=heatmap_data,
                annot=False,
                fmt=".1f",
                cmap="viridis",
                linewidths=0,
                ax=axes[idx],
                cbar_kws={'label': 'Reporting Rate (%)'},
                yticklabels=False
            )
            axes[idx].set_title(f'{adm1}', fontsize=14, fontweight='bold')
            axes[idx].set_xlabel('Date', fontsize=10)
            axes[idx].set_ylabel('District', fontsize=10)
            axes[idx].tick_params(axis='x', rotation=90)

        for ax in axes[len(adm1_groups):]:
            ax.axis('off')

        plt.suptitle('Monthly Reporting Rate by District (Grouped by Region)', fontsize=16, fontweight='bold')
        
        # Save to temp directory
        filepath = os.path.join(self.temp_dir, "regional_reporting_rates.png")
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        return fig

    def plot_all_individual_heatmaps(self):
        figures = []
        adm1_groups = sorted(self.grouped['adm1'].unique())

        for adm1 in adm1_groups:
            adm1_data = self.grouped[self.grouped['adm1'] == adm1]
            heatmap_data = self.pivot_heatmap_data(adm1_data)

            fig, ax = plt.subplots(figsize=(16, 10))
            sns.heatmap(
                data=heatmap_data,
                annot=False,
                fmt=".1f",
                cmap="viridis",
                linewidths=0,
                cbar_kws={'label': 'Reporting Rate (%)'},
                yticklabels=True
            )
            plt.title(f'Monthly Reporting Rate by District ({adm1})', fontsize=16, fontweight='bold')
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('District', fontsize=12)
            plt.xticks(rotation=90, ha='right')
            plt.tight_layout()
            
            # Save to temp directory
            filepath = os.path.join(self.temp_dir, f"reporting_rate_{adm1.replace(' ', '_')}.png")
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            figures.append((adm1, fig))
        
        return figures

    def create_zip_file(self):
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.basename(file_path)
                    zf.write(file_path, arcname)
        memory_file.seek(0)
        return memory_file

def save_fig_to_bytes(fig):
    from io import BytesIO
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    buf.seek(0)
    return buf

def main():
    st.title("Health Facility Reporting Rate Analysis")
    st.snow()
    st.balloons()
    
    processor = HealthFacilityReportingProcessor()
    
    if processor.load_data():
        with st.spinner("Processing data..."):
            try:
                processor.calculate_reporting_rate()
                
                # Overall Heatmap
                st.header("Overall Reporting Rate Heatmap")
                fig_overall = processor.plot_overall_heatmap()
                st.pyplot(fig_overall)
                
                overall_bytes = save_fig_to_bytes(fig_overall)
                st.download_button(
                    label="Download Overall Heatmap",
                    data=overall_bytes,
                    file_name="overall_reporting_rate.png",
                    mime="image/png"
                )
                
                # Regional Subplots
                st.header("Regional Reporting Rate Heatmaps")
                fig_subplots = processor.plot_subplots_by_adm1()
                st.pyplot(fig_subplots)
                
                subplots_bytes = save_fig_to_bytes(fig_subplots)
                st.download_button(
                    label="Download Regional Heatmaps",
                    data=subplots_bytes,
                    file_name="regional_reporting_rates.png",
                    mime="image/png"
                )
                
                # Individual Region Heatmaps
                st.header("Individual Region Heatmaps")
                individual_figures = processor.plot_all_individual_heatmaps()
                
                for adm1, fig in individual_figures:
                    st.subheader(f"{adm1} Region")
                    st.pyplot(fig)
                    
                    individual_bytes = save_fig_to_bytes(fig)
                    st.download_button(
                        label=f"Download {adm1} Heatmap",
                        data=individual_bytes,
                        file_name=f"reporting_rate_{adm1.replace(' ', '_')}.png",
                        mime="image/png"
                    )
                
                # Create and offer ZIP download
                st.header("Download All Visualizations")
                zip_file = processor.create_zip_file()
                st.download_button(
                    label="Download All Heatmaps (ZIP)",
                    data=zip_file,
                    file_name="all_reporting_rate_heatmaps.zip",
                    mime="application/zip"
                )
                
                st.snow()
                st.balloons()
                
            except Exception as e:
                st.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()
