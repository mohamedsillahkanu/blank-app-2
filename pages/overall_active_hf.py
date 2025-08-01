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

        # Create date column
        self.df['month'] = self.df['month'].astype(int).astype(str).str.zfill(2)
        self.df['year'] = self.df['year'].astype(int).astype(str)
        self.df['date'] = pd.to_datetime(self.df['year'] + '-' + self.df['month'], format='%Y-%m')

        # Determine first month reported per facility
        report_positive = self.df[self.df['report'] > 0]
        first_months = report_positive.groupby('hf_uid')['date'].min()
        self.df['First_month_hf_reported'] = self.df['hf_uid'].map(first_months)

        # Split active and inactive
        active_df = self.df[self.df['First_month_hf_reported'].notna()]
        inactive_df = self.df[self.df['First_month_hf_reported'].isna()]

        return active_df, inactive_df

    def plot_overall_counts(self, active_count, inactive_count):
        fig, ax = plt.subplots(figsize=(6, 4))
        labels = ['Active', 'Inactive']
        values = [active_count, inactive_count]
        colors = ['#47B5FF', 'lightpink']

        ax.barh(labels, values, color=colors, alpha=0.8)
        for i, v in enumerate(values):
            ax.text(v + 1, i, f'{v}', va='center', fontsize=10)

        ax.set_title('Overall Facility Counts')
        ax.set_xlabel('Number of Facilities')
        plt.tight_layout()
        return fig

    def plot_overall_percentages(self, active_pct, inactive_pct):
        fig, ax = plt.subplots(figsize=(6, 4))
        labels = ['Active', 'Inactive']
        values = [active_pct, inactive_pct]
        colors = ['#47B5FF', 'lightpink']

        ax.barh(labels, values, color=colors, alpha=0.8)
        for i, v in enumerate(values):
            ax.text(v / 2, i, f'{v:.1f}%', ha='center', va='center', fontsize=10, color='black')

        ax.set_title('Overall Facility Distribution (%)')
        ax.set_xlabel('Percentage')
        ax.set_xlim(0, 100)
        plt.tight_layout()
        return fig

def save_fig_to_bytes(fig):
    from io import BytesIO
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    buf.seek(0)
    return buf

def main():
    st.title("Health Facility Overview – Overall Summary")
    processor = HealthFacilityProcessor()

    if processor.load_data():
        with st.spinner("Processing data..."):
            try:
                active_df, inactive_df = processor.process_data()

                # Overall summary
                total_hfs = processor.df['hf_uid'].nunique()
                active_hfs = active_df['hf_uid'].nunique()
                inactive_hfs = inactive_df['hf_uid'].nunique()

                active_pct = active_hfs / total_hfs * 100 if total_hfs > 0 else 0
                inactive_pct = inactive_hfs / total_hfs * 100 if total_hfs > 0 else 0

                st.subheader("Summary Metrics")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Facilities", f"{total_hfs}")
                col2.metric("Active Facilities", f"{active_hfs} ({active_pct:.1f}%)")
                col3.metric("Inactive Facilities", f"{inactive_hfs} ({inactive_pct:.1f}%)")

                # Plot 1: Overall Counts
                st.subheader("Overall Facility Count")
                fig_counts = processor.plot_overall_counts(active_hfs, inactive_hfs)
                st.pyplot(fig_counts)
                st.download_button("Download Overall Count Plot", save_fig_to_bytes(fig_counts),
                                   file_name="overall_counts.png", mime="image/png")

                # Plot 2: Overall Percentages
                st.subheader("Overall Facility Distribution (%)")
                fig_percentages = processor.plot_overall_percentages(active_pct, inactive_pct)
                st.pyplot(fig_percentages)
                st.download_button("Download Overall Percentage Plot", save_fig_to_bytes(fig_percentages),
                                   file_name="overall_percentages.png", mime="image/png")

            except Exception as e:
                st.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()
