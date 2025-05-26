import streamlit as st
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import requests
import json
from datetime import datetime

# Streamlit App
st.title("📊 Clappia Data Analysis Dashboard")

# Configuration
CLAPPIA_URL = "https://icf.clappia.com/app/GMB253374/submissions/filters/eyJjb2x1bW5XaWR0aHMiOnt9LCJjb2x1bW5PcmRlcnMiOnt9LCJpbnRlcnZhbCI6ImRheSIsImZpbHRlcnMiOltdLCJibGFja2xpc3RlZEZpZWxkSWRzIjpbXSwic29ydEZpZWxkcyI6W3sic29ydEJ5IjoiJGxhc3RNb2RpZmllZEF0IiwiZGlyZWN0aW9uIjoiZGVzYyJ9XSwibmF2YmFyQ29sbGFwc2VkIjpmYWxzZX0="

# Data Upload Section
st.subheader("📂 Upload Clappia Data")
st.info("📋 **How to get your data:**")
st.markdown("""
1. **Go to your Clappia submissions page:** 
   `https://icf.clappia.com/app/GMB253374/submissions`
   
2. **Click the Download button** (usually at the top of the submissions table)

3. **Export as Excel or CSV format**

4. **Upload the downloaded file below** ⬇️
""")

uploaded_file = st.file_uploader(
    "Choose your Clappia export file", 
    type=['xlsx', 'xls', 'csv'],
    help="Upload the Excel or CSV file downloaded from your Clappia submissions page"
)
if uploaded_file is not None:
    try:
        # Show file details
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.1f} KB",
            "File type": uploaded_file.type
        }
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Filename", uploaded_file.name)
        with col2:
            st.metric("Size", f"{uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.metric("Type", uploaded_file.name.split('.')[-1].upper())
        
        # Read the file
        with st.spinner("Reading file..."):
            if uploaded_file.name.endswith('.csv'):
                df_original = pd.read_csv(uploaded_file)
            else:
                df_original = pd.read_excel(uploaded_file)
        
        st.success(f"✅ File uploaded successfully!")
        st.success(f"📊 Data shape: **{df_original.shape[0]:,} rows** × **{df_original.shape[1]} columns**")
        
        # Store in session state
        st.session_state.df_original = df_original
        st.session_state.last_updated = datetime.now()
        st.session_state.data_source = "manual_upload"
        st.session_state.filename = uploaded_file.name
        
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        st.info("💡 Make sure the file is a valid Excel (.xlsx, .xls) or CSV (.csv) file from Clappia")



# Process data if available
if 'df_original' in st.session_state:
    df_original = st.session_state.df_original
    
    # Display last updated time
    if 'last_updated' in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🕒 **Last updated:** {st.session_state.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
        with col2:
            if 'filename' in st.session_state:
                st.info(f"📁 **Source file:** {st.session_state.filename}")
    
    # Display dataset information
    st.subheader("📋 Dataset Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", len(df_original))
    with col2:
        st.metric("Total Columns", len(df_original.columns))
    with col3:
        st.metric("Memory Usage", f"{df_original.memory_usage(deep=True).sum() / 1024:.1f} KB")
    
    # Show available columns
    with st.expander("📊 Available Columns"):
        st.write(df_original.columns.tolist())
    
    # Auto-detect QR code column
    qr_column = None
    possible_qr_columns = ["Scan QR code", "QR Code", "qr_code", "QR", "scan_qr", "qr_data"]
    
    for col in possible_qr_columns:
        if col in df_original.columns:
            qr_column = col
            break
    
    # If not found, look for columns containing QR-related text
    if qr_column is None:
        for col in df_original.columns:
            if any(qr_term in col.lower() for qr_term in ['qr', 'code', 'scan']):
                qr_column = col
                break
    
    if qr_column is None:
        st.warning("⚠️ QR code column not found automatically. Please select:")
        qr_column = st.selectbox("Select QR Code Column:", df_original.columns.tolist())
    else:
        st.success(f"✅ QR code column detected: **{qr_column}**")
    
    # Extract data from QR codes
    if qr_column:
        with st.spinner("Processing QR code data..."):
            # Create empty lists to store extracted data
            districts, chiefdoms, phu_names, community_names, school_names = [], [], [], [], []
            
            # Process each row in the QR code column
            for qr_text in df_original[qr_column]:
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
                if column != qr_column:
                    extracted_df[column] = df_original[column]
            
            st.session_state.extracted_df = extracted_df
    
    # Display processed data
    if 'extracted_df' in st.session_state:
        extracted_df = st.session_state.extracted_df
        
        # Show data preview
        st.subheader("📄 Processed Data Preview")
        st.dataframe(extracted_df.head(10))
        
        # Auto-detect ITN columns
        itn_received_col = None
        itn_given_col = None
        
        possible_received_cols = ["ITN received", "ITN_received", "itn_received", "Received", "received", "nets_received"]
        possible_given_cols = ["ITN given", "ITN_given", "itn_given", "Given", "given", "nets_given", "nets_distributed"]
        
        for col in possible_received_cols:
            if col in extracted_df.columns:
                itn_received_col = col
                break
        
        for col in possible_given_cols:
            if col in extracted_df.columns:
                itn_given_col = col
                break
        
        # Manual selection if not found
        if itn_received_col is None or itn_given_col is None:
            st.subheader("🔧 Column Configuration")
            col1, col2 = st.columns(2)
            with col1:
                itn_received_col = st.selectbox("ITN Received Column:", [col for col in extracted_df.columns if extracted_df[col].dtype in ['int64', 'float64']])
            with col2:
                itn_given_col = st.selectbox("ITN Given Column:", [col for col in extracted_df.columns if extracted_df[col].dtype in ['int64', 'float64']])
        
        # Analysis section
        if itn_received_col and itn_given_col:
            st.subheader("📊 Data Analysis")
            
            # Quick stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total ITN Received", f"{extracted_df[itn_received_col].sum():,}")
            with col2:
                st.metric("Total ITN Given", f"{extracted_df[itn_given_col].sum():,}")
            with col3:
                st.metric("Distribution Rate", f"{(extracted_df[itn_given_col].sum() / extracted_df[itn_received_col].sum() * 100):.1f}%")
            with col4:
                st.metric("Remaining ITNs", f"{(extracted_df[itn_received_col].sum() - extracted_df[itn_given_col].sum()):,}")
            
            # Analysis tabs
            tab1, tab2, tab3 = st.tabs(["📈 District Analysis", "🏘️ Chiefdom Analysis", "🔍 Detailed Filtering"])
            
            with tab1:
                # District Summary
                district_summary = extracted_df.groupby("District").agg({
                    itn_received_col: "sum",
                    itn_given_col: "sum"
                }).reset_index()
                district_summary["Difference"] = district_summary[itn_received_col] - district_summary[itn_given_col]
                district_summary["Distribution Rate %"] = (district_summary[itn_given_col] / district_summary[itn_received_col] * 100).round(1)
                
                st.dataframe(district_summary, use_container_width=True)
                
                # District chart
                fig, ax = plt.subplots(figsize=(12, 6))
                district_summary.plot(kind="bar", x="District", y=[itn_received_col, itn_given_col], ax=ax, color=["#1f77b4", "#ff7f0e"])
                ax.set_title("ITN Distribution by District")
                ax.set_xlabel("")
                ax.set_ylabel("Number of ITNs")
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
            
            with tab2:
                # Chiefdom Summary
                chiefdom_summary = extracted_df.groupby(["District", "Chiefdom"]).agg({
                    itn_received_col: "sum",
                    itn_given_col: "sum"
                }).reset_index()
                chiefdom_summary["Difference"] = chiefdom_summary[itn_received_col] - chiefdom_summary[itn_given_col]
                chiefdom_summary["Distribution Rate %"] = (chiefdom_summary[itn_given_col] / chiefdom_summary[itn_received_col] * 100).round(1)
                
                st.dataframe(chiefdom_summary, use_container_width=True)
                
                # Chiefdom chart
                chiefdom_summary['Label'] = chiefdom_summary['District'] + ' - ' + chiefdom_summary['Chiefdom']
                fig, ax = plt.subplots(figsize=(14, 8))
                chiefdom_summary.plot(kind="bar", x="Label", y=[itn_received_col, itn_given_col], ax=ax, color=["#1f77b4", "#ff7f0e"])
                ax.set_title("ITN Distribution by District and Chiefdom")
                ax.set_xlabel("")
                ax.set_ylabel("Number of ITNs")
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
            
            with tab3:
                # Detailed filtering
                st.subheader("🔍 Filter Data")
                
                # Sidebar filters
                with st.sidebar:
                    st.header("Data Filters")
                    
                    # District filter
                    districts = sorted(extracted_df['District'].dropna().unique())
                    selected_district = st.selectbox("Select District:", ['All'] + districts)
                    
                    # Chiefdom filter
                    if selected_district != 'All':
                        chiefdoms = sorted(extracted_df[extracted_df['District'] == selected_district]['Chiefdom'].dropna().unique())
                        selected_chiefdom = st.selectbox("Select Chiefdom:", ['All'] + chiefdoms)
                    else:
                        selected_chiefdom = 'All'
                    
                    # Apply filters
                    filtered_df = extracted_df.copy()
                    if selected_district != 'All':
                        filtered_df = filtered_df[filtered_df['District'] == selected_district]
                    if selected_chiefdom != 'All':
                        filtered_df = filtered_df[filtered_df['Chiefdom'] == selected_chiefdom]
                
                # Display filtered results
                st.write(f"**Filtered Results:** {len(filtered_df)} records")
                st.dataframe(filtered_df, use_container_width=True)
                
                # Filtered summary
                if len(filtered_df) > 0:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Filtered ITN Received", f"{filtered_df[itn_received_col].sum():,}")
                    with col2:
                        st.metric("Filtered ITN Given", f"{filtered_df[itn_given_col].sum():,}")
                    with col3:
                        st.metric("Filtered Distribution Rate", f"{(filtered_df[itn_given_col].sum() / filtered_df[itn_received_col].sum() * 100):.1f}%")
        
        # Export section
        st.subheader("💾 Export Data")
        col1, col2 = st.columns(2)
        
        with col1:
            csv = extracted_df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"clappia_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            from io import BytesIO
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                extracted_df.to_excel(writer, sheet_name='Processed Data', index=False)
                if 'district_summary' in locals():
                    district_summary.to_excel(writer, sheet_name='District Summary', index=False)
                if 'chiefdom_summary' in locals():
                    chiefdom_summary.to_excel(writer, sheet_name='Chiefdom Summary', index=False)
            
            st.download_button(
                label="📊 Download as Excel",
                data=buffer.getvalue(),
                file_name=f"clappia_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

else:
    st.info("👆 **Please upload your Clappia data file to begin analysis**")
    
    # Help section
    with st.expander("❓ Need Help?"):
        st.markdown("""
        **Step-by-Step Guide:**
        
        1. **Access your Clappia data:**
           - Open: `https://icf.clappia.com/app/GMB253374/submissions`
           - Login to your Clappia account
        
        2. **Download your data:**
           - Look for a **Download** or **Export** button (usually at the top)
           - Choose **Excel (.xlsx)** or **CSV (.csv)** format
           - Save the file to your computer
        
        3. **Upload to this app:**
           - Use the file uploader above
           - Select your downloaded file
           - Wait for processing to complete
        
        **Expected Data Format:**
        - The app will automatically detect QR code columns
        - It will extract: District, Chiefdom, PHU Name, Community Name, School Name
        - It will find ITN (received/given) columns for analysis
        
        **File Requirements:**
        - Supported formats: Excel (.xlsx, .xls) or CSV (.csv)
        - Maximum file size: ~200MB
        - Must contain QR code data from Clappia submissions
        """)
        
    # Add sample data info
    st.markdown("---")
    st.markdown("**🔗 Quick Access Links:**")
    st.markdown("- [Your Clappia Submissions](https://icf.clappia.com/app/GMB253374/submissions)")
    st.markdown("- [Clappia Help Center](https://www.clappia.com/help/)")
    
    # Show what the app can do
    with st.expander("📊 What this app will do with your data"):
        st.markdown("""
        **Data Processing:**
        - ✅ Extract location data from QR codes (District, Chiefdom, PHU, Community, School)
        - ✅ Auto-detect ITN (Insecticide Treated Nets) columns
        - ✅ Clean and structure the data for analysis
        
        **Analysis Features:**
        - 📈 **District Summary:** Total ITNs received/given by district
        - 🏘️ **Chiefdom Analysis:** Detailed breakdown by chiefdom
        - 🔍 **Interactive Filtering:** Filter by location hierarchy
        - 📊 **Visual Charts:** Bar charts showing distribution patterns
        - 💾 **Export Options:** Download processed data as Excel/CSV
        
        **Key Metrics:**
        - Total ITNs received vs given
        - Distribution rates by location
        - Remaining inventory tracking
        - Performance comparisons across regions
        """)
