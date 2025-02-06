import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def generate_summary_stats(df, category_columns):
    summary_stats = {}
    for col in category_columns:
        total_outliers = (df[col] == 'Outlier').sum()
        total_non_outliers = (df[col] == 'Non-Outlier').sum()
        total = total_outliers + total_non_outliers
        summary_stats[col] = {
            'Total Outliers': total_outliers,
            'Total Non-Outliers': total_non_outliers,
            'Total Records': total,
            'Outlier Percentage': f"{(total_outliers/total)*100:.2f}%",
            'Non-Outlier Percentage': f"{(total_non_outliers/total)*100:.2f}%"
        }
    return pd.DataFrame(summary_stats).T

def generate_outlier_charts(df, column, chart_type):
    if 'year' not in df.columns:
        st.write("The dataset must contain a 'year' column for this analysis.")
        return
        
    grouped = df.groupby(['year', column]).size().unstack(fill_value=0)
    years = grouped.index.tolist()
    categories = grouped.columns.tolist()
    
    colors = {'Outlier': 'lightpink', 'Non-Outlier': '#47B5FF'}
    colors_list = [colors[cat] for cat in categories]
    
    if chart_type == "Bar Chart":
        fig = plt.figure(figsize=(15, 15))
        
        fig.suptitle("Outliers and Non-Outliers Bar Chart by Year after correction\n", fontsize=16, y=0.98)
        legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color) for color in colors_list]
        fig.legend(legend_elements, categories, 
                  loc='upper center', bbox_to_anchor=(0.5, 0.96),
                  ncol=len(categories), title="Categories")
        
        gs = fig.add_gridspec(3, 3, hspace=0.5, wspace=0.3)
        axes = [fig.add_subplot(gs[i//3, i%3]) for i in range(9)]
            
        for i, year in enumerate(years):
            if i < len(axes):
                ax = axes[i]
                year_data = grouped.loc[year]
                bars = ax.bar(categories, year_data, color=colors_list)
                ax.set_title(f"Year: {year}")
                ax.set_ylabel("Count", labelpad=10)
                ax.set_xlabel("Categories")
                ax.set_xticklabels(categories, rotation=0, ha='right')
                
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'{int(height)}', ha='center', va='bottom')
                           
        for j in range(len(years), len(axes)):
            fig.delaxes(axes[j])
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.90])
        
    elif chart_type == "Pie Chart":
        fig = plt.figure(figsize=(15, 15))
        
        fig.suptitle("Outliers and Non-Outliers Pie Chart by Year\n", fontsize=16, y=0.98)
        legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color) for color in colors_list]
        fig.legend(legend_elements, categories, 
                  loc='upper center', bbox_to_anchor=(0.5, 0.96),
                  ncol=len(categories), title="Categories")
        
        gs = fig.add_gridspec(3, 3, hspace=0.5, wspace=0.3)
        axes = [fig.add_subplot(gs[i//3, i%3]) for i in range(9)]
            
        for i, year in enumerate(years):
            if i < len(axes):
                ax = axes[i]
                year_data = grouped.loc[year]
                wedges, _, autotexts = ax.pie(year_data, colors=colors_list,
                                            autopct='%1.2f%%')
                ax.set_title(f"Year: {year}")
                
        for j in range(len(years), len(axes)):
            fig.delaxes(axes[j])
            
        plt.tight_layout(rect=[0, 0.03, 1, 0.90])
    
    st.pyplot(fig)

def main():
    st.title("Outlier Analysis with Charts by Year")
    uploaded_file = st.file_uploader("Upload your dataset (CSV/Excel):", type=["csv", "xlsx"])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            
            if not df.empty:
                category_columns = [col for col in df.columns 
                                  if 'winsorized_category' in col and 
                                  df[col].isin(['Outlier', 'Non-Outlier']).any()]
                
                analysis_type = st.radio("Select Analysis Type:", 
                                       ["Charts", "Summary Statistics"])
                
                if analysis_type == "Charts":
                    if category_columns:
                        selected_column = st.selectbox("Select column for analysis:", 
                                                     category_columns)
                        chart_type = st.radio("Select chart type:", 
                                            ["Bar Chart", "Pie Chart"])
                        generate_outlier_charts(df, selected_column, chart_type)
                    else:
                        st.write("No suitable category columns found.")
                else:
                    st.write("### Summary Statistics for All Variables")
                    summary_df = generate_summary_stats(df, category_columns)
                    st.dataframe(summary_df)
            else:
                st.write("Empty dataset.")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == '__main__':
    main()
