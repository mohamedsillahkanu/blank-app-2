import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# SEIR Model with Interventions
def seir_model(y, t, beta, sigma, gamma, c, delta):
    S, E, I, R = y
    dSdt = -beta * (1 - c) * S * I
    dEdt = beta * (1 - c) * S * I - sigma * E
    dIdt = sigma * E - (gamma + delta) * I
    dRdt = (gamma + delta) * I
    return [dSdt, dEdt, dIdt, dRdt]

# Streamlit UI
st.title("SEIR Malaria Transmission Model")
st.sidebar.header("Model Parameters")

# Parameter selection
beta = st.sidebar.slider("Transmission rate (β)", 0.0, 1.0, 0.3, 0.01)
sigma = st.sidebar.slider("Incubation rate (σ)", 0.0, 1.0, 0.2, 0.01)
gamma = st.sidebar.slider("Recovery rate (γ)", 0.0, 1.0, 0.1, 0.01)
c = st.sidebar.slider("Bed Net Effectiveness (c)", 0.0, 1.0, 0.0, 0.01)  # Default to 0 for baseline model
delta = st.sidebar.slider("Additional Recovery Rate (δ) due to Treatment", 0.0, 0.5, 0.0, 0.01)  # Default to 0 for baseline model

# Initial conditions
st.sidebar.header("Initial Conditions")
N = st.sidebar.number_input("Total Population (N)", min_value=1, value=1000)
S0 = st.sidebar.number_input("Initial Susceptible (S0)", min_value=0, value=N-1)
E0 = st.sidebar.number_input("Initial Exposed (E0)", min_value=0, value=0)
I0 = st.sidebar.number_input("Initial Infected (I0)", min_value=0, value=1)
R0 = st.sidebar.number_input("Initial Recovered (R0)", min_value=0, value=0)
y0 = [S0, E0, I0, R0]

# Time frame
t = np.linspace(0, 160, 160)

# Solve ODE
y = odeint(seir_model, y0, t, args=(beta, sigma, gamma, c, delta))
S, E, I, R = y.T

# Plot results
fig, ax = plt.subplots()
ax.plot(t, S, label="Susceptible", color='blue')
ax.plot(t, E, label="Exposed", color='orange')
ax.plot(t, I, label="Infectious", color='red')
ax.plot(t, R, label="Recovered", color='green')
ax.set_xlabel("Time (days)")
ax.set_ylabel("Population")
ax.set_title("SEIR Malaria Model (Baseline)")
ax.legend()
st.pyplot(fig)
