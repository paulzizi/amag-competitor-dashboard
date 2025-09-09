import streamlit as st
import pandas as pd
from datetime import datetime

# Minimale App zum Testen
st.set_page_config(page_title="AMAG Dashboard Test", page_icon="🚗")

st.title("🚗 AMAG Competitor Dashboard - Test")
st.write("Wenn Sie diesen Text sehen, funktioniert Streamlit!")

# Test-Daten
if st.button("Test-Daten laden"):
    test_data = {
        'Competitor': ['Emil Frey', 'Garage Weiss', 'Auto Kunz'],
        'Aktionen': [5, 3, 4],
        'Rabatt': ['15%', '10%', '12%']
    }
    df = pd.DataFrame(test_data)
    st.dataframe(df)
    st.success("✅ Test erfolgreich!")

st.info(f"Zeit: {datetime.now()}")

# Debug-Info
with st.expander("Debug-Information"):
    st.write("Python-Version:", st.__version__)
    st.write("Session State:", st.session_state)
