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

    def plot_by_adm3_for_each_adm1(self, active_df, inactive_df, selected_adm1):
        """
        Create plot for selected adm1, showing adm3 distributions.
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
        
        # Create figure
        fig, ax = plt.subplots(figsize=(15, max(8, len(adm3_values) * 0.4)))
        
        # Create bars
        y = np.arange(len(adm3_values))
        height = 0.8
        
        # Plot stacked bars
        active_data = [active_counts.get(adm3, 0) for adm3 in adm3_values]
        inactive_data = [inactive_counts.get(adm3, 0) for adm3 in adm3_values]
        
        ax.barh(y, active_data, height, label='Active', color='#47B5FF', alpha=0.8)
        ax.barh(y, inactive_data, height, left=active_data,
                label='Inactive', color='lightpink', alpha=0.8)
        
        # Add combined count and percentage labels
        for i, adm3 in enumerate(adm3_values):
            active_count = active_counts.get(adm3, 0)
            inactive_count = inactive_counts.get(adm3, 0)
            total = active_count + inactive_count
            
            if total > 0:
                active_pct = (active_count / total * 100)
                inactive_pct = (inactive_count / total * 100)
                
                # Add labels with combined count and percentage
                if active_count > 0:
                    ax.text(active_count/2, i, f'{active_count:,}',
                            ha='center', va='center')
                if inactive_count > 0:
                    ax.text(active_count + inactive_count/2, i,
                            f'{inactive_count:,}',
                            ha='center', va='center')
        
        plt.title(f'Health Facility Distribution in {selected_adm1} by District', fontsize=14, pad=20)
        plt.xlabel('Number of Health Facilities', fontsize=12, labelpad=10)
        plt.ylabel('District', fontsize=12, labelpad=10)
        plt.yticks(y, adm3_values)
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
                
                # Add district-level analysis section
                st.header("District-Level Distribution")
                
                # Get unique regions
                regions = sorted(processor.df['adm1'].unique())
                
                # Create region selector
                selected_region = st.selectbox(
                    "Select a region to view district-level distribution:",
                    regions
                )
                
                # Show district distribution for selected region
                st.subheader(f"Facility Distribution in {selected_region} by District")
                fig_district = processor.plot_by_adm3_for_each_adm1(active_df, inactive_df, selected_region)
                
                if fig_district is not None:
                    st.pyplot(fig_district)
                    
                    # Add download button for district visualization
                    district_bytes = save_fig_to_bytes(fig_district)
                    st.download_button(
                        label=f"Download {selected_region} District Distribution",
                        data=district_bytes,
                        file_name=f"facility_distribution_{selected_region.replace(' ', '_')}.png",
                        mime="image/png"
                    )
                else:
                    st.warning(f"No district-level data available for {selected_region}")

                st.snow()
                st.balloons()
                
            except Exception as e:
                st.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()
