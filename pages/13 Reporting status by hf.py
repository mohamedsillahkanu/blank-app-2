import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

def generate_heatmaps(df, selected_variables):
    df['Status'] = df[selected_variables].sum(axis=1).apply(lambda x: 1 if x > 1 else 0).astype(int)
    
    custom_cmap = ListedColormap(['pink', 'lightblue'])
    adm1_groups = df['adm1'].unique()
    
    n_rows, n_cols = 4, 4
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 20))
    axes = axes.flatten()
    
    for i, adm1 in enumerate(adm1_groups):
        subset = df[df['adm1'] == adm1]
        
        hf_order = subset.groupby('hf_uid')['Status'].sum().sort_values(ascending=False).index
        subset['hf_uid'] = pd.Categorical(subset['hf_uid'], categories=hf_order, ordered=True)
        subset = subset.sort_values('hf_uid')
        
        heatmap_data = subset.pivot(index='hf_uid', columns='Date', values='Status')
        heatmap_data.fillna(0, inplace=True)
        
        sns.heatmap(
            heatmap_data,
            cmap=custom_cmap,
            linewidths=0,
            cbar=False,
            yticklabels=False,
            annot=False,
            ax=axes[i]
        )
        axes[i].set_title(f'{adm1}', fontsize=14)
        axes[i].set_xlabel('Date', fontsize=10)
        axes[i].tick_params(axis='x', labelrotation=90)
    
    for j in range(len(adm1_groups), len(axes)):
        axes[j].axis('off')
    
    legend_labels = ['Do not report', 'Report']
    legend_colors = [custom_cmap(0), custom_cmap(1)]
    legend_patches = [Patch(color=color, label=label) 
                     for color, label in zip(legend_colors, legend_labels)]
    
    fig.legend(
        handles=legend_patches,
        loc='upper center',
        bbox_to_anchor=(0.5, 0.95),
        ncol=2,
        title='Reporting status',
        fontsize=12,
        title_fontsize=14
    )
    
    plt.suptitle('Health Facility Reporting Status by ADM1', fontsize=18, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    return fig

def main():
    st.title("Health Facility Reporting Status Analysis")
    
    uploaded_file = st.file_uploader("Upload dataset:", type=["xlsx", "xls", "csv"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            selected_vars = st.multiselect("Select variables for analysis:", numeric_cols)
            
            if selected_vars:
                st.write("### Reporting Status Heatmap")
                fig = generate_heatmaps(df, selected_vars)
                st.pyplot(fig)
            else:
                st.warning("Please select variables for analysis.")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == '__main__':
    main()
