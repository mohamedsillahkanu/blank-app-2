import streamlit as st
import pandas as pd
import plotly.express as px
import io

def process_health_facility_data(df):
    # Get all unique names from both columns
    all_unique_names = pd.DataFrame({
        'Health_Facility_Name': pd.unique(
            pd.concat([
                df['HF_Name_in_DHIS2'].dropna(),
                df['New_HF_Name_in_MFL'].dropna()
            ])
        )
    })
    
    # Classify each facility
    all_unique_names['Classification'] = all_unique_names['Health_Facility_Name'].apply(
        lambda x: (
            "HF in both DHIS2 and MFL" if (x in df['HF_Name_in_DHIS2'].values and x in df['New_HF_Name_in_MFL'].values)
            else "HF in MFL and not in DHIS2" if (x in df['New_HF_Name_in_MFL'].values and x not in df['HF_Name_in_DHIS2'].values)
            else "HF in DHIS2 and not in MFL" if (x in df['HF_Name_in_DHIS2'].values and x not in df['New_HF_Name_in_MFL'].values)
            else "Unclassified"
        )
    )
    
    # Create summary table
    summary_table = (
        all_unique_names.groupby('Classification')
        .size()
        .reset_index(name='Count')
    )
    summary_table['Percentage'] = round((summary_table['Count'] / summary_table['Count'].sum()) * 100, 2)
    
    return all_unique_names, summary_table

def main():
    st.title("Health Facility Data Analysis")
    
    # File upload
    uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx'])
    
    if uploaded_file is not None:
        # Read the uploaded file
        df = pd.read_excel(uploaded_file)
        
        # Process the data
        classified_results, summary_table = process_health_facility_data(df)
        
        # Display results
        st.header("Analysis Results")
        
        # Display summary table
        st.subheader("Summary Statistics")
        st.dataframe(summary_table)
        
        # Create and display count plot
        count_fig = px.bar(
            summary_table,
            x='Classification',
            y='Count',
            color='Classification',
            title='Summary of matching outcomes (Count)',
            color_discrete_map={
                "HF in both DHIS2 and MFL": "#6a9955",
                "HF in MFL and not in DHIS2": "#b55d5d",
                "HF in DHIS2 and not in MFL": "#5d89b5",
                "Unclassified": "gray"
            }
        )
        st.plotly_chart(count_fig)
        
        # Create and display percentage plot
        percentage_fig = px.bar(
            summary_table,
            x='Classification',
            y='Percentage',
            color='Classification',
            title='Summary of matching outcomes (Percentage)',
            color_discrete_map={
                "HF in both DHIS2 and MFL": "#6a9955",
                "HF in MFL and not in DHIS2": "#b55d5d",
                "HF in DHIS2 and not in MFL": "#5d89b5",
                "Unclassified": "gray"
            }
        )
        st.plotly_chart(percentage_fig)
        
        # Download buttons for results
        st.header("Download Results")
        
        # Convert DataFrames to Excel
        classified_buffer = io.BytesIO()
        summary_buffer = io.BytesIO()
        
        with pd.ExcelWriter(classified_buffer, engine='openpyxl') as writer:
            classified_results.to_excel(writer, index=False)
        
        with pd.ExcelWriter(summary_buffer, engine='openpyxl') as writer:
            summary_table.to_excel(writer, index=False)
            
        st.download_button(
            label="Download Classified Results",
            data=classified_buffer.getvalue(),
            file_name="health_facility_classification_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.download_button(
            label="Download Summary Results",
            data=summary_buffer.getvalue(),
            file_name="health_facility_summary_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
