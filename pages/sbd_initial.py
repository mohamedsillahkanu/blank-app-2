import streamlit as st
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set page config
st.set_page_config(page_title="Data Analysis Dashboard", layout="wide")

# Streamlit App
st.title("📊 Text Data Extraction & Visualization Dashboard")

# Upload file
uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])

# For demo purposes, keeping the hardcoded filename as fallback
if not uploaded_file:
    uploaded_file = "Report_GMB253374_SBD_1749318384635_submissions.xlsx"

if uploaded_file:
    try:
        # Read the uploaded Excel file
        df_original = pd.read_excel(uploaded_file)
        
        # Create empty lists to store extracted data
        districts, chiefdoms, phu_names, community_names, school_names = [], [], [], [], []
        
        # Process each row in the "Scan QR code" column
        for qr_text in df_original["Scan QR code"]:
            if pd.isna(qr_text):
                districts.append(None)
                chiefdoms.append(None)
                phu_names.append(None)
                community_names.append(None)
                school_names.append(None)
                continue
                
            # Extract values using regex patterns
            district_match = re.search(r"District:\s*([^\n]+)", str(qr_text))
            districts.append(district_match.group(1).strip() if district_match else None)
            
            chiefdom_match = re.search(r"Chiefdom:\s*([^\n]+)", str(qr_text))
            chiefdoms.append(chiefdom_match.group(1).strip() if chiefdom_match else None)
            
            phu_match = re.search(r"PHU name:\s*([^\n]+)", str(qr_text))
            phu_names.append(phu_match.group(1).strip() if phu_match else None)
            
            community_match = re.search(r"Community name:\s*([^\n]+)", str(qr_text))
            community_names.append(community_match.group(1).strip() if community_match else None)
            
            school_match = re.search(r"Name of school:\s*([^\n]+)", str(qr_text))
            school_names.append(school_match.group(1).strip() if school_match else None)
        
        # Create a new DataFrame with extracted values
        extracted_df = pd.DataFrame({
            "District": districts,
            "Chiefdom": chiefdoms,
            "PHU Name": phu_names,
            "Community Name": community_names,
            "School Name": school_names
        })
        
        # Add all other columns from the original DataFrame
        for column in df_original.columns:
            if column != "Scan QR code":
                extracted_df[column] = df_original[column]
        
        # Create tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs(["📄 Data Overview", "🏥 ITN Analysis", "🎓 Enrollment Analysis", "📊 Combined Insights"])
        
        with tab1:
            st.subheader("📄 Original Data Sample")
            st.dataframe(df_original.head())
            
            st.subheader("📋 Extracted Data")
            st.dataframe(extracted_df)
            
            # Data quality summary
            st.subheader("📈 Data Quality Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Records", len(extracted_df))
            with col2:
                missing_districts = extracted_df["District"].isna().sum()
                st.metric("Missing Districts", missing_districts)
            with col3:
                complete_records = len(extracted_df.dropna())
                st.metric("Complete Records", complete_records)
        
        with tab2:
            st.subheader("🎓 School Enrollment Analysis")
            
            # Define enrollment columns
            enrollment_columns = []
            for class_num in range(1, 6):
                enrollment_columns.extend([
                    f"Number of enrollments in class {class_num}",
                    f"Number of boys in class {class_num}",
                    f"Number of girls in class {class_num}"
                ])
            
            # Check if enrollment columns exist
            existing_enrollment_cols = [col for col in enrollment_columns if col in extracted_df.columns]
            
            if existing_enrollment_cols:
                st.write(f"Found {len(existing_enrollment_cols)} enrollment columns")
                
                # Summary buttons section
                col1, col2 = st.columns(2)
                
                with col1:
                    district_summary_button = st.button("Show District Summary")
                
                with col2:
                    chiefdom_summary_button = st.button("Show Chiefdom Summary")
                
                # Display District Summary
                if district_summary_button:
                    st.subheader("📈 Enrollment Summary by District")
                    
                    # Create aggregation dictionary for enrollment data
                    agg_dict = {}
                    
                    # Add enrollment columns to aggregation
                    for class_num in range(1, 6):
                        total_col = f"Number of enrollments in class {class_num}"
                        boys_col = f"Number of boys in class {class_num}"
                        girls_col = f"Number of girls in class {class_num}"
                        
                        if total_col in extracted_df.columns:
                            agg_dict[total_col] = "sum"
                        if boys_col in extracted_df.columns:
                            agg_dict[boys_col] = "sum"
                        if girls_col in extracted_df.columns:
                            agg_dict[girls_col] = "sum"
                    
                    # Group by District
                    district_summary = extracted_df.groupby("District").agg(agg_dict).reset_index()
                    
                    # Calculate enrollment totals
                    district_summary["Total Enrollment"] = 0
                    district_summary["Total Boys"] = 0
                    district_summary["Total Girls"] = 0
                    
                    for class_num in range(1, 6):
                        total_col = f"Number of enrollments in class {class_num}"
                        boys_col = f"Number of boys in class {class_num}"
                        girls_col = f"Number of girls in class {class_num}"
                        
                        if total_col in district_summary.columns:
                            district_summary["Total Enrollment"] += district_summary[total_col]
                        if boys_col in district_summary.columns:
                            district_summary["Total Boys"] += district_summary[boys_col]
                        if girls_col in district_summary.columns:
                            district_summary["Total Girls"] += district_summary[girls_col]
                    
                    # Calculate additional metrics
                    district_summary["Gender Ratio (Girls per 100 Boys)"] = (
                        district_summary["Total Girls"] / district_summary["Total Boys"] * 100
                    ).round(1)
                    district_summary["Gender Parity Index"] = (
                        district_summary["Total Girls"] / district_summary["Total Boys"]
                    ).round(3)
                    
                    # Replace inf and NaN values
                    district_summary = district_summary.replace([np.inf, -np.inf], 0).fillna(0)
                    
                    st.dataframe(district_summary)
                    
                    # Enhanced visualization
                    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))
                    
                    # Total Enrollment by District
                    district_summary.plot(kind="bar", x="District", y="Total Enrollment", 
                                        ax=ax1, color="steelblue", alpha=0.7)
                    ax1.set_title("Total Enrollment by District")
                    ax1.set_xlabel("")
                    ax1.set_ylabel("Number of Students")
                    ax1.tick_params(axis='x', rotation=45)
                    
                    # Gender Distribution
                    district_summary.plot(kind="bar", x="District", y=["Total Boys", "Total Girls"], 
                                        ax=ax2, color=["lightblue", "pink"])
                    ax2.set_title("Student Enrollment by Gender and District")
                    ax2.set_xlabel("")
                    ax2.set_ylabel("Number of Students")
                    ax2.tick_params(axis='x', rotation=45)
                    
                    # Gender Parity Index
                    ax3.bar(district_summary["District"], district_summary["Gender Parity Index"], 
                           color="purple", alpha=0.7)
                    ax3.set_title("Gender Parity Index by District")
                    ax3.set_xlabel("")
                    ax3.set_ylabel("Gender Parity Index")
                    ax3.tick_params(axis='x', rotation=45)
                    ax3.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Perfect Parity (1.0)')
                    ax3.legend()
                    
                    # Class Distribution (stacked)
                    class_cols = [f"Number of enrollments in class {i}" for i in range(1, 6) 
                                 if f"Number of enrollments in class {i}" in district_summary.columns]
                    if class_cols:
                        district_summary.plot(kind="bar", x="District", y=class_cols, 
                                            ax=ax4, stacked=True, colormap='Set3')
                        ax4.set_title("Enrollment Distribution by Class and District")
                        ax4.set_xlabel("")
                        ax4.set_ylabel("Number of Students")
                        ax4.tick_params(axis='x', rotation=45)
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Class-wise breakdown
                    st.subheader("📚 Class-wise Enrollment by District")
                    class_breakdown_cols = ["District"]
                    for class_num in range(1, 6):
                        total_col = f"Number of enrollments in class {class_num}"
                        boys_col = f"Number of boys in class {class_num}"
                        girls_col = f"Number of girls in class {class_num}"
                        
                        if total_col in district_summary.columns:
                            class_breakdown_cols.extend([total_col, boys_col, girls_col])
                    
                    if len(class_breakdown_cols) > 1:
                        class_breakdown = district_summary[class_breakdown_cols]
                        st.dataframe(class_breakdown)
                
                # Display Chiefdom Summary
                if chiefdom_summary_button:
                    st.subheader("📈 Enrollment Summary by Chiefdom")
                    
                    # Create aggregation dictionary for enrollment data
                    agg_dict = {}
                    
                    # Add enrollment columns to aggregation
                    for class_num in range(1, 6):
                        total_col = f"Number of enrollments in class {class_num}"
                        boys_col = f"Number of boys in class {class_num}"
                        girls_col = f"Number of girls in class {class_num}"
                        
                        if total_col in extracted_df.columns:
                            agg_dict[total_col] = "sum"
                        if boys_col in extracted_df.columns:
                            agg_dict[boys_col] = "sum"
                        if girls_col in extracted_df.columns:
                            agg_dict[girls_col] = "sum"
                    
                    # Group by District and Chiefdom
                    chiefdom_summary = extracted_df.groupby(["District", "Chiefdom"]).agg(agg_dict).reset_index()
                    
                    # Calculate enrollment totals
                    chiefdom_summary["Total Enrollment"] = 0
                    chiefdom_summary["Total Boys"] = 0
                    chiefdom_summary["Total Girls"] = 0
                    
                    for class_num in range(1, 6):
                        total_col = f"Number of enrollments in class {class_num}"
                        boys_col = f"Number of boys in class {class_num}"
                        girls_col = f"Number of girls in class {class_num}"
                        
                        if total_col in chiefdom_summary.columns:
                            chiefdom_summary["Total Enrollment"] += chiefdom_summary[total_col]
                        if boys_col in chiefdom_summary.columns:
                            chiefdom_summary["Total Boys"] += chiefdom_summary[boys_col]
                        if girls_col in chiefdom_summary.columns:
                            chiefdom_summary["Total Girls"] += chiefdom_summary[girls_col]
                    
                    # Calculate additional metrics
                    chiefdom_summary["Gender Ratio (Girls per 100 Boys)"] = (
                        chiefdom_summary["Total Girls"] / chiefdom_summary["Total Boys"] * 100
                    ).round(1)
                    chiefdom_summary["Gender Parity Index"] = (
                        chiefdom_summary["Total Girls"] / chiefdom_summary["Total Boys"]
                    ).round(3)
                    
                    # Replace inf and NaN values
                    chiefdom_summary = chiefdom_summary.replace([np.inf, -np.inf], 0).fillna(0)
                    
                    st.dataframe(chiefdom_summary)
                    
                    # Enhanced visualization
                    chiefdom_summary['Label'] = chiefdom_summary['District'] + ' - ' + chiefdom_summary['Chiefdom']
                    
                    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 12))
                    
                    # Total Enrollment by Chiefdom
                    chiefdom_summary.plot(kind="bar", x="Label", y="Total Enrollment", 
                                        ax=ax1, color="steelblue", alpha=0.7)
                    ax1.set_title("Total Enrollment by Chiefdom")
                    ax1.set_xlabel("")
                    ax1.set_ylabel("Number of Students")
                    ax1.tick_params(axis='x', rotation=45)
                    
                    # Gender Distribution
                    chiefdom_summary.plot(kind="bar", x="Label", y=["Total Boys", "Total Girls"], 
                                        ax=ax2, color=["lightblue", "pink"])
                    ax2.set_title("Student Enrollment by Gender and Chiefdom")
                    ax2.set_xlabel("")
                    ax2.set_ylabel("Number of Students")
                    ax2.tick_params(axis='x', rotation=45)
                    
                    # Gender Parity Index
                    ax3.bar(range(len(chiefdom_summary)), chiefdom_summary["Gender Parity Index"], 
                           color="purple", alpha=0.7)
                    ax3.set_title("Gender Parity Index by Chiefdom")
                    ax3.set_xlabel("")
                    ax3.set_ylabel("Gender Parity Index")
                    ax3.set_xticks(range(len(chiefdom_summary)))
                    ax3.set_xticklabels(chiefdom_summary["Label"], rotation=45)
                    ax3.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Perfect Parity (1.0)')
                    ax3.legend()
                    
                    # Class Distribution (stacked)
                    class_cols = [f"Number of enrollments in class {i}" for i in range(1, 6) 
                                 if f"Number of enrollments in class {i}" in chiefdom_summary.columns]
                    if class_cols:
                        chiefdom_summary.plot(kind="bar", x="Label", y=class_cols, 
                                            ax=ax4, stacked=True, colormap='Set3')
                        ax4.set_title("Enrollment Distribution by Class and Chiefdom")
                        ax4.set_xlabel("")
                        ax4.set_ylabel("Number of Students")
                        ax4.tick_params(axis='x', rotation=45)
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Class-wise breakdown table
                    st.subheader("📚 Class-wise Enrollment Breakdown by Chiefdom")
                    
                    # Create a detailed class breakdown
                    class_breakdown_cols = ["District", "Chiefdom"]
                    for class_num in range(1, 6):
                        total_col = f"Number of enrollments in class {class_num}"
                        boys_col = f"Number of boys in class {class_num}"
                        girls_col = f"Number of girls in class {class_num}"
                        
                        if total_col in chiefdom_summary.columns:
                            class_breakdown_cols.extend([total_col, boys_col, girls_col])
                    
                    if len(class_breakdown_cols) > 2:
                        class_breakdown = chiefdom_summary[class_breakdown_cols]
                        st.dataframe(class_breakdown)
                        
                        # Class distribution visualization
                        st.subheader("📊 Enrollment Distribution Across Classes")
                        
                        # Prepare data for class distribution chart
                        class_totals = {}
                        for class_num in range(1, 6):
                            total_col = f"Number of enrollments in class {class_num}"
                            if total_col in chiefdom_summary.columns:
                                class_totals[f"Class {class_num}"] = chiefdom_summary[total_col].sum()
                        
                        if class_totals:
                            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
                            
                            # Pie chart for overall class distribution
                            ax1.pie(class_totals.values(), labels=class_totals.keys(), autopct='%1.1f%%', 
                                   startangle=90, colors=plt.cm.Set3.colors)
                            ax1.set_title("Overall Class Distribution")
                            
                            # Bar chart for class totals
                            ax2.bar(class_totals.keys(), class_totals.values(), 
                                   color=plt.cm.Set3.colors[:len(class_totals)])
                            ax2.set_title("Total Enrollment by Class")
                            ax2.set_ylabel("Number of Students")
                            ax2.tick_params(axis='x', rotation=0)
                            
                            plt.tight_layout()
                            st.pyplot(fig)
            else:
                st.warning("No enrollment columns found in the dataset.") 8))
                        
                        chiefdom_summary.plot(kind="bar", x="Label", y="ITN given", 
                                            ax=ax, color="orange")
                        ax.set_title("ITN Given by Chiefdom")
                        ax.set_xlabel("")
                        ax.set_ylabel("ITN Count")
                        ax.tick_params(axis='x', rotation=45)
                        
                        plt.tight_layout()
                        st.pyplot(fig)class_breakdown_cols) > 2:
                            class_breakdown = chiefdom_summary[class_breakdown_cols]
                            st.dataframe(class_breakdown)
                            
                            # Class distribution visualization
                            st.subheader("📊 Enrollment Distribution Across Classes")
                            
                            # Prepare data for class distribution chart
                            class_totals = {}
                            for class_num in range(1, 6):
                                total_col = f"Number of enrollments in class {class_num}"
                                if total_col in chiefdom_summary.columns:
                                    class_totals[f"Class {class_num}"] = chiefdom_summary[total_col].sum()
                            
                            if class_totals:
                                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
                                
                                # Pie chart for overall class distribution
                                ax1.pie(class_totals.values(), labels=class_totals.keys(), autopct='%1.1f%%', 
                                       startangle=90, colors=plt.cm.Set3.colors)
                                ax1.set_title("Overall Class Distribution")
                                
                                # Bar chart for class totals
                                ax2.bar(class_totals.keys(), class_totals.values(), 
                                       color=plt.cm.Set3.colors[:len(class_totals)])
                                ax2.set_title("Total Enrollment by Class")
                                ax2.set_ylabel("Number of Students")
                                ax2.tick_params(axis='x', rotation=0)
                                
                                plt.tight_layout()
                                st.pyplot(fig)
                    else:
                        # If no enrollment data, show only ITN charts
                        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
                        
                        # ITN Distribution Chart
                        chiefdom_summary.plot(kind="bar", x="Label", y=["ITN received", "ITN given"], 
                                            ax=ax1, color=["steelblue", "orange"])
                        ax1.set_title("ITN Received vs. Given by Chiefdom")
                        ax1.set_xlabel("")
                        ax1.set_ylabel("ITN Count")
                        ax1.tick_params(axis='x', rotation=45)
                        
                        # Distribution Rate Chart
                        ax2.bar(range(len(chiefdom_summary)), chiefdom_summary["Distribution Rate (%)"], 
                               color="green", alpha=0.7)
                        ax2.set_title("ITN Distribution Rate by Chiefdom (%)")
                        ax2.set_xlabel("")
                        ax2.set_ylabel("Distribution Rate (%)")
                        ax2.set_xticks(range(len(chiefdom_summary)))
                        ax2.set_xticklabels(chiefdom_summary["Label"], rotation=45)
                        
                        plt.tight_layout()
                        st.pyplot(fig)
            else:
                st.warning("ITN given column not found in the dataset.")
        
        with tab3:
            st.subheader("📊 Educational Insights & Analytics")
            
            # Check if enrollment data exists
            has_enrollment = any(f"Number of enrollments in class {i}" in extracted_df.columns for i in range(1, 6))
            
            if has_enrollment:
                st.write("### Comprehensive Educational Analysis")
                
                # Create analysis by district
                educational_analysis = []
                
                for district in extracted_df["District"].dropna().unique():
                    district_data = extracted_df[extracted_df["District"] == district]
                    
                    # Calculate totals for this district
                    total_enrollment = sum([district_data[f"Number of enrollments in class {i}"].sum() 
                                          for i in range(1, 6) 
                                          if f"Number of enrollments in class {i}" in district_data.columns])
                    
                    total_boys = sum([district_data[f"Number of boys in class {i}"].sum() 
                                    for i in range(1, 6) 
                                    if f"Number of boys in class {i}" in district_data.columns])
                    
                    total_girls = sum([district_data[f"Number of girls in class {i}"].sum() 
                                     for i in range(1, 6) 
                                     if f"Number of girls in class {i}" in district_data.columns])
                    
                    # Calculate class-wise data
                    class_data = {}
                    for class_num in range(1, 6):
                        total_col = f"Number of enrollments in class {class_num}"
                        if total_col in district_data.columns:
                            class_data[f"Class {class_num}"] = district_data[total_col].sum()
                    
                    # Calculate metrics
                    gender_parity = (total_girls / total_boys) if total_boys > 0 else 0
                    
                    educational_analysis.append({
                        'District': district,
                        'Total Enrollment': total_enrollment,
                        'Boys': total_boys,
                        'Girls': total_girls,
                        'Gender Parity Index': round(gender_parity, 3),
                        'Girls per 100 Boys': round(total_girls / total_boys * 100, 1) if total_boys > 0 else 0,
                        **class_data
                    })
                
                analysis_df = pd.DataFrame(educational_analysis)
                st.dataframe(analysis_df)
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    total_students = analysis_df['Total Enrollment'].sum()
                    st.metric("Total Students", f"{total_students:,}")
                with col2:
                    total_boys = analysis_df['Boys'].sum()
                    st.metric("Total Boys", f"{total_boys:,}")
                with col3:
                    total_girls = analysis_df['Girls'].sum()
                    st.metric("Total Girls", f"{total_girls:,}")
                with col4:
                    overall_parity = (total_girls / total_boys) if total_boys > 0 else 0
                    st.metric("Overall Gender Parity", f"{overall_parity:.3f}")
                
                # Visualization
                if len(analysis_df) > 1:
                    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))
                    
                    # Total Enrollment by District
                    analysis_df.plot(kind='bar', x='District', y='Total Enrollment', 
                                   ax=ax1, color='steelblue', alpha=0.7)
                    ax1.set_title('Total Enrollment by District')
                    ax1.set_ylabel('Number of Students')
                    ax1.tick_params(axis='x', rotation=45)
                    
                    # Gender Distribution
                    analysis_df.plot(kind='bar', x='District', y=['Boys', 'Girls'], 
                                   ax=ax2, color=['lightblue', 'pink'])
                    ax2.set_title('Gender Distribution by District')
                    ax2.set_ylabel('Number of Students')
                    ax2.tick_params(axis='x', rotation=45)
                    
                    # Gender Parity Index
                    ax3.bar(analysis_df['District'], analysis_df['Gender Parity Index'], 
                           color='purple', alpha=0.7)
                    ax3.set_title('Gender Parity Index by District')
                    ax3.set_ylabel('Gender Parity Index (1.0 = Perfect Parity)')
                    ax3.tick_params(axis='x', rotation=45)
                    ax3.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Perfect Parity')
                    ax3.axhline(y=0.97, color='orange', linestyle='--', alpha=0.7, label='UNESCO Target (0.97-1.03)')
                    ax3.axhline(y=1.03, color='orange', linestyle='--', alpha=0.7)
                    ax3.legend()
                    
                    # Class Distribution (if class data exists)
                    class_cols = [col for col in analysis_df.columns if col.startswith('Class ')]
                    if class_cols:
                        analysis_df.plot(kind='bar', x='District', y=class_cols, 
                                       ax=ax4, stacked=True, colormap='Set3')
                        ax4.set_title('Class Distribution by District')
                        ax4.set_ylabel('Number of Students')
                        ax4.tick_params(axis='x', rotation=45)
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Priority analysis
                    st.subheader("📍 Priority Areas for Educational Support")
                    
                    # Identify areas needing attention
                    priority_analysis = analysis_df.copy()
                    
                    # Calculate priority scores
                    priority_analysis['Low Enrollment Score'] = (
                        1 - (priority_analysis['Total Enrollment'] / priority_analysis['Total Enrollment'].max())
                    )
                    priority_analysis['Gender Gap Score'] = abs(1 - priority_analysis['Gender Parity Index'])
                    priority_analysis['Priority Score'] = (
                        priority_analysis['Low Enrollment Score'] + priority_analysis['Gender Gap Score']
                    )
                    
                    priority_analysis = priority_analysis.sort_values('Priority Score', ascending=False)
                    
                    st.write("Districts ranked by need for intervention:")
                    priority_cols = ['District', 'Total Enrollment', 'Gender Parity Index', 'Priority Score']
                    st.dataframe(priority_analysis[priority_cols])
                    
                    # Educational equity analysis
                    st.subheader("⚖️ Educational Equity Analysis")
                    
                    # Gender parity analysis
                    parity_perfect = len(analysis_df[(analysis_df['Gender Parity Index'] >= 0.97) & 
                                                   (analysis_df['Gender Parity Index'] <= 1.03)])
                    parity_total = len(analysis_df)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Districts with Gender Parity", f"{parity_perfect}/{parity_total}")
                    with col2:
                        parity_percentage = (parity_perfect / parity_total * 100) if parity_total > 0 else 0
                        st.metric("Gender Parity Achievement", f"{parity_percentage:.1f}%")
                    with col3:
                        avg_enrollment = analysis_df['Total Enrollment'].mean()
                        st.metric("Average District Enrollment", f"{avg_enrollment:.0f}")
                
            else:
                st.warning("No enrollment data found for educational analysis.")
        
        with tab4:
            st.subheader("📊 Data Trends & Insights")
            
            # Check if enrollment data exists
            has_enrollment = any(f"Number of enrollments in class {i}" in extracted_df.columns for i in range(1, 6))
            
            if has_enrollment:
                st.write("### School Distribution and Access Analysis")
                
                # Schools per administrative unit analysis
                st.subheader("🏫 School Distribution Analysis")
                
                # Calculate number of schools per administrative level
                admin_levels = ["District", "Chiefdom", "PHU Name", "Community Name"]
                distribution_data = []
                
                for level in admin_levels:
                    if level in extracted_df.columns:
                        level_stats = extracted_df.groupby(level).agg({
                            'School Name': 'count',
                            **{f"Number of enrollments in class {i}": 'sum' for i in range(1, 6) 
                               if f"Number of enrollments in class {i}" in extracted_df.columns}
                        }).reset_index()
                        
                        # Calculate total enrollment per administrative unit
                        level_stats['Total Enrollment'] = 0
                        for class_num in range(1, 6):
                            total_col = f"Number of enrollments in class {class_num}"
                            if total_col in level_stats.columns:
                                level_stats['Total Enrollment'] += level_stats[total_col]
                        
                        level_stats['Students per School'] = (
                            level_stats['Total Enrollment'] / level_stats['School Name']
                        ).round(1)
                        
                        distribution_data.append({
                            'Administrative Level': level,
                            'Number of Units': len(level_stats),
                            'Average Schools per Unit': level_stats['School Name'].mean().round(1),
                            'Average Students per Unit': level_stats['Total Enrollment'].mean().round(0),
                            'Average Students per School': level_stats['Students per School'].mean().round(1)
                        })
                
                if distribution_data:
                    distribution_df = pd.DataFrame(distribution_data)
                    st.dataframe(distribution_df)
                
                # Class transition analysis
                st.subheader("📈 Class Enrollment Patterns")
                
                # Calculate enrollment by class
                class_enrollment = {}
                for class_num in range(1, 6):
                    total_col = f"Number of enrollments in class {class_num}"
                    if total_col in extracted_df.columns:
                        class_enrollment[f"Class {class_num}"] = extracted_df[total_col].sum()
                
                if class_enrollment:
                    # Create transition analysis
                    classes = list(class_enrollment.keys())
                    enrollments = list(class_enrollment.values())
                    
                    # Calculate retention rates (assuming perfect progression)
                    retention_rates = []
                    for i in range(len(enrollments) - 1):
                        if enrollments[i] > 0:
                            retention = (enrollments[i + 1] / enrollments[i]) * 100
                            retention_rates.append(retention)
                        else:
                            retention_rates.append(0)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Enrollment by class chart
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.bar(classes, enrollments, color=plt.cm.Set3.colors[:len(classes)])
                        ax.set_title('Enrollment by Class Level')
                        ax.set_ylabel('Number of Students')
                        ax.tick_params(axis='x', rotation=45)
                        
                        # Add enrollment numbers on top of bars
                        for i, v in enumerate(enrollments):
                            ax.text(i, v + max(enrollments) * 0.01, str(v), 
                                   ha='center', va='bottom', fontweight='bold')
                        
                        plt.tight_layout()
                        st.pyplot(fig)
                    
                    with col2:
                        # Retention analysis
                        if retention_rates:
                            fig, ax = plt.subplots(figsize=(10, 6))
                            transitions = [f"{classes[i]} to {classes[i+1]}" for i in range(len(retention_rates))]
                            colors = ['green' if r >= 95 else 'orange' if r >= 85 else 'red' for r in retention_rates]
                            
                            ax.bar(range(len(retention_rates)), retention_rates, color=colors, alpha=0.7)
                            ax.set_title('Class Transition Rates')
                            ax.set_ylabel('Retention Rate (%)')
                            ax.set_xticks(range(len(retention_rates)))
                            ax.set_xticklabels([f"C{i+1}→C{i+2}" for i in range(len(retention_rates))], rotation=0)
                            ax.axhline(y=100, color='black', linestyle='--', alpha=0.5, label='100%')
                            ax.axhline(y=95, color='green', linestyle='--', alpha=0.5, label='95% (Good)')
                            ax.axhline(y=85, color='orange', linestyle='--', alpha=0.5, label='85% (Moderate)')
                            
                            # Add percentage labels on bars
                            for i, v in enumerate(retention_rates):
                                ax.text(i, v + 1, f"{v:.1f}%", ha='center', va='bottom', fontweight='bold')
                            
                            ax.legend()
                            plt.tight_layout()
                            st.pyplot(fig)
                
                # Geographic analysis
                st.subheader("🗺️ Geographic Distribution of Students")
                
                # Calculate enrollment by district and chiefdom
                geo_analysis = extracted_df.groupby(['District', 'Chiefdom']).agg({
                    'School Name': 'count',
                    **{f"Number of enrollments in class {i}": 'sum' for i in range(1, 6) 
                       if f"Number of enrollments in class {i}" in extracted_df.columns}
                }).reset_index()
                
                # Calculate totals
                geo_analysis['Total Enrollment'] = 0
                for class_num in range(1, 6):
                    total_col = f"Number of enrollments in class {class_num}"
                    if total_col in geo_analysis.columns:
                        geo_analysis['Total Enrollment'] += geo_analysis[total_col]
                
                geo_analysis['Students per School'] = (
                    geo_analysis['Total Enrollment'] / geo_analysis['School Name']
                ).round(1)
                
                # Sort by total enrollment
                geo_analysis = geo_analysis.sort_values('Total Enrollment', ascending=False)
                
                st.write("**Top Areas by Enrollment:**")
                top_areas = geo_analysis.head(10)[['District', 'Chiefdom', 'School Name', 'Total Enrollment', 'Students per School']]
                st.dataframe(top_areas)
                
                # Summary statistics
                st.subheader("📊 Key Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_schools = extracted_df['School Name'].nunique()
                    st.metric("Total Schools", total_schools)
                
                with col2:
                    avg_students_per_school = geo_analysis['Students per School'].mean()
                    st.metric("Avg Students/School", f"{avg_students_per_school:.1f}")
                
                with col3:
                    max_enrollment = geo_analysis['Total Enrollment'].max()
                    st.metric("Largest School Area", f"{max_enrollment:,} students")
                
                with col4:
                    min_enrollment = geo_analysis['Total Enrollment'].min()
                    st.metric("Smallest School Area", f"{min_enrollment:,} students")
                
                # Access and equity indicators
                st.subheader("⚖️ Educational Access Indicators")
                
                # Calculate quartiles for school size
                q1 = geo_analysis['Students per School'].quantile(0.25)
                q3 = geo_analysis['Students per School'].quantile(0.75)
                
                small_schools = len(geo_analysis[geo_analysis['Students per School'] < q1])
                large_schools = len(geo_analysis[geo_analysis['Students per School'] > q3])
                total_areas = len(geo_analysis)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Small School Areas", f"{small_schools} ({small_schools/total_areas*100:.1f}%)")
                    st.caption(f"< {q1:.1f} students per school")
                
                with col2:
                    st.metric("Large School Areas", f"{large_schools} ({large_schools/total_areas*100:.1f}%)")
                    st.caption(f"> {q3:.1f} students per school")
                
                with col3:
                    school_distribution_cv = (geo_analysis['Students per School'].std() / 
                                            geo_analysis['Students per School'].mean())
                    st.metric("Distribution Inequality", f"{school_distribution_cv:.2f}")
                    st.caption("Coefficient of Variation")
                
            else:
                st.warning("No enrollment data found for trend analysis.")
        
        # Filtering section (moved to sidebar)
        st.sidebar.header("🔍 Advanced Filtering")
        
        # Hierarchy selection
        hierarchy = {
            "District": ["District"],
            "Chiefdom": ["District", "Chiefdom"],
            "PHU Name": ["District", "Chiefdom", "PHU Name"],
            "Community Name": ["District", "Chiefdom", "PHU Name", "Community Name"],
            "School Name": ["District", "Chiefdom", "PHU Name", "Community Name", "School Name"]
        }
        
        grouping_selection = st.sidebar.radio(
            "Select the level for grouping:",
            ["District", "Chiefdom", "PHU Name", "Community Name", "School Name"],
            index=0
        )
        
        # Apply hierarchical filters
        filtered_df = extracted_df.copy()
        selected_values = {}
        
        for level in hierarchy[grouping_selection]:
            level_values = sorted(filtered_df[level].dropna().unique())
            
            if level_values:
                selected_value = st.sidebar.selectbox(f"Select {level}", level_values)
                selected_values[level] = selected_value
                filtered_df = filtered_df[filtered_df[level] == selected_value]
        
        # Display filtered results in sidebar
        if not filtered_df.empty:
            st.sidebar.write(f"**Filtered Records:** {len(filtered_df)}")
            if st.sidebar.button("Show Filtered Data"):
                st.subheader(f"🔍 Filtered Data ({len(filtered_df)} records)")
                st.dataframe(filtered_df)
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.write("Please make sure the Excel file contains the expected columns.")

else:
    st.info("Please upload an Excel file to begin analysis.")
    st.write("Expected columns include:")
    st.write("- Scan QR code (containing location information)")
    st.write("- ITN received, ITN given (for distribution analysis)")
    st.write("- Enrollment columns by class and gender (for education analysis)")
