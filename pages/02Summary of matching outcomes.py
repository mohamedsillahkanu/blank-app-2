import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# Page configuration
st.set_page_config(page_title="Health Facility Matching Analysis", layout="wide")

# Show welcome animations if first load
if 'first_load' not in st.session_state:
    st.session_state.first_load = True
    st.balloons()
    st.snow()

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
    """Improved health facility data processing with detailed calculations"""
    
    # Display column lengths and null counts
    st.write("### Column Information")
    col_info = pd.DataFrame({
        'Column': df.columns,
        'Total Count': len(df),
        'Non-Null Count': df.count(),
        'Null Count': df.isnull().sum(),
        'Percentage Filled': round((df.count() / len(df)) * 100, 2)
    })
    st.dataframe(col_info)
    
    # Get unique facilities from both sources
    dhis2_facilities = set(df['hf_DHIS2'].dropna().unique())
    mfl_facilities = set(df['New_MFL'].dropna().unique())
    
    # Calculate intersection and differences
    both_systems = dhis2_facilities.intersection(mfl_facilities)
    only_mfl = mfl_facilities - dhis2_facilities
    only_dhis2 = dhis2_facilities - mfl_facilities
    
    # Create classification DataFrame
    classifications = []
    
    # Add facilities in both systems
    for facility in both_systems:
        classifications.append({
            'Health_Facility_Name': facility,
            'Classification': 'HF in both DHIS2 and MFL',
            'Source': 'Both'
        })
    
    # Add MFL-only facilities
    for facility in only_mfl:
        classifications.append({
            'Health_Facility_Name': facility,
            'Classification': 'HF in MFL and not in DHIS2',
            'Source': 'MFL'
        })
    
    # Add DHIS2-only facilities
    for facility in only_dhis2:
        classifications.append({
            'Health_Facility_Name': facility,
            'Classification': 'HF in DHIS2 and not in MFL',
            'Source': 'DHIS2'
        })
    
    # Create DataFrame from classifications
    all_unique_names = pd.DataFrame(classifications)
    
    # Create summary table
    summary_table = pd.DataFrame([
        {'Classification': 'HF in both DHIS2 and MFL', 'Count': len(both_systems)},
        {'Classification': 'HF in MFL and not in DHIS2', 'Count': len(only_mfl)},
        {'Classification': 'HF in DHIS2 and not in MFL', 'Count': len(only_dhis2)}
    ])
    
    # Calculate percentages
    total_facilities = len(both_systems) + len(only_mfl) + len(only_dhis2)
    summary_table['Percentage'] = round((summary_table['Count'] / total_facilities) * 100, 2)
    
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
    st.subheader("Match Quality Distribution")
    
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
    st.title("Health Facility Matching Analysis")
    
    # File upload with multiple formats
    uploaded_file = st.file_uploader(
        "Upload the Facility_matching_result file (CSV, Excel)", 
        type=['csv', 'xlsx', 'xls']
    )
    
    if uploaded_file is not None:
        # Show animation on file upload
        st.balloons()
        
        # Read the uploaded file
        df = read_file(uploaded_file)
        
        if df is not None:
            st.snow()  # Show snow after successful file read
            
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
                if st.download_button(
                    label="Download Detailed Results",
                    data=classified_buffer.getvalue(),
                    file_name="health_facility_classification_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ):
                    st.snow()  # Show snow on download
            
            with col2:
                if st.download_button(
                    label="Download Summary Results",
                    data=summary_buffer.getvalue(),
                    file_name="health_facility_summary_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ):
                    st.balloons()  # Show balloons on download

if __name__ == "__main__":
    main()
