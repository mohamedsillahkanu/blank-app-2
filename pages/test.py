import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from io import StringIO

# GitHub raw file URL
GITHUB_DATA_URL = "https://raw.githubusercontent.com/mohamedsillahkanu/blank-app-2/1d6f2568e2e9630ed33f7e320e2751ab475cb35f/key_variables%20(2).csv"

class HealthFacilityReportingProcessor:
    def __init__(self, df):
        """
        Initializes the processor with a DataFrame
        """
        self.df = df

    def calculate_report(self):
        """
        Calculate the 'report' column for all active health facilities.
        """
        self.df['report'] = (self.df[['allout', 'susp', 'test', 'conf', 'maltreat']] > 0).sum(axis=1, min_count=1)

    def ensure_numeric_conf(self):
        """
        Ensure the 'conf' column is numeric.
        """
        self.df['conf'] = pd.to_numeric(self.df['conf'], errors='raise')

    def calculate_report_conf(self):
        """
        Determine if confirmed cases were reported.
        """
        self.df['report_conf'] = np.where(self.df['conf'] > 0, 1, 0)

    def create_date_column(self):
        """
        Create a 'date' column in the format YYYY-MM and ensure it's datetime.
        """
        self.df['month'] = self.df['month'].astype(int).astype(str).str.zfill(2)
        self.df['year'] = self.df['year'].astype(int).astype(str)
        self.df['date'] = pd.to_datetime(self.df['year'] + '-' + self.df['month'], format='%Y-%m')

    def calculate_first_month_reported(self):
        """
        Calculate the first month each health facility reported (report > 0).
        """
        report_positive = self.df[self.df['report'] > 0]
        first_months = report_positive.groupby('hf_uid')['date'].min()
        self.df['First_month_hf_reported'] = self.df['hf_uid'].map(first_months)

    def add_expected_reporting_column(self):
        """
        Add a column 'hf_expected_to_report_month' based on the condition.
        """
        self.df['hf_expected_to_report_month'] = np.where(
            self.df['date'] >= self.df['First_month_hf_reported'], 1, 0
        )

    def add_monthly_reporting_rate(self):
        """
        Add a column 'monthly_reporting_rate'.
        """
        self.df['monthly_reporting_rate'] = np.where(
            self.df['hf_expected_to_report_month'] > 0,
            (self.df['report_conf'] / self.df['hf_expected_to_report_month']) * 100,
            0
        )

    def split_active_inactive(self):
        """
        Split the DataFrame into active and inactive health facilities.
        """
        active_df = self.df[self.df['First_month_hf_reported'].notna()].copy()
        inactive_df = self.df[self.df['First_month_hf_reported'].isna()].copy()

        column_order = ['adm1', 'adm2', 'adm3'] + [col for col in active_df.columns if col not in ['adm1', 'adm2', 'adm3']]
        active_df = active_df[column_order]
        inactive_df = inactive_df[column_order]

        unique_active_hfs = active_df['hf_uid'].nunique()
        unique_inactive_hfs = inactive_df['hf_uid'].nunique()

        return active_df, inactive_df, unique_active_hfs, unique_inactive_hfs

    def plot_counts_by_adm1(self, active_df, inactive_df):
        """
        Create a horizontal stacked bar chart showing facility counts by region.
        """
        fig, ax = plt.subplots(figsize=(12, 10))
        
        adm1_values = sorted(self.df['adm1'].unique())
        active_counts = active_df.groupby('adm1')['hf_uid'].nunique()
        inactive_counts = inactive_df.groupby('adm1')['hf_uid'].nunique()

        y = np.arange(len(adm1_values))
        height = 0.8

        ax.barh(y, [active_counts.get(adm1, 0) for adm1 in adm1_values],
               height, label='Active', color='#47B5FF', alpha=0.8)
        ax.barh(y, [inactive_counts.get(adm1, 0) for adm1 in adm1_values],
               height, left=[active_counts.get(adm1, 0) for adm1 in adm1_values],
               label='Inactive', color='lightpink', alpha=0.8)

        for i, adm1 in enumerate(adm1_values):
            active_count = active_counts.get(adm1, 0)
            inactive_count = inactive_counts.get(adm1, 0)

            if active_count > 0:
                ax.text(active_count/2, i, f'{active_count}',
                       ha='center', va='center')
            if inactive_count > 0:
                ax.text(active_count + inactive_count/2, i,
                       f'{inactive_count}',
                       ha='center', va='center')

        ax.set_title('Health Facility Counts by Region', fontsize=14, pad=20)
        ax.set_xlabel('Number of Health Facilities', fontsize=12, labelpad=10)
        ax.set_ylabel('Region', fontsize=12, labelpad=10)
        ax.set_yticks(y)
        ax.set_yticklabels(adm1_values)
        ax.legend()

        plt.tight_layout()
        return fig

    def plot_percentages_by_adm1(self, active_df, inactive_df):
        """
        Create a horizontal stacked bar chart showing facility percentages by region.
        """
        fig, ax = plt.subplots(figsize=(12, 10))
        
        adm1_values = sorted(self.df['adm1'].unique())
        active_counts = active_df.groupby('adm1')['hf_uid'].nunique()
        inactive_counts = inactive_df.groupby('adm1')['hf_uid'].nunique()

        y = np.arange(len(adm1_values))
        height = 0.8

        for i, adm1 in enumerate(adm1_values):
            active_count = active_counts.get(adm1, 0)
            inactive_count = inactive_counts.get(adm1, 0)
            total = active_count + inactive_count

            if total > 0:
                active_pct = (active_count / total * 100)
                inactive_pct = (inactive_count / total * 100)

                ax.barh(i, active_pct, height, label='Active' if i == 0 else "",
                       color='#47B5FF', alpha=0.8)
                ax.barh(i, inactive_pct, height, left=active_pct,
                       label='Inactive' if i == 0 else "", color='lightpink', alpha=0.8)

                if active_pct > 0:
                    ax.text(active_pct/2, i, f'{active_pct:.1f}%',
                          ha='center', va='center')
                if inactive_pct > 0:
                    ax.text(active_pct + inactive_pct/2, i, f'{inactive_pct:.1f}%',
                          ha='center', va='center')

        ax.set_title('Health Facility Distribution by Region (%)', fontsize=14, pad=20)
        ax.set_xlabel('Percentage of Health Facilities', fontsize=12, labelpad=10)
        ax.set_ylabel('Region', fontsize=12, labelpad=10)
        ax.set_yticks(y)
        ax.set_yticklabels(adm1_values)
        ax.set_xlim(0, 100)
        ax.legend()

        plt.tight_layout()
        return fig

    def plot_overall_bar(self, active_count, inactive_count):
        """
        Plot overall vertical stacked bar chart for active and inactive health facilities.
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        total = active_count + inactive_count
        active_percentage = (active_count / total) * 100
        inactive_percentage = (inactive_count / total) * 100

        ax.bar('Total Facilities', active_count, color='#47B5FF', alpha=0.8, label='Active')
        ax.bar('Total Facilities', inactive_count, bottom=active_count,
               color='lightpink', alpha=0.8, label='Inactive')

        ax.text(0, active_count/2, f'{active_count}\n({active_percentage:.1f}%)',
               ha='center', va='center')
        ax.text(0, active_count + inactive_count/2, f'{inactive_count}\n({inactive_percentage:.1f}%)',
               ha='center', va='center')

        ax.set_title('Overall Active vs Inactive Health Facilities')
        ax.legend()
        ax.set_xticks([])

        plt.tight_layout()
        return fig

    def plot_by_adm3_for_each_adm1(self, active_df, inactive_df, selected_adm1):
        """
        Create plots for adm3 distributions within selected adm1.
        """
        # Filter data for this adm1
        active_adm1 = active_df[active_df['adm1'] == selected_adm1]
        inactive_adm1 = inactive_df[inactive_df['adm1'] == selected_adm1]

        # Get adm3 values for this adm1
        adm3_values = sorted(set(active_adm1['adm3'].unique()) | set(inactive_adm1['adm3'].unique()))

        if not adm3_values:
            return None

        # Calculate counts for each adm3
        active_counts = active_adm1.groupby('adm3')['hf_uid'].nunique()
        inactive_counts = inactive_adm1.groupby('adm3')['hf_uid'].nunique()

        fig, ax = plt.subplots(figsize=(15, max(8, len(adm3_values) * 0.4)))

        y = np.arange(len(adm3_values))
        height = 0.8

        active_data = [active_counts.get(adm3, 0) for adm3 in adm3_values]
        inactive_data = [inactive_counts.get(adm3, 0) for adm3 in adm3_values]

        ax.barh(y, active_data, height, label='Active', color='#47B5FF', alpha=0.8)
        ax.barh(y, inactive_data, height, left=active_data,
               label='Inactive', color='lightpink', alpha=0.8)

        for i, adm3 in enumerate(adm3_values):
            active_count = active_counts.get(adm3, 0)
            inactive_count = inactive_counts.get(adm3, 0)

            if active_count > 0:
                ax.text(active_count/2, i, f'{active_count:,}',
                       ha='center', va='center')
            if inactive_count > 0:
                ax.text(active_count + inactive_count/2, i,
                       f'{inactive_count:,}',
                       ha='center', va='center')

        ax.set_title(f'Health Facility Distribution in {selected_adm1} by District', fontsize=14, pad=20)
        ax.set_xlabel('Number of Health Facilities', fontsize=12, labelpad=10)
        ax.set_ylabel('District', fontsize=12, labelpad=10)
        ax.set_yticks(y)
        ax.set_yticklabels(adm3_values)
        ax.legend()

        plt.tight_layout()
        return fig

    def process(self):
        """
        Execute the entire processing pipeline.
        """
        self.calculate_report()
        self.ensure_numeric_conf()
        self.calculate_report_conf()
        self.create_date_column()
        self.calculate_first_month_reported()
        self.add_expected_reporting_column()
        self.add_monthly_reporting_rate()


def load_data():
    """
    Load data from local file
    """
    try:
        df = pd.read_csv('key_variables.csv')
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None


def main():
    st.set_page_config(page_title="Health Facility Reporting Analysis", layout="wide")
    
    st.title("Health Facility Reporting Analysis")
    st.markdown("""
    This application analyzes health facility reporting data and provides visualizations 
    for active and inactive facilities across different administrative levels.
    """)
    
    # Load data
    with st.spinner('Loading data...'):
        df = load_data()
    
    if df is not None:
        try:
            # Initialize processor
            processor = HealthFacilityReportingProcessor(df)
            
            # Process data
            processor.process()
            
            # Split data and get counts
            active_df, inactive_df, unique_active_hfs, unique_inactive_hfs = processor.split_active_inactive()
            
            # Display summary statistics
            st.header("Summary Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Active Health Facilities", unique_active_hfs)
            with col2:
                st.metric("Inactive Health Facilities", unique_inactive_hfs)
            
            # Create tabs for different visualizations
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "Overall Distribution",
                "Regional Counts",
                "Regional Percentages",
                "District-level Analysis",
                "Download Data"
            ])
            
            with tab1:
                st.subheader("Overall Distribution of Health Facilities")
                fig = processor.plot_overall_bar(unique_active_hfs, unique_inactive_hfs)
                st.pyplot(fig)
            
            with tab2:
                st.subheader("Health Facility Counts by Region")
                fig = processor.plot_counts_by_adm1(active_df, inactive_df)
                st.pyplot(fig)
            
            with tab3:
                st.subheader("Health Facility Distribution by Region (%)")
                fig = processor.plot_percentages_by_adm1(active_df, inactive_df)
                st.pyplot(fig)
            
            with tab4:
                st.subheader("District-level Analysis")
                selected_adm1 = st.selectbox(
                    "Select a region to view district-level distribution:",
                    sorted(df['adm1'].unique())
                )
                if selected_adm1:
                    fig = processor.plot_by_adm3_for_each_adm1(active_df, inactive_df, selected_adm1)
                    if fig:
                        st.pyplot(fig)
                    else:
                        st.warning(f"No district-level data available for {selected_adm1}")
            
            with tab5:
                st.subheader("Download Processed Data")
                
                # Create download buttons for each dataset
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Download active facilities data
                    csv_active = active_df.to_csv(index=False)
                    st.download_button(
                        label="Download Active Facilities Data",
                        data=csv_active,
                        file_name="active_facilities.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    # Download inactive facilities data
                    csv_inactive = inactive_df.to_csv(index=False)
                    st.download_button(
                        label="Download Inactive Facilities Data",
                        data=csv_inactive,
                        file_name="inactive_facilities.csv",
                        mime="text/csv"
                    )
                
                with col3:
                    # Download full processed data
                    csv_full = processor.df.to_csv(index=False)
                    st.download_button(
                        label="Download Full Dataset",
                        data=csv_full,
                        file_name="full_processed_data.csv",
                        mime="text/csv"
                    )
                
                # Add explanation of the datasets
                st.markdown("""
                ### Dataset Descriptions:
                
                1. **Active Facilities Data**: Contains information about health facilities that have reported at least once
                2. **Inactive Facilities Data**: Contains information about health facilities that have never reported
                3. **Full Dataset**: Contains all processed data including both active and inactive facilities
                
                Each dataset includes the following key columns:
                - Administrative regions (adm1, adm2, adm3)
                - Health facility unique identifier (hf_uid)
                - Reporting dates and status
                - Reporting rates and metrics
                """)

        except Exception as e:
            st.error(f"An error occurred while processing the data: {str(e)}")
            st.exception(e)


if __name__ == "__main__":
    main()
