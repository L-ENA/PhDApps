import streamlit as st
from utils import my_authenticator

my_authenticator()

if st.session_state["authentication_status"]:

    st.markdown("# Lena's Horizon Scanning Tools")
    st.write("Select a tool from the navigation pane on the left side of the screen. ")
    # st.sidebar.markdown("## Navigate page ")
    #
    # st.sidebar.markdown('## [Welcome](#welcome)')
    # st.sidebar.markdown('## [What it is](#what-it-is)')