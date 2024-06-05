import os.path

import streamlit_authenticator as stauth
import streamlit as st
# streamlit run C:\Users\c1049033\PycharmProjects\phd_apps\welcome.py

import yaml
from yaml.loader import SafeLoader


def my_authenticator():
    try:
        with open('other/usr.yml') as file:
            config = yaml.load(file, Loader=SafeLoader)
    except:
        with open(r'C:\Users\c1049033\PycharmProjects\phd_apps\other\usr.yml') as file:
            config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['pre-authorized']
    )
    authenticator.login(location='sidebar')

    if st.session_state["authentication_status"]:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')