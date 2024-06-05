import streamlit as st
from utils import my_authenticator

my_authenticator()

if st.session_state["authentication_status"]:
    st.markdown('''# 🕵️ 🗃️  :rainbow[MK-2 Schizophrenia]: The former Cochrane Schizophrenia Group Study-based Register''')
    st.markdown("MK2 is available as a separate application [here](http://16.171.210.179:8501/): ")
