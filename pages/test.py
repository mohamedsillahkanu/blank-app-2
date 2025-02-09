import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

class HealthFacilityProcessor:
    def __init__(self):
        self.df = None
    
    def load_data(self, uploaded_file):
        try:
            self.df = pd.read_csv(uploaded_file)
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
        
        return (active_df['hf_uid'].nunique(), inactive_df['hf_uid'].nunique(), 
                active_df, inactive_df, self.df)
    
    def plot_overall_distribution(self, active_count, inactive_count):
        fig, ax = plt.subplots(figsize=(8, 6))
        
        total = active_count + inactive_count
        active_percentage = (active_count / total) * 100
        inactive_percentage = (inactive_count / total) * 100
        
        # Create stacked bar
        p1 = ax.bar('Total Facilities', active_count, color='#47B5FF', 
                   alpha=0.8, label='Active')
        p2 = ax.bar('Total Facilities', inactive_count, bottom=active_count,
                   color='lightpink', alpha=0.8, label='Inactive')
        
        # Add labels in the middle of each segment
        ax.text(0, active_count/2, f'{active_count}\n({active_percentage:.1f}%)',
                ha='center', va='center')
        ax.text(0, active_count + inactive_count/2, 
                f'{inactive_count}\n({inactive_percentage:.1f}%)',
                ha='center', va='center')
        
        plt.title('Overall Active vs Inactive Health Facilities')
        plt.legend()
        plt.xticks([])
        
        # Save plot to BytesIO object
        img = BytesIO()
        plt.savefig(img, format='png', dpi=300, bbox_inches='tight')
        img.seek(0)
        
        # Display plot
        st.pyplot(fig)
        
        # Add download button for the plot
        st.download_button(
            label="Download Plot as PNG",
            data=img,
            file_name='facility_distribution.png',
            mime='image/png'
        )

def main():
    st.title("Health Facility Distribution Analysis")
    st.write("Upload your CSV file to see the distribution of active vs inactive health facilities.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        processor = HealthFacilityProcessor()
        
        if processor.load_data(uploaded_file):
            with st.spinner("Processing data..."):
                try:
                    active_count, inactive_count, active_df, inactive_df, full_df = processor.process_data()
                    
                    # Display metrics
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Active Facilities", active_count)
                    with col2:
                        st.metric("Inactive Facilities", inactive_count)
                    
                    # Show visualization
                    st.subheader("Overall Distribution")
                    processor.plot_overall_distribution(active_count, inactive_count)
                    
                    # Add Excel file downloads
                    st.subheader("Download Data")
                    
                    def to_excel(df):
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df.to_excel(writer, index=False)
                        output.seek(0)
                        return output
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        excel_active = to_excel(active_df)
                        st.download_button(
                            label="Download Active Facilities",
                            data=excel_active,
                            file_name='active_facilities.xlsx',
                            mime='application/vnd.ms-excel'
                        )
                    
                    with col2:
                        excel_inactive = to_excel(inactive_df)
                        st.download_button(
                            label="Download Inactive Facilities",
                            data=excel_inactive,
                            file_name='inactive_facilities.xlsx',
                            mime='application/vnd.ms-excel'
                        )
                    
                    with col3:
                        excel_full = to_excel(full_df)
                        st.download_button(
                            label="Download Full Dataset",
                            data=excel_full,
                            file_name='full_dataset.xlsx',
                            mime='application/vnd.ms-excel'
                        )
                    
                except Exception as e:
                    st.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()
