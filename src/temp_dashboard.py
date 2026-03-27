import streamlit as st
import pandas as pd

# Load the CSV data
df = pd.read_csv('data/gold/final_barangay_schedule.csv')

# Dashboard
st.title('Temporary Dashboard: Final Barangay Schedule')

# Display the table
st.dataframe(df)