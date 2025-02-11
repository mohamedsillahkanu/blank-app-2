import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class HealthFacilityReportingProcessor:
    def __init__(self):
        """
        Initializes the processor.
        """
        self.df = None
        self.grouped = None

    def load_data(self):
        """
        Load the data from embedded file.
        """
        try:
            self.df = pd.read_excel("active_health_facilities.xlsx")
            st.success("Data successfully loaded!")
            return True
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return False

    def calculate_reporting_rate(self):
        """
        Group and calculate the reporting rate by adm1, adm3, and date.
        """
        self.grouped = (
            self.df.groupby(['adm1', 'adm3', 'date'])
            .agg(
                report_conf_sum=('report_conf', 'sum'),
                hf_expected_sum=('hf_expected_to_report_month', 'sum')
            )
            .reset_index()
        )

        # Calculate the reporting rate
        self.grouped['reporting_rate'] = (
            self.grouped['report_conf_sum'].div(self.grouped['hf_expected_sum']) * 100
        ).round(2)

    def pivot_heatmap_data(self, data):
        """
        Pivot the data for heatmap plotting.
        """
        heatmap_data = data.pivot(index='adm3', columns='date', values='reporting_rate')

        # Format date columns and sort by average reporting rate
        heatmap_data.columns = heatmap_data.columns.strftime('%Y-%m')
        heatmap_data['average_reporting_rate'] = heatmap_data.mean(axis=1, skipna=True)
        heatmap_data = heatmap_data.sort_values(by='average_reporting_rate', ascending=False)
        return heatmap_data.drop(columns=['average_reporting_rate'])

    def plot_overall_heatmap(self):
        """
        Plot the overall heatmap for reporting rates across all adm3 and dates.
        """
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
        
        return fig

    def plot_subplots_by_adm1(self):
        """
        Plot subplots for each adm1 showing reporting rates by adm3 and date.
        """
        adm1_groups = self.grouped['adm1'].unique()
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

        # Hide unused subplots
        for ax in axes[len(adm1_groups):]:
            ax.axis('off')

        plt.suptitle('Monthly Reporting Rate by District (Grouped by Region)', fontsize=16, fontweight='bold')
        return fig

    def plot_individual_heatmap(self, selected_adm1):
        """
        Generate individual heatmap for selected adm1.
        """
        adm1_data = self.grouped[self.grouped['adm1'] == selected_adm1]
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
        plt.title(f'Monthly Reporting Rate by District ({selected_adm1})', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('District', fontsize=12)
        plt.xticks(rotation=90, ha='right')
        plt.tight_layout()
        
        return fig

def save_fig_to_bytes(fig):
    """Convert a matplotlib figure to bytes for downloading."""
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
                
                # Individual Region Analysis
                st.header("Individual Region Analysis")
                regions = sorted(processor.grouped['adm1'].unique())
                selected_region = st.selectbox(
                    "Select a region to view detailed reporting rates:",
                    regions
                )
                
                fig_individual = processor.plot_individual_heatmap(selected_region)
                st.pyplot(fig_individual)
                
                individual_bytes = save_fig_to_bytes(fig_individual)
                st.download_button(
                    label=f"Download {selected_region} Heatmap",
                    data=individual_bytes,
                    file_name=f"reporting_rate_{selected_region.replace(' ', '_')}.png",
                    mime="image/png"
                )
                
                st.snow()
                st.balloons()
                
            except Exception as e:
                st.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()
