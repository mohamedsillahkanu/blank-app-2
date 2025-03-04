import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Step 1: Generate Observed Data (True Distribution)
true_mean, true_std = 50, 10
observed_data = np.random.normal(true_mean, true_std, 1000)

# Sidebar: Model Calibration Parameters
st.sidebar.header("Adjust Model Parameters")
estimated_mean = st.sidebar.slider("Mean (μ)", 30, 70, 50)
estimated_std = st.sidebar.slider("Standard Deviation (σ)", 5, 20, 10)

# Step 2: Simulated Data using Adjustable Parameters
simulated_data = np.random.normal(estimated_mean, estimated_std, 1000)

# Plot Observed vs. Simulated Data
fig, ax = plt.subplots()
x = np.linspace(20, 80, 1000)
ax.plot(x, norm.pdf(x, true_mean, true_std), label="Observed Data (True)", color="blue")
ax.plot(x, norm.pdf(x, estimated_mean, estimated_std), label="Simulated Data (Model)", linestyle="dashed", color="red")
ax.legend()
ax.set_title("Model Calibration: Adjust Mean & Std Dev")

# Show the plot in Streamlit
st.pyplot(fig)
