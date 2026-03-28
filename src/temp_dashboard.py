import streamlit as st
import pandas as pd

# Load the JSON data
df = pd.read_json('data/silver/stage_1_filtered/final_barangay_schedule.json')

# Dashboard
st.title('Temporary Dashboard: Final Barangay Schedule')

# Display the table
st.dataframe(df)