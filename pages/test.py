import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

class HealthFacilityReportingProcessor:
    def __init__(self):
        """
        Initializes the processor with placeholder for DataFrame
        """
        self.df = None

    def load_data(self, uploaded_file):
        """
        Load the CSV data from Streamlit's uploaded file.
        """
        try:
            self.df = pd.read_csv(uploaded_file)
            st.success("Data successfully loaded!")
            return True
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return False

    def calculate_report(self):
        """
        Calculate the 'report' column for all active health facilities.
        """
        self.df['report'] = (self.df[['allout', 'susp', 'test', 'conf', 'maltreat']] > 0).sum(axis=1, min_count=1)

    def ensure_numeric_conf(self):
        """
        Ensure the 'conf' column is numeric.
        """
        try:
            self.df['conf'] = pd.to_numeric(self.df['conf'], errors='raise')
            return True
        except Exception as e:
            st.error(f"Error converting 'conf' column to numeric: {str(e)}")
            return False

    def calculate_report_conf(self):
        """
        Determine if confirmed cases were reported.
        """
        self.df['report_conf'] = np.where(self.df['conf'] > 0, 1, 0)

    def create_date_column(self):
        """
        Create a 'date' column in the format YYYY-MM and ensure it's datetime.
        """
        try:
            self.df['month'] = self.df['month'].astype(int).astype(str).str.zfill(2)
            self.df['year'] = self.df['year'].astype(int).astype(str)
            self.df['date'] = pd.to_datetime(self.df['year'] + '-' + self.df['month'], format='%Y-%m')
            return True
        except Exception as e:
            st.error(f"Error creating date column: {str(e)}")
            return False

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

        column_order = ['adm1', 'adm2', 'adm3'] + [col for col in active_df.columns 
                                                  if col not in ['adm1', 'adm2', 'adm3']]
        active_df = active_df[column_order]
        inactive_df = inactive_df[column_order]

        unique_active_hfs = active_df['hf_uid'].nunique()
        unique_inactive_hfs = inactive_df['hf_uid'].nunique()

        return active_df, inactive_df, unique_active_hfs, unique_inactive_hfs

    def plot_overall_bar(self, active_count, inactive_count):
        """
        Plot overall vertical stacked bar chart using Streamlit.
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        
        total = active_count + inactive_count
        active_percentage = (active_count / total) * 100
        inactive_percentage = (inactive_count / total) * 100
        
        p1 = ax.bar('Total Facilities', active_count, color='#47B5FF', alpha=0.8, label='Active')
        p2 = ax.bar('Total Facilities', inactive_count, bottom=active_count,
                    color='lightpink', alpha=0.8, label='Inactive')
        
        ax.text(0, active_count/2, f'{active_count}\n({active_percentage:.1f}%)',
                ha='center', va='center')
        ax.text(0, active_count + inactive_count/2, f'{inactive_count}\n({inactive_percentage:.1f}%)',
                ha='center', va='center')
        
        plt.title('Overall Active vs Inactive Health Facilities')
        plt.legend()
        plt.xticks([])
        
        st.pyplot(fig)

    def plot_by_region(self, active_df, inactive_df):
        """
        Plot facilities by region using Streamlit.
        """
        # Count facilities by adm1
        active_by_adm1 = active_df['hf_uid'].groupby(active_df['adm1']).nunique()
        inactive_by_adm1 = inactive_df['hf_uid'].groupby(inactive_df['adm1']).nunique()

        # Create DataFrame for plotting
        plot_df = pd.DataFrame({
            'Active': active_by_adm1,
            'Inactive': inactive_by_adm1
        }).fillna(0)

        # Calculate percentages
        total = plot_df.sum(axis=1)
        plot_df_pct = plot_df.div(total, axis=0) * 100

        # Create two columns for the plots
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Counts by Region")
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            plot_df.plot(kind='bar', ax=ax1)
            plt.title('Health Facilities by Region')
            plt.xlabel('Region')
            plt.ylabel('Number of Facilities')
            plt.xticks(rotation=45)
            plt.legend(title='Status')
            st.pyplot(fig1)

        with col2:
            st.subheader("Percentages by Region")
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            plot_df_pct.plot(kind='bar', stacked=True, ax=ax2)
            plt.title('Health Facilities Distribution by Region')
            plt.xlabel('Region')
            plt.ylabel('Percentage')
            plt.xticks(rotation=45)
            plt.legend(title='Status')
            st.pyplot(fig2)

def main():
    st.title("Health Facility Reporting Analysis")
    st.write("Upload your CSV file to analyze health facility reporting patterns.")

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        # Initialize processor
        processor = HealthFacilityReportingProcessor()

        # Process data
        with st.spinner("Processing data..."):
            if processor.load_data(uploaded_file):
                processor.calculate_report()
                if processor.ensure_numeric_conf():
                    processor.calculate_report_conf()
                    if processor.create_date_column():
                        processor.calculate_first_month_reported()
                        processor.add_expected_reporting_column()
                        processor.add_monthly_reporting_rate()

                        # Split data and get counts
                        active_df, inactive_df, unique_active_hfs, unique_inactive_hfs = processor.split_active_inactive()

                        # Display summary statistics
                        st.header("Summary Statistics")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Active Facilities", unique_active_hfs)
                        with col2:
                            st.metric("Inactive Facilities", unique_inactive_hfs)

                        # Show visualizations
                        st.header("Visualizations")
                        
                        # Overall distribution
                        st.subheader("Overall Distribution")
                        processor.plot_overall_bar(unique_active_hfs, unique_inactive_hfs)

                        # Regional distribution
                        st.subheader("Regional Distribution")
                        processor.plot_by_region(active_df, inactive_df)

                        # Download processed data
                        st.header("Download Processed Data")
                        
                        def to_excel(df):
                            output = BytesIO()
                            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                df.to_excel(writer, index=False)
                            return output.getvalue()

                        col1, col2 = st.columns(2)
                        with col1:
                            excel_active = to_excel(active_df)
                            st.download_button(
                                label="Download Active Facilities Data",
                                data=excel_active,
                                file_name='active_facilities.xlsx',
                                mime='application/vnd.ms-excel'
                            )
                        
                        with col2:
                            excel_inactive = to_excel(inactive_df)
                            st.download_button(
                                label="Download Inactive Facilities Data",
                                data=excel_inactive,
                                file_name='inactive_facilities.xlsx',
                                mime='application/vnd.ms-excel'
                            )

if __name__ == "__main__":
    main()
