import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
import requests

client_id = st.secrets["auth"]["client_id"]
client_secret = st.secrets["auth"]["client_secret"]

def login_callback():
    flow = InstalledAppFlow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": ["https://ksc-at-khec.streamlit.app"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]
    )
    credentials = flow.run_local_server(port=9000)
    st.session_state["credentials"] = credentials

if "credentials" not in st.session_state:
    st.button("Login with Google", type="primary", on_click=login_callback)
else:
    # Get user info
    resp = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        params={"alt": "json"},
        headers={"Authorization": f"Bearer {st.session_state['credentials'].token}"}
    )
    st.json(resp.json())

