import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class HealthFacilityProcessor:
    def __init__(self):
        self.df = None
    
    def load_data(self):
        try:
            self.df = pd.read_csv("key_variables (2).csv")
            st.success("Data successfully loaded!")
            return True
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return False
    
    def process_data(self):
        # Calculate report column
        self.df['report'] = (self.df[['allout', 'susp', 'test', 'conf', 'maltreat']] > 0).sum(axis=1, min_count=1)
        
        # Create date column and calculate first month reported
        self.df['month'] = self.df['month'].astype(int).astype(str).str.zfill(2)
        self.df['year'] = self.df['year'].astype(int).astype(str)
        self.df['date'] = pd.to_datetime(self.df['year'] + '-' + self.df['month'], format='%Y-%m')
        
        # Calculate first month reported
        report_positive = self.df[self.df['report'] > 0]
        first_months = report_positive.groupby('hf_uid')['date'].min()
        self.df['First_month_hf_reported'] = self.df['hf_uid'].map(first_months)
        
        # Split active and inactive
        active_df = self.df[self.df['First_month_hf_reported'].notna()]
        inactive_df = self.df[self.df['First_month_hf_reported'].isna()]
        
        return active_df, inactive_df

    def plot_counts_by_adm1(self, active_df, inactive_df):
        """
        Create a horizontal stacked bar chart showing facility counts by region.
        """
        # Get unique adm1 values and sort them
        adm1_values = sorted(self.df['adm1'].unique())

        # Calculate counts for each region
        active_counts = active_df.groupby('adm1')['hf_uid'].nunique()
        inactive_counts = inactive_df.groupby('adm1')['hf_uid'].nunique()

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))

        # Create bars
        y = np.arange(len(adm1_values))
        height = 0.8

        # Plot stacked bars
        active_bars = ax.barh(y, [active_counts.get(adm1, 0) for adm1 in adm1_values],
                             height, label='Active', color='#47B5FF', alpha=0.8)
        inactive_bars = ax.barh(y, [inactive_counts.get(adm1, 0) for adm1 in adm1_values],
                               height, left=[active_counts.get(adm1, 0) for adm1 in adm1_values],
                               label='Inactive', color='lightpink', alpha=0.8)

        # Add count labels
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

        plt.title('Health Facility Counts by Region', fontsize=14, pad=20)
        plt.xlabel('Number of Health Facilities', fontsize=12, labelpad=10)
        plt.ylabel('Region', fontsize=12, labelpad=10)
        plt.yticks(y, adm1_values)
        plt.legend()

        plt.tight_layout()
        return fig

    def plot_percentages_by_adm1(self, active_df, inactive_df):
        """
        Create a horizontal stacked bar chart showing facility percentages by region.
        """
        # Get unique adm1 values and sort them
        adm1_values = sorted(self.df['adm1'].unique())
        
        # Calculate counts and percentages
        active_counts = active_df.groupby('adm1')['hf_uid'].nunique()
        inactive_counts = inactive_df.groupby('adm1')['hf_uid'].nunique()

        fig, ax = plt.subplots(figsize=(12, 10))
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

        plt.title('Health Facility Distribution by Region (%)', fontsize=14, pad=20)
        plt.xlabel('Percentage of Health Facilities', fontsize=12, labelpad=10)
        plt.ylabel('Region', fontsize=12, labelpad=10)
        plt.yticks(y, adm1_values)
        plt.xlim(0, 100)
        plt.legend()

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
    st.title("Health Facility Regional Distribution Analysis")
    st.snow()
    st.balloons()
    
    processor = HealthFacilityProcessor()
    
    if processor.load_data():
        with st.spinner("Processing data..."):
            try:
                active_df, inactive_df = processor.process_data()
                
                # Show count visualization
                st.subheader("Facility Counts by Region")
                fig_counts = processor.plot_counts_by_adm1(active_df, inactive_df)
                st.pyplot(fig_counts)
                
                # Add download button for counts visualization
                counts_bytes = save_fig_to_bytes(fig_counts)
                st.download_button(
                    label="Download Counts Visualization",
                    data=counts_bytes,
                    file_name="facility_counts.png",
                    mime="image/png"
                )
                
                # Show percentage visualization
                st.subheader("Facility Distribution by Region (%)")
                fig_percentages = processor.plot_percentages_by_adm1(active_df, inactive_df)
                st.pyplot(fig_percentages)
                
                # Add download button for percentages visualization
                percentages_bytes = save_fig_to_bytes(fig_percentages)
                st.download_button(
                    label="Download Percentages Visualization",
                    data=percentages_bytes,
                    file_name="facility_percentages.png",
                    mime="image/png"
                )
                
                st.snow()
                st.balloons()
                
            except Exception as e:
                st.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()
