import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

def read_file(uploaded_file):
    """Read different file formats"""
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            return pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format")
            return None
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

def process_health_facility_data(df):
    # Get all unique names from both columns
    all_unique_names = pd.DataFrame({
        'Health_Facility_Name': pd.unique(
            pd.concat([
                df['hf_DHIS2'].dropna(),
                df['New_MFL'].dropna()
            ])
        )
    })
    
    # Classify each facility
    all_unique_names['Classification'] = all_unique_names['Health_Facility_Name'].apply(
        lambda x: (
            "HF in both DHIS2 and MFL" if (x in df['hf_DHIS2'].values and x in df['New_MFL'].values)
            else "HF in MFL and not in DHIS2" if (x in df['New_MFL'].values and x not in df['hf_DHIS2'].values)
            else "HF in DHIS2 and not in MFL" if (x in df['hf_DHIS2'].values and x not in df['New_MFL'].values)
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

def create_pie_chart(summary_table):
    """Create an interactive pie chart"""
    colors = {
        "HF in both DHIS2 and MFL": "#6a9955",
        "HF in MFL and not in DHIS2": "#b55d5d",
        "HF in DHIS2 and not in MFL": "#5d89b5",
        "Unclassified": "gray"
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=summary_table['Classification'],
        values=summary_table['Count'],
        hole=.3,
        marker_colors=[colors[cls] for cls in summary_table['Classification']],
        textinfo='percent+label',
        hovertemplate="<b>%{label}</b><br>" +
                      "Count: %{value}<br>" +
                      "Percentage: %{percent}<br>" +
                      "<extra></extra>"
    )])
    
    fig.update_layout(
        title="Distribution of Health Facilities",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def display_additional_stats(df):
    """Display additional statistics about the matching"""
    st.subheader("Detailed Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        exact_matches = len(df[df['Match_Score'] == 100])
        st.metric("Exact Matches", exact_matches)
        
    with col2:
        high_matches = len(df[(df['Match_Score'] >= 70) & (df['Match_Score'] < 100)])
        st.metric("High Similarity Matches (≥70%)", high_matches)
        
    with col3:
        low_matches = len(df[df['Match_Score'] < 70])
        st.metric("Low Similarity (<70%)", low_matches)

def main():
    st.title("Summary of Matching Outcomes")
    
    # File upload with multiple formats
    uploaded_file = st.file_uploader(
        "Upload the Facility_matching_result file (CSV, Excel)", 
        type=['csv', 'xlsx', 'xls']
    )
    
    if uploaded_file is not None:
        # Read the uploaded file
        df = read_file(uploaded_file)
        
        if df is not None:
            # Display initial counts
            st.header("Initial Data Overview")
            total_records = len(df)
            st.metric("Total Records Processed", total_records)
            
            # Process the data
            classified_results, summary_table = process_health_facility_data(df)
            
            # Display additional statistics
            display_additional_stats(df)
            
            # Display results
            st.header("Analysis Results")
            
            # Display summary table
            st.subheader("Summary Statistics")
            styled_summary = summary_table.style.format({
                'Percentage': '{:.2f}%'
            })
            st.dataframe(styled_summary)
            
            # Create and display visualizations in columns
            col1, col2 = st.columns(2)
            
            with col1:
                # Display pie chart
                pie_fig = create_pie_chart(summary_table)
                st.plotly_chart(pie_fig)
            
            with col2:
                # Display bar chart
                count_fig = px.bar(
                    summary_table,
                    x='Classification',
                    y='Count',
                    color='Classification',
                    title='Facility Matching Outcomes',
                    color_discrete_map={
                        "HF in both DHIS2 and MFL": "#6a9955",
                        "HF in MFL and not in DHIS2": "#b55d5d",
                        "HF in DHIS2 and not in MFL": "#5d89b5",
                        "Unclassified": "gray"
                    }
                )
                count_fig.update_layout(
                    xaxis_title="Classification",
                    yaxis_title="Number of Facilities",
                    showlegend=False
                )
                st.plotly_chart(count_fig)
            
            # Display percentage visualization
            percentage_fig = px.bar(
                summary_table,
                x='Classification',
                y='Percentage',
                color='Classification',
                title='Percentage Distribution of Matches',
                color_discrete_map={
                    "HF in both DHIS2 and MFL": "#6a9955",
                    "HF in MFL and not in DHIS2": "#b55d5d",
                    "HF in DHIS2 and not in MFL": "#5d89b5",
                    "Unclassified": "gray"
                }
            )
            percentage_fig.update_layout(
                xaxis_title="Classification",
                yaxis_title="Percentage (%)",
                showlegend=False
            )
            st.plotly_chart(percentage_fig)
            
            # Download section
            st.header("Download Results")
            
            # Convert DataFrames to Excel
            classified_buffer = io.BytesIO()
            summary_buffer = io.BytesIO()
            
            with pd.ExcelWriter(classified_buffer, engine='openpyxl') as writer:
                classified_results.to_excel(writer, index=False)
                summary_table.to_excel(writer, sheet_name='Summary', index=False)
            
            with pd.ExcelWriter(summary_buffer, engine='openpyxl') as writer:
                summary_table.to_excel(writer, index=False)
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download Detailed Results",
                    data=classified_buffer.getvalue(),
                    file_name="health_facility_classification_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col2:
                st.download_button(
                    label="Download Summary Results",
                    data=summary_buffer.getvalue(),
                    file_name="health_facility_summary_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

if __name__ == "__main__":
    main()
